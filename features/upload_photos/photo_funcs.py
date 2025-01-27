import requests


def upload_to_telegraph(file_path):
    with open(file_path, "rb") as file:
        files = {"file": ("image.jpg", file)}
        response = requests.post("https://telegra.ph/upload", files=files)
    if response.ok:
        result = response.json()
        return f"https://telegra.ph{result[0]['src']}"  # Получаем ссылку
    return None


print(upload_to_telegraph('/Users/nick/Documents/Python/EnglishTutor/Wind7-Ult64-img0-SCALE3456x2160.png'))
