import requests
import telebot
import urllib.parse as urlencoder
from bs4 import BeautifulSoup
from desctop_agents import get_header


class Reviews:
    def __init__(self, request):
        self.requestString = request
        self.name = ''
        self.link = ''

        self.urlSearch = 'https://www.metacritic.com/search/movie/#SEARCH#/results'
        self.urlDetailReviews = 'https://www.metacritic.com#NAME_LINK#/user-reviews'

        self.process_search()
        # self.get_reviews()

    def process_search(self):
        self.requestString = urlencoder.quote_plus(self.requestString)
        url_search = self.urlSearch.replace('#SEARCH#', self.requestString)

        result = requests.get(url_search, headers=get_header())  # отправляем HTTP запрос
        soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга

        search_results = soup.find('ul', {'class': 'search_results'})  # скорее всего вы ищете
        items = search_results.find_all('li')

        for item in items:
            title_block = item.find('h3', {'class': 'product_title'})
            title_link = title_block.find('a')

            if title_link is not None:
                self.name = title_link.text.lstrip().rstrip()  # удаляет лишние пробелы в начале и конце
                print(self.name)

                self.link = title_link.attrs['href']
                print(self.link)

            main_stats = item.find('div', {'class': 'main_stats'})
            date = main_stats.find('p')
            if date is not None:
                print(date.text.lstrip().rstrip())

            desc = item.find('p', {'class': ['deck', 'basic_stat']})
            if desc is not None:
                print(desc.text)

            print('          ')
            print('          ')

    def get_reviews(self):
        url_search_detail = self.urlDetailReviews.replace('#NAME_LINK#', self.link)
        result = requests.get(url_search_detail, headers=get_header())  # отправляем HTTP запрос
        soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга

        reviews_main_block = soup.find('div', {'class': 'reviews'})  # скорее всего вы ищете
        reviews = reviews_main_block.find_all('div', {'class': 'review'})  # Получаем все блоки с отзывами

        for comment in reviews:
            author_block = comment.find('span', {'class': 'author'})
            if author_block is not None:
                author_link = author_block.find('a')
                if author_link is not None:
                    print('author: ', author_link.text)
                else:
                    print('author: ', author_block.text)

                message_block = comment.find('span', {'class': 'blurb_expanded'})
                if message_block is not None:
                    print('text: ', message_block.text)
                    print('   ')
                else:
                    message_block = comment.find('div', {'class': 'review_body'})
                    message_block = message_block.find('span')
                    print('text: ', message_block.text)
                    print('                 -----------------------                       ')


#Test = Reviews('The godfather')
