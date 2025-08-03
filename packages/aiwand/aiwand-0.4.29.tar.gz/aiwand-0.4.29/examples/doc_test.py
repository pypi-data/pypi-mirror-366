import aiwand
from openai import Client
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

import requests

load_dotenv()

def main():
    doc_links = [
        "https://ceodelhi.gov.in/OnlineERMS/PERMORMANCE/P8.pdf"
    ]

    messages = [
  {
    "role": "system",
    "content": "You are AIWand, a helpful AI assistant that provides clear, accurate, and concise responses.You excel at text processing, analysis, and generation tasks."
  },
  {
    "role": "user",
    "content": "total candidates number in list"
  },
  {
    "role": "user",
    "content": [
      {
        "type": "input_file",
        "file_url": "https://ceodelhi.gov.in/OnlineERMS/PERMORMANCE/P8.pdf"
      }
    ]
  }
]
    client = Client()
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
    )
    print(response.output_text)

    image_path = "https://goo.gle/instrument-img"
    image_bytes = requests.get(image_path).content
    image = types.Part.from_bytes(
      data=image_bytes, mime_type="image/jpeg"
    )

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=["What is this image?", image],
    )
    print(response.text)

    class Consistuency(BaseModel):
        name: str
        party: str
    class FullResponse(BaseModel):
        total_candidates: int
        consistuencies: list[Consistuency]

    response = client.responses.parse(
        model="gpt-4o",
        input=response.output_text,
        text_format=FullResponse
    )
    print(response.output_parsed)

    repsonse = aiwand.call_ai(
        user_prompt="total candidates number in list",
        document_links=doc_links,
        model="gpt-4o"
    )
    print(repsonse)

    response = aiwand.extract(
        document_links=doc_links,
        model="gpt-4o",
        response_format=FullResponse
    )
    print(response)

    pokedex_link = 'https://bella.amankumar.ai/examples/pokedex.pdf'
    response = aiwand.call_ai(
      document_links=[pokedex_link],
      user_prompt="which pokemon has highest speed? check correctly, share the page number and info about this pokemon",
      # debug=True,
      # model="gpt-4o"
    )
    print(response)


if __name__ == "main":
    main()