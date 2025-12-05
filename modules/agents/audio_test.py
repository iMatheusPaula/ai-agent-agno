from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.media import Audio
import requests

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
