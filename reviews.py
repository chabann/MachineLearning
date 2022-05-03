import requests
import urllib.parse as urlencoder
from bs4 import BeautifulSoup
from desctop_agents import get_header


class Reviews:
    def __init__(self, request):
        self.requestString = request

        self.urlSearch = 'https://www.metacritic.com/search/movie/#SEARCH#/results'
        self.urlDetailReviews = 'https://www.metacritic.com#NAME_LINK#/user-reviews'

    def process_search(self):
        self.requestString = urlencoder.quote_plus(self.requestString)
        url_search = self.urlSearch.replace('#SEARCH#', self.requestString)

        result = requests.get(url_search, headers=get_header())  # отправляем HTTP запрос
        soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга

        search_results = soup.find('ul', {'class': 'search_results'})  # скорее всего вы ищете

        if search_results is None:
            return []
        else:
            items = search_results.find_all('li')
            result_items = []

            for item in items:
                title_block = item.find('h3', {'class': 'product_title'})
                title_link = title_block.find('a')
                current_item = {}

                if title_link is not None:
                    name = title_link.text.lstrip().rstrip()  # удаляет лишние пробелы в начале и конце
                    link = title_link.attrs['href']

                    current_item['name'] = name
                    current_item['link'] = link

                main_stats = item.find('div', {'class': 'main_stats'})
                date = main_stats.find('p')
                if date is not None:
                    current_item['date'] = date.text.lstrip().rstrip()

                desc = item.find('p', {'class': ['deck', 'basic_stat']})
                if desc is not None:
                    current_item['description'] = desc.text

                result_items.append(current_item)

            return result_items

    def get_reviews(self, link):
        url_search_detail = self.urlDetailReviews.replace('#NAME_LINK#', link)
        result = requests.get(url_search_detail, headers=get_header())  # отправляем HTTP запрос
        soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга

        reviews_main_block = soup.find('div', {'class': 'reviews'})  # скорее всего вы ищете
        if reviews_main_block is None:
            return False

        reviews = reviews_main_block.find_all('div', {'class': 'review'})  # Получаем все блоки с отзывами

        return_reviews = []
        for comment in reviews:
            author_block = comment.find('span', {'class': 'author'})
            if author_block is not None:
                current_review = {}

                author_link = author_block.find('a')
                if author_link is not None:
                    print('author: ', author_link.text)
                    current_review['author'] = author_link.text
                else:
                    print('author: ', author_block.text)
                    current_review['author'] = author_block.text

                message_block = comment.find('span', {'class': 'blurb_expanded'})
                if message_block is not None:
                    current_review['text'] = message_block.text
                else:
                    message_block = comment.find('div', {'class': 'review_body'})
                    message_block = message_block.find('span')
                    current_review['text'] = message_block.text

                return_reviews.append(current_review)

        return return_reviews
