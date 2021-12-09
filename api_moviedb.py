"""
Необходимо реализовать мини приложение для просмотра списка популярных фильмов,
используя https://www.themoviedb.org/documentation/api приложение должно содержать: 
- список популярных фильмов (дизайн произвольный) 
- экран с подробной информацией о фильме (дизайн произвольный). 
 Рекомендации:
- желательно использовать минимальное количество пакетов
- желательно использовать какой либо паттерн представления

Результатом выполненных работ должна быть ссылка на просмотр видео с записью экрана 
телефона или эмулятора с работой приложения, а также ссылка на просмотр исходных кодов.
"""


import requests


api_key = '8cb863e3ab720c55e546b4cf0948d16b'
base_image_url = 'http://image.tmdb.org/t/p/w342'


def get_list_of_popular_films(key):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={key}&language=en-US&page=1"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    return response


def get_film_details(key, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={key}&language=en-US"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    return response
