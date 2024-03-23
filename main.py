from components import Main
from flet import *


def main(main_page: Page):
    main_page.window_top = 0
    main_page.window_left = 0
    main_page.window_maximized = True
    main_page.theme_mode = ThemeMode.LIGHT
    main_page.title = 'Formulário de Documento'
    main_page.window_title_bar_buttons_hidden = True
    main_page.add(Main(main_page))


if __name__ == '__main__':
    app(name='Document Form', target=main, view=FLET_APP)
