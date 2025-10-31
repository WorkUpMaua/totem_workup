import requests, os
from dotenv import load_dotenv

load_dotenv()

url_back = os.environ.get("BACK_URL")

class Presenter:

    @staticmethod
    def get_door_open_code(code: str) -> str:
        response = requests.get(url_back + f'/{code}/json')
        return response