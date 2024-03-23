from typing import List, Callable
from enum import Enum
from document_manager import DocumentManager
from flet import *


class VisualizationMode(Enum):
    IMAGE = 'IMAGE'
    PARAGRAPH = 'PARAGRAPH'


class FormViewer(ListView):
    def __init__(self, images: List[str] = None, paragraphs: List = None, mode: VisualizationMode = VisualizationMode.PARAGRAPH):
        super().__init__()
        if paragraphs is None:
            paragraphs = []
        if images is None:
            images = []
            
        self.spacing = 10
        self.expand = True
        self.images_controls: List[Row] = []
        self.images: List[str] = images
        self.paragraphs_controls: List[Row] = []
        self.paragraphs: List[str] = paragraphs
        self.mode: VisualizationMode = mode
        self.fields: List[Control] = []

    def build(self) -> ListView:
        self.setup_paragraphs()
        self.setup_images()
        self.controls = self.paragraphs_controls
        return ListView(controls=self.controls)
    
    def update_controls(self, images: List = None, paragraphs: List = None) -> None:
        self.images = images
        self.paragraphs = paragraphs
        self.setup_images()
        self.setup_paragraphs()
        if self.mode == VisualizationMode.IMAGE:
            self.controls = self.images_controls
        else:
            self.controls = self.paragraphs_controls
        self.update()
    
    def setup_images(self) -> None:
        self.images_controls = [Image(src=image) for image in self.images]

    def setup_paragraphs(self) -> None:   
        self.paragraphs_controls.clear()
        
        for texts, align in self.paragraphs:  
            paragraph = self.create_paragraph_viewer(texts, align)
            self.paragraphs_controls.append(paragraph)
            
    def create_paragraph_viewer(self, texts: List[str], align: Alignment) -> Row:
        """
        Creates a paragraph viewer with the given texts and alignment.

        Parameters:
        ----------
        - texts (List[str]): The texts of the paragraph.
        - align (Alignment): The alignment of the paragraph.

        Returns:
        -------
        - Row: The paragraph viewer.
        """
        content = Row(wrap=True, alignment=align)
                        
        for text in texts:
            if '@TF' in text:
                control = self.create_textfield(value=text)
                content.controls.append(control)
                self.fields.append(control)
            elif '@CB' in text:
                control = self.create_checkbox(value='x' in text.lower())
                content.controls.append(control)
                self.fields.append(control)
            else:
                control = self.create_text(value=text)
                content.controls.append(control)
                self.fields.append(control)
                    
        return content

    def create_textfield(self, value: str = '') -> TextField:
        def resize_w(e: ControlEvent):
            c = e.control
            c.width = max(len(c.value) * 11, 50)
            c.update()
                        
        value = value.replace('@TF', '')
        
        return TextField(
            value=value.replace(':', ''),
            width=max(len(value) * 11, 50),
            height=30,
            content_padding=Padding(left=5, top=3, right=5, bottom=3),
            data={'type': '@TF', 'old_value': value},
            on_change=resize_w,
        )

    def create_checkbox(self, value: bool = False) -> Checkbox:
        return Checkbox(value=value, data={'type': '@CB', 'old_value': value})

    def create_text(self, value: str = '') -> Text:
        return Text(value=value, selectable=True, data={'type': '@TX', 'old_value': value})

    def get_paragraphs(self) -> List[str]:
        """
        Returns a list of strings, where each string is a paragraph of the form.
        The strings are constructed by concatenating the values of each control in the paragraph,
        separated by spaces.
        """
        paragraphs_texts = []
        for paragraph in self.paragraphs_controls:
            texts = []
            
            for control in paragraph.controls:
                if isinstance(control, TextField):
                    value = control.value 
                    old_value = control.data["old_value"]
                    texts.append((":" + value if old_value.startswith(":") else value) or old_value)
                elif isinstance(control, Text):
                    texts.append(control.value) or control.data["old_value"]
                elif isinstance(control, Checkbox):
                    texts.append('( X )' if control.value else '(  )')
                else:
                    continue
                
            paragraphs_texts.append(''.join(texts))

        return paragraphs_texts
 
    def clear_values(self) -> None:
        for field in self.fields:
            
            if isinstance(field, TextField):
                field.value = ""
                continue
            
            if isinstance(field, Checkbox):
                field.value = False
                continue
            
        self.update()

    def change_visualization_mode(self) -> None:
        """
        Switch between image and paragraph visualization modes.

        If the current mode is paragraph, the controls will be updated to display the images,
        and the mode will be set to image. If the current mode is image, the controls will be updated
        to display the paragraphs, and the mode will be set to paragraph.
        """
        if self.mode == VisualizationMode.PARAGRAPH:
            self.controls = self.images_controls
            self.mode = VisualizationMode.IMAGE
        else:
            self.controls = self.paragraphs_controls
            self.mode = VisualizationMode.PARAGRAPH
        self.update()


class Main(Row):
    def __init__(self, page: Page) -> None:
        super().__init__()
        self.page: Page = page
        self.dm: DocumentManager = DocumentManager()
        self.dialog: AlertDialog = AlertDialog()
        self.file_picker: FilePicker = FilePicker()
        self.load: ProgressRing = ProgressRing(visible=False, disabled=True)
        self.viewer: FormViewer = FormViewer()
        self.menu: GridView = GridView()
        self.page.add(self.dialog)
        self.page.window_prevent_close = True
        self.page.on_window_event = self.on_window_event
        self.expand = True
        self.alignment = MainAxisAlignment.CENTER
        self.vertical_alignment = CrossAxisAlignment.CENTER

    def build(self) -> Control:
        self.setup_menu()

        return Row(
            controls=[
                self.viewer,
                self.menu,
                self.file_picker,
                self.load,
            ],
            expand=True,
            alignment=MainAxisAlignment.CENTER,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )

    def setup_menu(self) -> None:
        self.menu = GridView(
            controls=[
                IconButton(icon=icons.FILE_UPLOAD, on_click=lambda _: self.open_file(), icon_color=colors.YELLOW_ACCENT_700, tooltip='Carregar arquivo'),
                IconButton(icon=icons.SAVE, on_click=lambda _: self.save_word(), icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar Word'),
                IconButton(icon=icons.PICTURE_AS_PDF, on_click=lambda _: self.save_pdf(), icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar PDF'),
                IconButton(icon=icons.PHOTO_LIBRARY, on_click=lambda _: self.save_images(), icon_color=colors.YELLOW_ACCENT_700, tooltip='Salvar Imagens'),
                IconButton(icon=icons.SUNNY, on_click=self.change_theme, icon_color=colors.YELLOW_ACCENT_700, tooltip='Mudar Tema'),
                IconButton(icon=icons.TEXT_FORMAT, on_click=self.change_visualization, icon_color=colors.YELLOW_ACCENT_700, tooltip='Mudar Visualização'),
                IconButton(icon=icons.DELETE, on_click=lambda _: self.clear_form(), icon_color=colors.YELLOW_ACCENT_700, tooltip='Apagar Campos'),
            ],
            spacing=10,
            width=50
        )

    def on_window_event(self, e: ControlEvent) -> None:
        if e.data == 'close':
            try:
                self.dm.clear()
            finally:
                self.page.window_destroy()
                exit(0)

    def on_error(self, title: str = '', msg: str = '', error: Exception | None = None) -> None:
        def on_more_click(_) -> None:
            msg_error.visible = True
            msg_error.disabled = False
            btn.icon = icons.REMOVE
            btn.on_click = on_minus_click
            content.update()

        def on_minus_click(_) -> None:
            msg_error.visible = False
            msg_error.disabled = True
            btn.icon = icons.ADD
            btn.on_click = on_more_click
            content.update()

        title = Text(value=title or "Ocorreu um erro", text_align=TextAlign.CENTER)
        msg = Text(value=msg, text_align=TextAlign.CENTER)
        msg_error = Text(
            value=f'Se preciso, informe o erro "{error}" para o desenvolvedor.', 
            selectable=True, 
            visible=False, 
            disabled=True,
            text_align=TextAlign.CENTER,
        )
        btn = IconButton(icon=icons.ADD, on_click=on_more_click)
        content = Row(controls=[msg, msg_error, btn], alignment=MainAxisAlignment.CENTER, wrap=True)
        self.show_dialog(title=title, content=content)

    def on_file_error(self, error: Exception):
        if isinstance(error, FileNotFoundError):
            self.on_error(
            title='Ocorreu um erro ao salvar o arquivo',
            msg='Por favor verique se a pasta existe.',
            error=error
        )
        elif isinstance(error, PermissionError):
            self.on_error(
            title='Permissão negada',
            msg='O documento que quer substituir pode estar sendo usado por outro programa.',
            error=error
        )
        else:
            self.on_error(error=error)

    def loading_start(self) -> None:
        self.viewer.disabled = True
        self.viewer.visible = False

        self.menu.disabled = True
        self.menu.visible = False

        self.load.disabled = False
        self.load.visible = True

        self.page.update()

    def loading_end(self) -> None:
        self.viewer.disabled = False
        self.viewer.visible = True

        self.menu.disabled = False
        self.menu.visible = True

        self.load.disabled = True
        self.load.visible = False

        self.page.update()

    def change_theme(self, e: ControlEvent) -> None:
        button_control: IconButton = e.control

        page_theme = self.page.theme_mode

        if page_theme is ThemeMode.DARK:
            button_control.icon = icons.SUNNY
            self.page.theme_mode = ThemeMode.LIGHT
        else:
            button_control.icon = icons.NIGHTLIGHT
            self.page.theme_mode = ThemeMode.DARK

        button_control.update()
        self.page.update()

    def change_visualization(self, e: ControlEvent) -> None:
        self.viewer.change_visualization_mode()
        icon_button = e.control
        if self.viewer.mode == VisualizationMode.PARAGRAPH:
            icon_button.icon = icons.TEXT_FORMAT
        else:
            icon_button.icon = icons.IMAGE
        icon_button.update()

    def show_dialog(self, title: str | Control | None = None, content: str | Control | None = None, actions: List[Control] | None = None) -> None:
        if isinstance(title, str):
            title = Text(value=title)

        if isinstance(content, str):
            content = Text(value=content)

        self.dialog.title = title
        self.dialog.content = content
        self.dialog.actions = actions
        self.dialog.elevation = 10
        self.dialog.actions_alignment = MainAxisAlignment.END

        self.dialog.open = True
        self.page.update()

    def close_dialog(self) -> None:
        self.dialog.open = False
        self.dialog.title.clean()
        self.dialog.content.clean()
        self.dialog.actions.clear()
        self.dialog.update()

    def show_dialog_saved_file(self, saved: bool, output_path: str = '', output_folder: str = '') -> None:
        if saved:
            actions = []

            if output_path:
                actions.append(TextButton(
                    text='Abrir arquivo',
                    on_click=lambda _: self.dm.open_path(path=output_path)
                ))

            if output_folder:
                actions.append(TextButton(
                    text='Abrir pasta',
                    on_click=lambda _: self.dm.open_path(path=output_folder)
                ))

            self.show_dialog(
                title="Documento salvo",
                content="Deseja abrir no Explorer o(a) arquivo/pasta onde foi salvo?",
                actions=actions
            )
        else:
            self.show_dialog(title="Nenhum arquivo para salvar", content="Selecione um arquivo antes de salvá-lo")

    def pick_file(self, func: Callable, allowed_extensions: List[str]) -> None:
        self.file_picker.on_result = func
        self.file_picker.pick_files(dialog_title='Abrir documento', allowed_extensions=allowed_extensions)

    def pick_path(self, func: Callable) -> None:
        self.file_picker.on_result = func
        self.file_picker.get_directory_path(dialog_title='Abrir pasta')

    def open_file(self) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            try:
                if not e.files:
                    return

                input_path = e.files[0].path

                if not input_path:
                    return

                self.viewer.clean()
                self.dm.clear()
                self.loading_start()

                output_path = self.dm.change_file_path(path=input_path, folder=self.dm.default_path + ".documents/")
                self.dm.create_dir(path=output_path)
                self.dm.copy_file_to(input_path=input_path, output_path=output_path)
                abs_output_path = self.dm.file_info(path=output_path)['abs_path']
                
                if output_path.endswith('.docx'):
                    self.dm.word_path = abs_output_path
                    self.dm.docx2pdf(save_path=True)
                elif output_path.endswith('.pdf'):
                    self.dm.pdf_path = abs_output_path
                    self.dm.pdf2docx(save_path=True)

                self.generate_form()
            except Exception as error:
                self.on_error(
                    title='Ocorreu um erro ao carregar o arquivo',
                    msg='Por favor verique se o documento existe ou se está corrompido.',
                    error=error
                )
            finally:
                self.loading_end()

        self.pick_file(func=pick_file_result, allowed_extensions=["docx", "pdf"])

    def save_word(self) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_folder := e.path:
                self.loading_start()
                
                try:
                    self.dm.save_changes(save_folder=output_folder, paragraphs=self.get_paragraphs())
                    self.show_dialog_saved_file(saved=True, output_folder=output_folder)
                except Exception as error:
                    self.on_file_error(error=error)
                    
                self.loading_end()

        if self.dm.word_path:
            self.pick_path(func=pick_file_result)
        else:
            self.show_dialog_saved_file(saved=False)

    def save_pdf(self) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_folder := e.path:
                self.loading_start()
                
                try:
                    self.dm.save_changes(paragraphs=self.get_paragraphs())
                    self.dm.docx2pdf(output_folder=output_folder)
                    self.show_dialog_saved_file(saved=True, output_folder=output_folder)
                except Exception as error:
                    self.on_file_error(error=error)
                    
                self.loading_end()

        if self.dm.word_path:
            self.pick_path(func=pick_file_result)
        else:
            self.show_dialog_saved_file(saved=False)
            
    def save_images(self) -> None:
        def pick_file_result(e: FilePickerResultEvent) -> None:
            if output_folder := e.path:
                self.loading_start()
                
                try:
                    self.dm.save_changes(paragraphs=self.get_paragraphs())
                    self.dm.docx2pdf()
                    self.dm.pdf2images(output_folder=output_folder)
                    self.show_dialog_saved_file(saved=True, output_folder=output_folder)
                except Exception as error:
                    self.on_file_error(error=error)
                    
                self.loading_end()

        if self.dm.word_path:
            self.pick_path(func=pick_file_result)
        else:
            self.show_dialog_saved_file(saved=False)

    def generate_form(self) -> None:
        self.viewer.update_controls(self.dm.pdf2images(save_path=True), self.dm.extract_form_rows())

    def get_paragraphs(self) -> List[str]:
        return self.viewer.get_paragraphs()

    def clear_form(self) -> None:
        if self.dm.word_path:
            def clear() -> None:
                self.viewer.clear_values()
                self.close_dialog()

            button = TextButton(text='Sim', on_click=lambda _: clear())
            self.show_dialog(title='Confirmação de exclusão', content='Tem certeza que quer excluir o que foi preenchido?', actions=[button])
        else:
            self.show_dialog(title='Nada para apagar', content='Carregue um documento antes de apagar seus campos')
