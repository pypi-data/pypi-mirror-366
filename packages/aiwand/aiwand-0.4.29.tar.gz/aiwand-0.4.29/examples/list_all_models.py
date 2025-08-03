import aiwand
import pprint
from dotenv import load_dotenv
from aiwand import (
    GeminiModel,
    get_ai_client
)

def main():
    load_dotenv()
    client = get_ai_client()
    
    models = aiwand.list_models()
    for model in models:
        print(model.id)

    model_id = GeminiModel.GEMINI_2_0_FLASH_LITE.value
    model_data = client.models.retrieve(model_id)
    pprint.pp(model_data)

if __name__ == "__main__":
    main()