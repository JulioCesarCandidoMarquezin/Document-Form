from typing import List, Tuple, Callable
from document_manager import DocumentManager
from flet import *


class PageForm(UserControl):
    def __init__(self, paragraphs: List):
        super().__init__()
        self.layout = ListView(expand=True, spacing=10)
        self.paragraphs = paragraphs
        self.fields = []

    def build(self) -> ListView:
        self.setup_rows()
        return self.layout

    def setup_rows(self) -> None:
        for paragraph, align in self.paragraphs:
            content = Container(
                content=Row(
                    wrap=True,
                    alignment=align
                ),
                shadow=BoxShadow(
                    spread_radius=1,
                    blur_radius=2,
                    color=colors.BLUE_GREY_300,
                    offset=Offset(0, 0),
                    blur_style=ShadowBlurStyle.OUTER,
                )
            )
            
            for text in paragraph:
                if '@TF' in text:
                    control = TextField(
                        value=text.replace('@TF', ''),
                        width=200,
                        height=30,
                        content_padding=Padding(left=5, top=3, right=5, bottom=3),
                        data={'type': '@TF'},
                    )
                    content.content.controls.append(control)
                    self.fields.append(control)
                elif '@CB' in text:
                    control = Checkbox(value='x' in text.lower(), data={'type': '@CB'})
                    content.content.controls.append(control)
                    self.fields.append(control)
                else:
                    content.content.controls.append(Text(value=text, selectable=True))
                    
            self.layout.controls.append(content)

    def get_fields_values(self) -> List[Tuple]:
        values = []
        for field in self.fields:
            if isinstance(field, TextField):
                value = field.value or '__________'
            elif isinstance(field, Checkbox):
                value = '( X )' if field.value else '(  )'
            else:
                value = ''

            values.append((value, field.data['type']))

        return values

    def clear_values(self) -> None:
        for field in self.fields:
            field.value = None
        self.update()


def Main(root: Page) -> Control:
    dm: DocumentManager = DocumentManager()
    root_dialog: AlertDialog = AlertDialog()
    root_file_picker: FilePicker = FilePicker()
    load: ProgressRing = ProgressRing(visible=False, disabled=True)
    viewer: ListView = ListView()
    menu: GridView = GridView()

    root.add(root_dialog)
    root.window_prevent_close = True
    root.on_window_event = lambda e: on_window_event(e)

    def build() -> Control:
        nonlocal viewer, menu, root_file_picker, load
        viewer = setup_viewer()
        menu = setup_menu()

        return Row(
            controls=[
                viewer,
                menu,
                root_file_picker,
                load,
            ],
            expand=True,
            adaptive=True,
            alignment=MainAxisAlignment.CENTER,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )

    def setup_viewer() -> ListView:
        return ListView(expand=True, spacing=10)

    def setup_menu() -> GridView:
        return GridView(
            controls=[
                IconButton(icon=icons.FILE_UPLOAD, on_click=open_file, icon_color=colors.YELLOW_ACCENT_700, tooltip='Carregar arquivo'),
                IconButton(icon=icons.SAVE_ROUNDED, on_click=save_word, icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar Word'),
                IconButton(icon=icons.PICTURE_AS_PDF, on_click=save_pdf, icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar PDF'),
                IconButton(icon=icons.PHOTO_LIBRARY, on_click=save_images, icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar Imagens'),
                IconButton(icon=icons.SUNNY, on_click=change_theme, icon_color=colors.YELLOW_ACCENT_700, tooltip='Mudar Tema'),
                IconButton(icon=icons.DELETE, on_click=clear_form, icon_color=colors.YELLOW_ACCENT_700, tooltip='Apagar Campos'),
            ],
            spacing=10,
            width=50
        )

    def on_window_event(e: ControlEvent) -> None:
        if e.data == 'close':
            try:
                dm.clear()
            finally:
                root.window_destroy()

    def on_error(title: str = '', msg: str = '', error: Exception | None = None) -> None:
        def on_more_click(_) -> None:
            content.controls.append(msg_error)
            btn.icon = icons.REMOVE
            btn.on_click = on_minus_click
            content.update()

        def on_minus_click(_) -> None:
            content.controls.remove(msg_error)
            btn.icon = icons.ADD
            btn.on_click = on_more_click
            content.update()

        title = Text(value=title if title else 'Ocorreu um erro')
        msg = Text(value=msg)
        msg_error = Text(value=f'Se preciso, informe o erro "{error}" para o desenvolvedor.', selectable=True)
        btn = IconButton(icon=icons.ADD, on_click=on_more_click)
        content = Row(controls=[msg, msg_error, btn], wrap=True)
        show_dialog(title=title, content=content)

    def loading_start() -> None:
        viewer.disabled = True
        viewer.visible = False

        menu.disabled = True
        menu.visible = False

        load.disabled = False
        load.visible = True

        root.update()

    def loading_end() -> None:
        viewer.disabled = False
        viewer.visible = True

        menu.disabled = False
        menu.visible = True

        load.disabled = True
        load.visible = False

        root.update()

    def change_theme(e: ControlEvent) -> None:
        button_control: IconButton = e.control

        page_theme = root.theme_mode

        if page_theme is ThemeMode.DARK:
            button_control.icon = icons.SUNNY
            root.theme_mode = ThemeMode.LIGHT
        else:
            button_control.icon = icons.NIGHTLIGHT
            root.theme_mode = ThemeMode.DARK

        button_control.update()
        root.update()

    def close_dialog() -> None:
        root_dialog.open = False
        root_dialog.title.clean()
        root_dialog.content.clean()
        root_dialog.actions.clear()
        root_dialog.update()

    def show_dialog(title: str | Control | None = None, content: str | Control | None = None, actions: List[Control] | None = None) -> None:
        if isinstance(title, str):
            title = Text(value=title)

        if isinstance(content, str):
            content = Text(value=content)

        root_dialog.title = title
        root_dialog.content = content
        root_dialog.actions = actions
        root_dialog.elevation = 10
        root_dialog.actions_alignment = MainAxisAlignment.END

        root_dialog.open = True
        root.update()

    def show_dialog_saved_file(saved: bool, output_path: str = '', output_folder: str = '') -> None:
        if saved:
            actions = []

            if output_path:
                actions.append(TextButton(
                    text='Abrir arquivo',
                    on_click=lambda _: dm.open_path(path=output_path)
                ))

            if output_folder:
                actions.append(TextButton(
                    text='Abrir pasta',
                    on_click=lambda _: dm.open_path(path=output_folder)
                ))

            show_dialog(
                title="Documento salvo",
                content="Deseja abrir no Explorer o(a) arquivo/pasta onde foi salvo?",
                actions=actions
            )
        else:
            show_dialog(title="Nenhum arquivo para salvar", content="Selecione um arquivo antes de salvá-lo")

    def generate_form() -> None:
        viewer.controls.append(PageForm(paragraphs=dm.extract_form_rows()))
        viewer.update()

    def get_form_values() -> List[Tuple]:
        values = []
        for page_viewer in viewer.controls:
            values.extend(page_viewer.get_fields_values())
        return values

    def pick_files(func: Callable, allowed_extensions: List[str]) -> None:
        root_file_picker.on_result = func
        root_file_picker.pick_files(dialog_title='Abrir documento', allowed_extensions=allowed_extensions)

    def pick_path(func: Callable) -> None:
        root_file_picker.on_result = func
        root_file_picker.get_directory_path(dialog_title='Selecionar pasta')

    def save_file(func: Callable, file_name: str, allowed_extensions: List[str]) -> None:
        root_file_picker.on_result = func
        root_file_picker.save_file(dialog_title='Salvar como', file_name=file_name, allowed_extensions=allowed_extensions)

    def open_file(*args) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            try:
                if not e.files:
                    return

                input_path = e.files[0].path

                if not input_path:
                    return

                viewer.clean()
                dm.clear()
                loading_start()

                output_path = dm.change_file_path(path=input_path, folder='./.documents/')
                dm.create_dir(path=output_path)
                dm.copy_file_to(input_path=input_path, output_path=output_path)

                if output_path.endswith('.docx'):
                    dm.word_path = output_path
                    dm.docx2pdf(save_path=True)
                elif output_path.endswith('.pdf'):
                    dm.pdf_path = output_path
                    dm.pdf2docx(save_path=True)

                generate_form()
            except Exception as error:
                on_error(
                    title='Ocorreu um erro ao carregar o arquivo',
                    msg='Por favor verique se o documento existe ou se está corrompido.',
                    error=error
                )
            finally:
                loading_end()

        pick_files(func=pick_file_result, allowed_extensions=["docx", "pdf"])

    def save_word(*args) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_path := e.path:
                loading_start()
                try:
                    output_folder = dm.file_info(path=output_path)['abs_folder']
                    dm.save_changes(save_path=output_path, field_values=get_form_values())
                    show_dialog_saved_file(saved=True, output_path=output_path,  output_folder=output_folder)
                except FileNotFoundError as error:
                    on_error(
                        title='Ocorreu um erro ao salvar o arquivo',
                        msg='Por favor verique se a pasta existe.',
                        error=error
                    )
                except Exception as error:
                    on_error(error=error)
                loading_end()

        if word_path := dm.word_path:
            file_name = dm.file_info(path=word_path)['full_name']
            save_file(func=pick_file_result, allowed_extensions=['docx'], file_name=file_name)
        else:
            show_dialog_saved_file(saved=False)

    def save_pdf(*args) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_path := e.path:
                loading_start()
                try:
                    output_folder = dm.file_info(path=output_path)['abs_folder']
                    dm.save_changes(save_path=dm.word_path, field_values=get_form_values())
                    dm.docx2pdf(output_folder=output_folder)
                    show_dialog_saved_file(saved=True, output_path=output_path, output_folder=output_folder)
                except FileNotFoundError as error:
                    on_error(
                        title='Ocorreu um erro ao salvar o arquivo',
                        msg='Por favor verique se a pasta existe.',
                        error=error
                    )
                except Exception as error:
                    on_error(error=error)
                loading_end()

        if pdf_path := dm.pdf_path:
            file_name = dm.file_info(path=pdf_path)['full_name']
            save_file(func=pick_file_result, allowed_extensions=['pdf'], file_name=file_name)
        else:
            show_dialog_saved_file(saved=False)

    def save_images(*args) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_folder := e.path:
                loading_start()
                try:
                    output_folder = dm.file_info(path=output_folder, is_dir=True)['abs_folder']
                    dm.pdf2images(output_folder=output_folder)
                    show_dialog_saved_file(saved=True, output_folder=output_folder)
                except FileNotFoundError as error:
                    on_error(
                        title='Ocorreu um erro ao salvar o arquivo',
                        msg='Por favor verique se a pasta existe.',
                        error=error
                    )
                except Exception as error:
                    on_error(error=error)
                loading_end()

        if dm.pdf_path:
            pick_path(func=pick_file_result)
        else:
            show_dialog_saved_file(saved=False)

    def clear_form(*args) -> None:
        if dm.word_path or dm.pdf_path:
            def clear(*arg) -> None:
                [view_control.clear_values() for view_control in viewer.controls]
                close_dialog()

            button = TextButton(text='Sim', on_click=clear)
            show_dialog(title='Confirmação de exclusão', content='Tem certeza que quer excluir o que foi preenchido?', actions=[button])
        else:
            show_dialog(title='Nada para apagar', content='Carregue um documento antes de apagar seus campos')

    return build()
