import requests
import urllib.parse as urlencoder
from bs4 import BeautifulSoup
from desctop_agents import get_header


class Reviews:
    def __init__(self, request):
        self.requestString = request

        self.urlSearch = 'https://www.metacritic.com/search/movie/#SEARCH#/results'
        self.urlDetailFilm = 'https://www.metacritic.com#FILM_NAME#'
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

    def get_reviews_info(self, link):
        return_reviews = []
        score = 0
        page = 0

        url_search_detail = self.urlDetailFilm.replace('#FILM_NAME#', link)
        result = requests.get(url_search_detail, headers=get_header())
        soup = BeautifulSoup(result.text, 'html.parser')
        review_block = soup.find_all('div', {'class': 'subsection_title'})

        if len(review_block) > 1:
            review_block = review_block[1].find('a')  # 0 - отзывы критиков, 1 - отзывы зрителей
        elif len(review_block) == 1:
            review_block = review_block[0].find('a')
        else:
            review_block = None

        if review_block is not None:
            link = review_block.attrs['href']

            url_search_detail = self.urlDetailReviews.replace('#NAME_LINK#', link)
            url_search_detail_page = url_search_detail + '?page=' + str(page)

            result = requests.get(url_search_detail_page, headers=get_header())  # отправляем HTTP запрос
            soup = BeautifulSoup(result.text, 'html.parser')  # Отправляем полученную страницу в библиотеку для парсинга

            main_info = soup.find('table', {'class': 'simple_summary'})
            score = main_info.find('span', {'class': 'metascore_w'})
            if score is not None:
                score = score.text

            reviews_main_block = soup.find('div', {'class': 'reviews'})

            while reviews_main_block is not None:  # листаем пагинацию, пока есть отзывы
                # Получаем все блоки с отзывами для текущей страницы
                reviews = reviews_main_block.find_all('div', {'class': 'review'})

                for comment in reviews:
                    author_block = comment.find('span', {'class': 'author'})
                    if author_block is not None:
                        current_review = {}

                        author_link = author_block.find('a')
                        if author_link is not None:
                            current_review['author'] = author_link.text
                        else:
                            current_review['author'] = author_block.text

                        score_block = comment.find('span', {'class': 'metascore_w'})
                        if score_block is not None:
                            current_review['score'] = score_block.text
                        else:
                            score_block = comment.find('div', {'class': 'metascore_w'})
                            if score_block is not None:
                                current_review['score'] = score_block.text
                            else:
                                current_review['score'] = 0

                        message_block = comment.find('span', {'class': 'blurb_expanded'})
                        if message_block is not None:
                            current_review['text'] = message_block.text
                        else:
                            message_block = comment.find('div', {'class': 'review_body'})
                            message_block = message_block.find('span')
                            current_review['text'] = message_block.text

                        return_reviews.append(current_review)

                page += 1
                url_search_detail_page = url_search_detail + '?page=' + str(page)

                result = requests.get(url_search_detail_page, headers=get_header())
                soup = BeautifulSoup(result.text, 'html.parser')
                reviews_main_block = soup.find('div', {'class': 'reviews'})

        return {'arReviews': return_reviews, 'averageScore': score}
