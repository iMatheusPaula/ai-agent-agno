from agno.agent import Agent
from agno.run.response import RunResponse
from agno.tools import tool
from agno.models.openai import OpenAIChat
from agno.storage.mongodb import MongoDbStorage
from base_conhecimento import cardapio
from agno.media import Audio
import requests
import os

STORAGE_URL = os.getenv("STORAGE_URL")
storage = MongoDbStorage(
    collection_name="agent_sessions",
    db_url=STORAGE_URL,
)


@tool()
def chamada_webhook(metodo_http: str, url_webhook: str, parametros, headers=None):
    print(f"Chamada de webhook com método {metodo_http} para a URL {url_webhook} com parâmetros: {parametros}")
    response = requests.request(
        method=metodo_http,
        url=url_webhook,
        json=parametros,
        headers=headers or {}
    )

    return response.content


def execute(message: str, session_id: str) -> RunResponse:
    agent_created = build_agent(session_id=session_id)

    return agent_created.run(message)


def build_agent(session_id: str) -> Agent:
    description = """
            Você é o Agente do "Açougue dos Amigos", um agente com comunicação simpática e paciente e informal.
            
            Sua finalidade é: atendimento ao cliente e vendas de itens do cardápio.
            
            USE UMA LINGUAGEM INFORMAL E DESCONTRAIDA COM POUCAS PALAVRAS COM SOTAQUE BEM NORDESTINO
            E AS VEZES USE A GIRIA "MEU PATRÃO".
            
            Comporte-se da seguinte forma: Seja acolhedor, proativo e objetivo. Sempre pergunte o que o cliente deseja 
            antes de responder. Use linguagem simples e próxima. Quando não souber algo, admita e sugira solução.
            Sempre de respostas curtas.
            NÃO MEÇA ESFORÇOS PARA BUSCAR INFORMAÇOES NA BASE DE CONHECIMENTO.
            
            Você oferece suporte para: clientes interessados nos pacotes de espetinhos e no serviço de entrega dentro da cidade.
            
            A Empresa se descreve como: O Açougue dos Amigos é um açougue local que vende pacotes de 
            espetinhos variados, com entrega rápida na cidade.
        """

    # description += """
    #         IMPORTANTE: Responda apenas com base nos documentos fornecidos na base de conhecimento.
    #         Se a resposta não estiver claramente presente nos documentos, diga:
    #         'Não encontrei essa informação.'
    #         Nunca adapte informações de um tema para outro, nem utilize conhecimento externo.
    #         SEMPRE cite o trecho exato do documento ao responder.
    #         """

    description += """
            IMPORTANTE: Caso o cliente peça algo fora do carpadio Não invente preço.
            Se for algo que possa vender em açougue fala que pode ser que tenha o item.
            Encaminha o cliente para o atendimento humano.
            """

    description += """
                TAXA DE ENTREGA NA CIDADE DE TRÊS LAGOAS TEM UM ACRÉSCIMO AO VALOR DO PEDIDO DE 7 Reais.
                IMPORTANTE: Abaixo é o cardapio de espetinhos.
                SEMPRE CONFIRME SE O CLIENTE ESTA PEDINDO UM PACOTE OU QUANTIDADE UNITÁRIA, CASO FOR UM PEDIDO COM QUANTIDADE 
                UNITARIA E A CONTA NÃO FECHE PACOTES LACRADOS INFORME.
                O VALOR DO CARDAPIO É O VALOR FECHADO DO PACOTE COM X QUANTIDADE DE UNIDADES.
                IMPORTANTE: AO REALIZAR O PEDIDO, O CLIENTE PODE MANDAR MENSAGENS PICADAS VOCÊ DEVE TER ATENÇÃO PARA 
                PEGAR TODOS OS ITENS DO PEDIDO.
                
                {
  "cardapio_espetinhos": [
    {
      "nome": "Carne",
      "preco": 40.00,
      "quantidade": 10,
      "unidade": "unidades"
    },
    {
      "nome": "Coração",
      "preco": 19.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Costela",
      "preco": 22.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Cupim na Bodinha",
      "preco": 25.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Cupim na Mostarda",
      "preco": 25.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Frango",
      "preco": 17.50,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Kafta",
      "preco": 17.50,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Linguiça Apimentada",
      "preco": 19.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Linguiça Cuiabana",
      "preco": 19.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Linguiça de Costela",
      "preco": 19.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Medalhão de Carne",
      "preco": 26.50,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Medalhão de Frango",
      "preco": 26.50,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Medalhão de Queijo",
      "preco": 35.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Panceta",
      "preco": 20.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Pão de Alho",
      "preco": 15.00,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Queijo Coalho",
      "preco": 35.00,
      "quantidade": 7,
      "unidade": "unidades"
    },
    {
      "nome": "Queijo Nozinho",
      "preco": 27.50,
      "quantidade": 5,
      "unidade": "unidades"
    },
    {
      "nome": "Tulipa de Frango",
      "preco": 17.50,
      "quantidade": 5,
      "unidade": "unidades"
    }
  ]
}
                """

    # description += """
    #         === INTENÇÕES ===
    #         Sempre que o usuário demostrar alguma das intenções abaixo, você deve chamar a tool/mcp mencionada na intenção.
    #
    #         == INTENÇÃO 1 : CONSULTAR IPVA ===
    #         Quando o usuário demonstrar intenção de emitir uma conta de IPVA ou fizer perguntas relacionadas a IPVA.
    #
    #         Devem ser solicitadas as seguintes informações de forma separada, para que não haja confusão no usuário:
    #         Placa: Placa do veiculo para emissão da certidão
    #
    #         você deve chamar a tool/mcp:
    #         chamada_webhook
    #
    #         Esses parametros devem ser enviados para a URL:
    #         https://webhook-test.com/7b78176fd710920851bfa20d05c11f34
    #
    #         Com o metodo http:
    #         POST
    #
    #         Com os seguintes headers:
    #         {
    #             "Authorization": "Bearer token123",
    #             "Content-Type": "application/json"
    #         }
    #
    #         A resposta da tool/mcp irá conter o seguinte formato:
    #         {}
    #
    #         Quando a tool/mpc:"chamada_webhook" responder avise o usuário que deu certo.
    #         """

    agent_params = {
        "name": "Atendimento do Açougue dos Amigos",
        "model": OpenAIChat(id="gpt-4o-mini"),
        "tools": [chamada_webhook],
        "session_id": session_id,
        "storage": storage,
        "add_history_to_messages": True,
        "num_history_runs": 20,
        "description": description,
        "markdown": True,
        "debug_mode": True
    }

    knowledge_params = {
        "knowledge": cardapio
    }
    agent_params.update(knowledge_params)

    agent_baiano = Agent(**agent_params)

    agent_baiano.knowledge.load(recreate=False)

    return agent_baiano


def audio_agent():
    agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        markdown=True,
    )

    url = "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/QA-01.mp3"

    response = requests.get(url)
    audio_content = response.content

    agent.print_response(
        "Give a transcript of this audio conversation. Use speaker A, speaker B to identify speakers.",
        audio=[Audio(content=audio_content)],
        stream=True,
    )
