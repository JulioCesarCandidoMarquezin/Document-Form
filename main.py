from components import MainPage
from flet import *


def main(main_page: Page):
    # main_page.window_maximizable = False
    # main_page.window_resizable = False
    main_page.window_width = 640 + 60
    main_page.window_height = 800
    main_page.window_left = 0
    main_page.window_top = 0

    main_page.theme_mode = ThemeMode.LIGHT

    main_page.title = 'Word Form'
    main_page.add(MainPage(main_page))
    main_page.update()


if __name__ == '__main__':
    app(target=main, view=FLET_APP)
