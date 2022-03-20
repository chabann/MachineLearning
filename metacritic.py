import requests
import json
from bs4 import BeautifulSoup
from desctop_agents import get_header


url_search = 'https://www.metacritic.com/search/all/the%20godfather/results'
url_search_detail = 'https://www.metacritic.com/movie/the-godfather/user-reviews'

result = requests.get(url_search_detail, headers=get_header())  # отправляем HTTP запрос
soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга
reviewsMainBlock = soup.find('div', {'class': 'reviews'})  # скорее всего вы ищете
reviews = reviewsMainBlock.find_all('div', {'class': 'review'})  # Получаем все блоки с отзывами

for comment in reviews:
    authorBlock = comment.find('span', {'class': 'author'})
    if authorBlock is not None:
        authorLink = authorBlock.find('a')
        if authorLink is not None:
            print('author: ', authorLink.text)
        else:
            print('author: ', authorBlock.text)

        messBlock = comment.find('span', {'class': 'blurb_expanded'})
        if messBlock is not None:
            print('text: ', messBlock.text)
            print('   ')
        else:
            messBlock = comment.find('div', {'class': 'review_body'})
            messBlock = messBlock.find('span')
            print('text: ', messBlock.text)
            print('                 -----------------------                       ')

