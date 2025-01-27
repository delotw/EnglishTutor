from mistralai import Mistral


async def get_info_from_photo(photo_url: str):
    model = 'pixtral-12b-2409'
    api = 'wGkkpBYNqfIEermA9FfcodBC7DaX243X'
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
                    "image_url": photo_url
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

