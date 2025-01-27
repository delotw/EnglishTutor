from mistralai import Mistral
import base64

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # 
        print(f"Error: {e}")
        return None


async def get_info_from_photo(photo_path: str):
    model = 'pixtral-12b-2409'
    api = 'wGkkpBYNqfIEermA9FfcodBC7DaX243X'
    base64_image = encode_image(image_path=photo_path)
    client = Mistral(api_key=api)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, you need to display all the information that will be on the next photo in English, without losing the semantic part of the infographic. Make it look like you have to replace the infographics with text, but don't add anything of yourself at the end and start of asnwer. Your answer should contain ONLY information from the infographic."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]
    chat_response = await client.chat.complete_async(
        model=model,
        messages=messages
    )
    answer = chat_response.choices[0].message.content # type: ignore
    return answer

