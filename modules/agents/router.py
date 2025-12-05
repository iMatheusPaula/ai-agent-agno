from fastapi import APIRouter, Body
from modules.agents.service import execute
from modules.agents.schemas import UseAgentRequest
import requests
import base64
import hashlib
import hmac
import os
import time
from typing import Tuple
from Crypto.Cipher import AES

WHATSAPP_MEDIA_DIR = os.getenv("WHATSAPP_MEDIA_DIR", "/tmp")

agents_router = APIRouter()


def _parse_number_from_jid(jid: str) -> str:
    """
    Converte '5517996097839@s.whatsapp.net' para o formato esperado pela API ('17996097839').
    Regras:
    - Remove o sufixo '@...'
    - Remove o prefixo do país '55' se existir
    """
    if not isinstance(jid, str):
        return ""
    local = jid.split("@", 1)[0]
    return local if local.startswith("55") else f"55{local}"


def send_whatsapp_text(number: str, text: str) -> dict:
    url = "http://bot-code-chat-1:8084/message/sendText/codechat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpbnN0YW5jZU5hbWUiOiJjb2RlY2hhdCIsImFwaU5hbWUiOiJ3aGF0c2FwcC1hcGkiLCJ0b2tlbklkIjoiMDFLMjVYOTNBUVlYMFZSRkZLVlcxSDhaUVgiLCJpYXQiOjE3NTQ2OTI2MTksImV4cCI6MTc1NDY5MjYxOSwic3ViIjoiZy10In0.yrfuOxvqibDFi-eXoQ6USkZckfFTeF4rSqQgl2tfbms"
    }
    payload = {
        "number": number,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": text
        }
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    try:
        return {"status_code": resp.status_code, "data": resp.json()}
    except Exception:
        return {"status_code": resp.status_code, "data": resp.text}


# ======= UTILITÁRIOS PARA MÍDIA WHATSAPP =======

def _hkdf(media_key: bytes, length: int, info: bytes) -> bytes:
    """
    HKDF-SHA256 como usado pelo WhatsApp. Salt nulo (32 bytes zero).
    Gera 'length' bytes.
    """
    salt = b"\x00" * 32
    prk = hmac.new(salt, media_key, hashlib.sha256).digest()
    okm = b""
    t = b""
    counter = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:length]


def _derive_keys_for_audio(media_key_b64: str) -> Tuple[bytes, bytes, bytes]:
    """
    Para audioMessage, o 'info' é b"WhatsApp Audio Keys".
    Retorna (iv, cipher_key, mac_key)
    """
    media_key = base64.b64decode(media_key_b64)
    info = b"WhatsApp Audio Keys"
    # WhatsApp usa 80 bytes de material: 16 iv + 32 cipherKey + 32 macKey
    key_material = _hkdf(media_key, 80, info)
    iv = key_material[:16]
    cipher_key = key_material[16:48]
    mac_key = key_material[48:80]
    return iv, cipher_key, mac_key


def _verify_and_decrypt(enc_bytes: bytes, iv: bytes, cipher_key: bytes, mac_key: bytes) -> bytes:
    """
    Valida o MAC (últimos 10 bytes) e descriptografa (AES-CBC).
    """
    if len(enc_bytes) <= 10:
        raise ValueError("Arquivo muito curto para conter MAC")

    mac_from_file = enc_bytes[-10:]
    cipher_payload = enc_bytes[:-10]

    # MAC é HMAC-SHA256(iv + cipher_payload), comparar os 10 primeiros bytes
    mac_calc_full = hmac.new(mac_key, iv + cipher_payload, hashlib.sha256).digest()
    if mac_from_file != mac_calc_full[:10]:
        raise ValueError("MAC inválido: conteúdo corrompido ou chave errada")

    cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_payload)

    # Remover PKCS7
    pad = decrypted[-1]
    if pad < 1 or pad > 16:
        raise ValueError("Padding inválido")
    return decrypted[:-pad]


def download_and_decrypt_whatsapp_audio(content: dict, save_dir: str = "/medias") -> str:
    """
    Baixa o .enc do WhatsApp e retorna o caminho do arquivo .ogg descriptografado.
    'content' é o dict que veio no webhook (em content).
    """
    url = content.get("url") or ""
    if not url:
        raise ValueError("URL ausente no conteúdo")

    # Alguns webhooks trazem '&amp;' no lugar de '&'
    url = url.replace("&amp;", "&")

    media_key_b64 = content.get("mediaKey")
    if not media_key_b64:
        raise ValueError("mediaKey ausente no conteúdo")

    # Deriva chaves
    iv, cipher_key, mac_key = _derive_keys_for_audio(media_key_b64)

    # Baixa arquivo criptografado
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    enc_bytes = resp.content

    # Descriptografa
    decrypted = _verify_and_decrypt(enc_bytes, iv, cipher_key, mac_key)

    # Decide extensão pelo mimetype (esperado: audio/ogg; codecs=opus)
    mimetype = (content.get("mimetype") or "").lower()
    ext = ".ogg" if "ogg" in mimetype or "opus" in mimetype else ".aud"

    # Gera nome de arquivo
    base = "wa-audio"
    file_sha_b64 = content.get("fileSha256") or ""
    if file_sha_b64:
        try:
            base = base + "-" + base64.b64decode(file_sha_b64)[:6].hex()
        except Exception:
            pass
    ts = int(time.time())
    filename = f"{base}-{ts}{ext}"

    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, filename)
    with open(path, "wb") as f:
        f.write(decrypted)

    return path


# Endpoint para usar o agente
@agents_router.post("/use", response_model=dict)
async def use_agent(request: UseAgentRequest):
    response = execute(
        message=request.message,
        session_id=request.session_id
    )

    return response.to_dict()


@agents_router.post("/webhook", response_model=dict)
async def webhook_handler(payload: dict = Body(...)):
    event = payload.get("event")

    if event != "messages.upsert":
        return {"message": "evento não suportado"}

    data = payload.get("data") or {}
    key_from_me = data.get("keyFromMe")
    if key_from_me:
        return {"message": "mensagem do próprio agente."}

    session_id = data.get("keyRemoteJid")
    message_type = data.get("messageType")
    content = data.get("content") or {}
    text = content.get("text")

    if not session_id:
        return {"message": "keyRemoteJid ausente"}

    if message_type == "extendedTextMessage" or isinstance(text, str) and text.strip():
        response = execute(message=text.strip(), session_id=session_id)

        number_to_send = _parse_number_from_jid(session_id)

        send_result = send_whatsapp_text(number=number_to_send, text=response.content)

        print(send_result)
        return {"message": response.content}

    if message_type == "audioMessage":
        try:
            saved_path = download_and_decrypt_whatsapp_audio(content)
            number_to_send = _parse_number_from_jid(session_id)
            confirmation = f"Áudio recebido e salvo: {saved_path}"
            send_result = send_whatsapp_text(number=number_to_send, text=confirmation)
            print(send_result)
            return {"message": confirmation, "path": saved_path}
        except Exception as e:
            return {"message": f"Falha ao processar áudio: {e}"}

    return {"message": "messageType ou conteúdo não suportado"}
