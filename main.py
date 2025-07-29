import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Загружаем переменные из .env
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

BASE_URL = "http://185.244.219.162/phpmyadmin/"
LOGIN_URL = BASE_URL + "index.php"

session = requests.Session()

# Получаем токен
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")
token_tag = soup.find("input", {"name": "token"})
token = token_tag["value"] if token_tag else None

login_data = {
    "pma_username": USERNAME,
    "pma_password": PASSWORD,
    "server": "1",
    "target": "index.php",
    "token": token,
    "set_session": ""
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": LOGIN_URL,
    "Content-Type": "application/x-www-form-urlencoded"
}

response = session.post(LOGIN_URL, data=login_data, headers=headers)

if "route=/logout" in response.text:
    print("успешный вход в phpmyadmin\n")
else:
    print("ошибка авторизации\n")
    exit()

#запрос к таблице users http://185.244.219.162/phpmyadmin/index.php?route=/sql&server=1&db=testDB&table=users&pos=0
users_url = BASE_URL + "index.php?route=/sql&server=1&db=testDB&table=users&pos=0"
users_response = session.get(users_url)

if users_response.status_code != 200:
    print("ошибка получении данных таблицы users\n")
    exit()

soup = BeautifulSoup(users_response.text, "html.parser")
table = soup.find("table", {"class": "data"})

if not table:
    print("таблицы users не найдена\n")
    exit()

headers = []
for th in table.find_all("th"):
    small = th.find("small")
    if small:
        small.decompose()
    headers.append(th.get_text(strip=True))
    
rows = []
for tr in table.find_all("tr")[1:]:
    tds = tr.find_all("td")
    data_cells = [td.get_text(strip=True) for td in tds[4:]]
    if data_cells:
        rows.append(data_cells)

headers = [h for h in headers if h.strip() != ""]
print("содержимое таблицы users:")

# print(headers) # первый пустой элемент 
print(*headers, sep='\t|')
for row in rows:
    print(*row, sep='\t|')
     
exit()
