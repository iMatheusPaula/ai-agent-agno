# Chatbot Para Atendimento ao Público com IA

O que é?
O projeto Chatbot Para Atendimento ao Público com IA é uma iniciativa que visa democratizar o acesso a
ferramentas de atendimento ao cliente para pequenos negócios e empreendedores que não possuem
recursos para investir em soluções complexas e caras.

O sistema consiste em um Agente de Inteligência Artificial,
proporcionando atendimento automatizado, com IA capaz de se comunicar com clientes via Whatsapp,
seguindo uma base de conhecimento pré-estabelecida.

O protótipo foi desenvolvido para testes, inicialmente para um estabelecimento específico, com o objetivo
de estruturar pedidos, com base no cardápio (o qual apresenta
valores e quantidades pré-estabelecidas para cada item).

* Os principais objetivos com esse projeto são capacitar microempreendedores no uso da ferramenta, reduzir tempo médio
  de atendimento e erros operacionais.

## Atendimento ao cliente

De acordo com o SEBRAE, "Um atendimento de qualidade é estar lá quando o cliente precisa,
de forma ágil e eficiente."
Um bom atendimento ao cliente traz beneícios como: Reputação positiva,
Redução de custos, Aumento da receita, Fidelização de clientes, Recomendações.
Para isso foi desenvolvido um chatbot que responde automaticamente as mensagens do cliente.

## Tecnologias utilizadas:

| Categoria            | Tecnologias                 |
|----------------------|-----------------------------|
| Backend              | Python, FastAPI             |
| Framework de Agentes | **Agno**                    |
| IA                   | OpenAI API                  |
| Integração WhatsApp  | CodeChat / Baileys          |
| Bancos               | MongoDB, PostgreSQL         |
| ORM                  | SQLAlchemy                  |
| Containerização      | Docker + docker-compose     |
| Infraestrutura       | Variáveis ambiente (dotenv) |

## Como executar:

Faça o clone do projeto:

`git clone 
https://github.com/iMatheusPaula/ai-agent-agno.git
`

Entre na pasta do projeto:
``cd ai-agent-agno``

Tendo o docker instalado e iniciado, executar o seguinte comando dentro da pasta
do projeto:
``docker compose up -d``

Será criada uma conexão via API CodeChat com o Whatsapp do estabelecimento.
PAra isso, leia o QR CODE com o whatsapp que será integrado ao Chatbot, e pronto.
Todas as mensagens recebidas por esse canal, serão respondidas automaticamente,
com base no cardápio (base de conhecimento).

