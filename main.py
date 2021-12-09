import sqlite3

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import SlideTransition

import api_moviedb



class WrappedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x:
            self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class Menu(Screen):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

        conn = sqlite3.connect("films.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS films
                  (title text, id int UNIQUE, poster text,
                   backdrop text, release_date text, vote_average text)
               """)
        films = []

        c = api_moviedb.get_list_of_popular_films(api_moviedb.api_key)

        for film in c['results']:
            try:
                if film['backdrop_path'] is None:
                    continue
                films.append((
                    film['title'],
                    film['id'],
                    api_moviedb.base_image_url + f"{film['poster_path']}",
                    api_moviedb.base_image_url + f"{film['backdrop_path']}",
                    film['release_date'][:4],
                    film['vote_average']
                ))
            except KeyError:
                pass

        cursor.executemany(
            "INSERT OR IGNORE INTO films VALUES (?,?,?,?,?,?)", films)
        conn.commit()
        conn.close()

        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        height=Window.height * 2)
        box.bind(minimum_height=box.setter("height"))
        title = Label(text="List of popular films on themoviedb.org",
                      font_size=50, size_hint=(1, 0.04))
        box.add_widget(title)

        grid = GridLayout(cols=2, row_force_default=True,
                          row_default_height=190)

        for film in c['results']:
            try:
                if film['backdrop_path'] is None:
                    continue
                path = api_moviedb.base_image_url + f"{film['backdrop_path']}"
                img = AsyncImage(source=path, size_hint_x=None, width=350)
                if film['vote_average'] == 0:
                    film['vote_average'] = 'NR'
                else:
                    film['vote_average'] = f"{film['vote_average']} *"
                b = Button(text=f"{film['title']}, {film['release_date'][:4]}, {film['vote_average']}",
                        font_size=30,
                        id=str(film['id']),
                        background_color=(4, 1.0, 1.0, 0.5),
                        on_press=self.switch_to_film)
                grid.add_widget(img)
                grid.add_widget(b)
            except KeyError:
                pass

        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.do_scroll_x = False

        box.add_widget(grid)
        scrollview.add_widget(box)
        self.add_widget(scrollview)

    def switch_to_film(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = instance.id


class Film(Screen):
    def __init__(self, **kwargs):
        super(Film, self).__init__(**kwargs)

        film = api_moviedb.get_film_details(api_moviedb.api_key, int(self.name))

        layout = BoxLayout(orientation='vertical')
        grid = GridLayout(cols=2)
        overview_layout = BoxLayout(orientation='vertical')

        img = AsyncImage(source=api_moviedb.base_image_url +
                         film['poster_path'], size_hint=(1, 1), width=180)
        grid.add_widget(img)

        title = WrappedLabel(text=film['title'], size_hint=(1, 0.1))
        overview_layout.add_widget(title)

        if film['vote_average'] == 0:
            film['vote_average'] = 'NR'
        else:
            film['vote_average'] = f"{film['vote_average']} *"
        vote_average = WrappedLabel(
            text=film['vote_average'], size_hint=(1, 0.1))
        overview_layout.add_widget(vote_average)

        date_genre_string = [film['release_date'][:4]]
        for genre in film['genres']:
            date_genre_string.append(genre['name'])
        date_and_genres = WrappedLabel(text=', '.join(
            date_genre_string), size_hint=(1, 0.1))
        overview_layout.add_widget(date_and_genres)

        country_runtime_string = []
        for country in film['production_countries']:
            country_runtime_string.append(country['name'])
        country_runtime_string.append(
            f"{film['runtime'] // 60} h {film['runtime'] % 60} m")
        overview_layout.add_widget(WrappedLabel(
            text=', '.join(country_runtime_string), size_hint=(1, 0.1)))

        overview = WrappedLabel(text=film['overview'])
        overview_layout.add_widget(overview)

        # homepage = Label(text=c['homepage'])
        # overview_layout.add_widget(homepage)

        grid.add_widget(overview_layout)

        layout.add_widget(grid)

        b = Button(text='Return to menu',
                   background_color=(4, 1.0, 1.0, 0.5),
                   on_press=self.switch_to_menu,
                   size_hint=(1, 0.1))
        layout.add_widget(b)

        self.add_widget(layout)

    def switch_to_menu(self, *args):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'menu'


class AppScreenManager(ScreenManager):
    pass


class MovieDB(App):
    def build(self):
        root = AppScreenManager()
        root.add_widget(Menu(name='menu'))

        conn = sqlite3.connect("films.db")
        cursor = conn.cursor()

        sql = "SELECT id FROM films"
        cursor.execute(sql)

        for film in cursor.fetchall():
            root.add_widget(Film(name=str(film[0])))

        conn.close()
        return root


if __name__ == "__main__":
    MovieDB().run()
