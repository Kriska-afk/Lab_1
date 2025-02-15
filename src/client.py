import requests
from requests.auth import HTTPBasicAuth
import time
import configparser


config = configparser.ConfigParser()
config.read("config.ini")


HOST = config["Client-server_app"]["host"]
PORT = int(config["Client-server_app"]["port"])
BASE_URL = f"http://{HOST}:{PORT}"
USERNAME = config["Client-server_app"]["username"]
PASSWORD = config["Client-server_app"]["password"]


class Cache:
    cache = {}

    @classmethod
    def set_cache_data(cls, endpoint, response):
        """Добавить данные в кэш"""
        cache_control = response.headers.get('Cache-Control')
        max_age = cls.__parse_cache_control(cache_control)
        cls.cache[endpoint] = (response.json(), time.time() + max_age)

    @classmethod
    def get_cached_data(cls, endpoint):
        """Достать данные из кэша"""
        if endpoint in cls.cache:
            if time.time() < cls.cache[endpoint][1]:
                return cls.cache[endpoint]
            else:
                del cls.cache[endpoint]
        return None

    @staticmethod
    def __parse_cache_control(cache_control):
        """Распарсить заголовок Cache-Control"""
        directives = cache_control.split(',')
        for directive in directives:
            directive = directive.strip()
            if directive.startswith('max-age='):
                try:
                    return int(directive.split('=')[1])
                except ValueError:
                    pass
        return None


def make_request(method, endpoint, data=None):
    """Основная функция отправка запроса"""
    url = f"{BASE_URL}{endpoint}"

    if method.upper() == 'GET':
        cached_data = Cache.get_cached_data(endpoint=endpoint)
        if cached_data:
            print("Используем кэшированные данные.")
            print(f"Response Code: 200")
            print(f"Response Body: {cached_data}")
            return

        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            Cache.set_cache_data(endpoint=endpoint, response=response)
            print(f"Response Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        else:
            print(f"Error: {response.status_code}  {response.reason}")

    elif method.upper() == 'POST':
        response = requests.post(url, json=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            print(f"Response Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        else:
            print(f"Error: {response.status_code}  {response.reason}")

    elif method.upper() == 'PUT':
        response = requests.put(url, json=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            print(f"Response Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        else:
            print(f"Error: {response.status_code}  {response.reason}")

    elif method.upper() == 'DELETE':
        response = requests.delete(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            print(f"Response Code: {response.status_code}")
            print(f"Response Body: {response.json()}")
        else:
            print(f"Error: {response.status_code} {response.reason}")


if __name__ == "__main__":
    while True:
        method = input("Введите метод (GET, POST, PUT, DELETE) или 'exit' для выхода: ").strip()
        if method.lower() == 'exit':
            break
        url = input("Введите URL: ").strip()

        data = None
        if method.upper() in ['POST', 'PUT']:
            data_input = input("Введите данные в формате JSON (или оставьте пустым для пустого тела): ")
            if data_input:
                try:
                    data = eval(data_input)
                except Exception as e:
                    print(f"Ошибка при разборе данных: {e}")
                    continue

        make_request(method=method, endpoint=url, data=data)
