import aiwand
import pprint
from pydantic import BaseModel
from dotenv import load_dotenv

def main():
    load_dotenv()
    links = [
        "https://bella.amankumar.ai/examples/receipt_1.jpeg"
    ]
    data = aiwand.call_ai(
        system_prompt="You are a helpful assistant that can extract text from images.",
        user_prompt="Extract the whole text from the image.",
        images=links,
        debug=True,
        model='gpt-4o'
    )
    print(data)

    data2 = aiwand.extract(
        images=links
    )
    pprint.pp(data2)

    class ReceiptItem(BaseModel):
        name: str
        quantity: str
        rate: str
        total: str
    class FullResponse(BaseModel):
        total: str
        store_name: str
        items: list[ReceiptItem]
    data3 = aiwand.extract(
        images=links,
        response_format=FullResponse
    )        
    pprint.pp(data3)

    return data

if __name__ == "main":
    main()