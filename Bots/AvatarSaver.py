import requests
from bs4 import BeautifulSoup
from TelegramSender import sending_to_tg

# URL для POST-запроса
url = "https://ttsave.app/en/profile"

# Заголовки запроса
headers = {
    "Content-Type": "application/json",
    "X-Xsrf-Token": "eyJpdiI6IlhTNTNjNlhhRTQrVGh4WmcyenZDanc9PSIsInZhbHVlIjoiVW1BMk5xSXFSM2ZOMTV4K3cxVEs1WjlsVm1jT1EvcmF4cVk4SDBiUUZsSUQ1S1Nxd1JsaFBtWHdycXk0VElJYTd5Smtzc3hENnppWENyYmhDOVJJbXVwempyZ1F1QlJtV2VBOUVIb0dwem40RWpEeEZTNEtVTXZLOXd6T2RXTEgiLCJtYWMiOiJhMzA1ZmY3YjliZjE1ZDQzNWRkZmQ1ZTA5MzY5MjRjNjRhOWFmMDdhYWU0YjQ3MGI4OTc4YTVlYTFkNmM4NjRjIiwidGFnIjoiIn0=",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru,en;q=0.9"
}


async def save_avatar(id): 
    # Данные для отправки (с вашими параметрами)
    data = {
        "query": id,
        "language_id": "1"
    }

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)

    # Проверка ответа
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        download_button = soup.find('a', class_='w-full text-white font-bold rounded-xl border flex flow-row items-center justify-center py-2 px-3 bg-blue-500 hover:bg-purple-500 mt-5')
        if download_button:
            download_link = download_button['href']
            return download_link
        else:
            await sending_to_tg(text="❗️Ошибка скачивания аватара❗️")
    else:
        await sending_to_tg(text="❗️Ошибка скачивания аватара❗️")
