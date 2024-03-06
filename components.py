from typing import List, Tuple, Dict, Union, Any, Callable

from document_manager import DocumentManager
from data import FieldsData
from PIL import Image as PILImage
from flet import *
import os


class PDFPageViewer(UserControl):
    def __init__(self, page_image: Dict[str, PILImage.Image], fields_data: FieldsData):
        super().__init__()
        path, page_image = page_image.popitem()
        self.layout = Stack()
        self.size: Tuple[float, float] = page_image.size
        self.image = Image(src=os.path.abspath(path=path))
        self.fields_data: FieldsData = fields_data
        self.fields: List[Union[TextField | Checkbox]] = []

    def build(self) -> Stack:
        self.layout.controls.append(self.image)
        self.generate_components()
        return self.layout

    def generate_components(self) -> None:
        while data := self.fields_data.next():
            field = data.component_type(**data.args)
            x1, y1, x2, y2 = data.bbox
            field.value = data.value

            # img_w, img_h = (self.size[0] / 2, self.size[1] / 2)
            #
            # field.width = x2 - x1
            # field.height = y2 - y1
            #
            # element = Container(
            #     content=field,
            #     alignment=Alignment(x=(x2 - img_w) / img_w, y=(y2 - img_h) / img_w),
            # )

            element = Stack(
                controls=[field],
                width=(x2 - x1),
                height=(y2 - y1),
                left=x1,
                bottom=y1,
            )

            self.fields.append(field)
            self.layout.controls.append(element)

    def get_values(self) -> List[Any]:
        return [field.value for field in self.fields]

    def clear_values(self) -> None:
        for field in self.fields:
            field.value = None
        self.update()


# class MainPage(UserControl):
#     def __init__(self, parent: Page):
#         super().__init__()
#         self.parent: Page = parent
#         self.row = Row(
#             expand=True,
#             alignment=MainAxisAlignment.CENTER,
#             vertical_alignment=CrossAxisAlignment.START
#         )
#         self.document_manager: DocumentManager = DocumentManager()
#         self.dialog: AlertDialog = AlertDialog(on_dismiss=self.close_dialog, visible=False, disabled=True)
#         self.file_picker: FilePicker = FilePicker()
#         self.load = ProgressRing(visible=False, disabled=True)
#         self.viewer: ListView = ListView(height=self.parent.height, expand=True, spacing=10)
#         self.menu: UserControl = UserControl()
#
#     def loading_start(self) -> None:
#         self.viewer.disabled = True
#         self.viewer.visible = False
#
#         self.menu.disabled = True
#         self.menu.visible = False
#
#         self.load.disabled = False
#         self.load.visible = True
#
#         self.row.update()
#
#     def loading_end(self) -> None:
#         self.viewer.disabled = False
#         self.viewer.visible = True
#
#         self.menu.disabled = False
#         self.menu.visible = True
#
#         self.load.disabled = True
#         self.load.visible = False
#
#         self.row.update()
#
#     def change_theme(self, e: ControlEvent) -> None:
#         button_control: IconButton = e.control
#
#         page_theme = self.parent.theme_mode
#
#         if page_theme is ThemeMode.DARK:
#             button_control.icon = icons.SUNNY
#             self.parent.theme_mode = ThemeMode.LIGHT
#         else:
#             button_control.icon = icons.NIGHTLIGHT
#             self.parent.theme_mode = ThemeMode.DARK
#
#         button_control.update()
#         self.parent.update()
#
#     def build(self) -> Control:
#         self.setup_menu()
#
#         self.row.controls = [self.viewer, self.menu, self.file_picker, self.dialog, self.load]
#         return self.row
#
#     def setup_menu(self) -> None:
#         self.menu = GridView(spacing=10, width=50)
#
#         menu_buttons = [
#             IconButton(icon=icons.FILE_UPLOAD, on_click=self.open_file, icon_color=colors.YELLOW_ACCENT_700),
#             IconButton(icon=icons.SAVE_ROUNDED, on_click=self.save_document, icon_color=colors.YELLOW_ACCENT_700),
#             IconButton(icon=icons.PICTURE_AS_PDF, on_click=self.save_pdf, icon_color=colors.YELLOW_ACCENT_700),
#             IconButton(icon=icons.PHOTO_LIBRARY, on_click=self.save_images, icon_color=colors.YELLOW_ACCENT_700),
#             IconButton(icon=icons.SUNNY, on_click=self.change_theme, icon_color=colors.YELLOW_ACCENT_700),
#             IconButton(icon=icons.DELETE, on_click=self.clear_form, icon_color=colors.YELLOW_ACCENT_700),
#         ]
#         [self.menu.controls.append(button) for button in menu_buttons]
#
#     def close_dialog(self, *args) -> None:
#         self.dialog.open = False
#         self.dialog.visible = False
#         self.dialog.disabled = True
#         self.row.update()
#         self.update()
#
#     def show_dialog(
#             self,
#             title: str | Text | None = None,
#             content: str | Text | None = None,
#             actions: List[TextButton] | None = None
#     ) -> None:
#         if isinstance(title, str):
#             title = Text(value=title)
#
#         if isinstance(content, str):
#             content = Text(value=content)
#
#         self.dialog.title = title
#         self.dialog.content = content
#         self.dialog.actions = actions
#         self.dialog.elevation = 10
#         self.dialog.actions_alignment = MainAxisAlignment.END
#
#         self.dialog.open = True
#         self.dialog.visible = True
#         self.dialog.disabled = False
#         self.row.update()
#
#     def show_dialog_saved_file(self, saved: bool, output_folder: str = '', output_path: str = '') -> None:
#         if saved:
#             saved_dialog_buttons = [
#                 TextButton(text='Abrir pasta', on_click=lambda x: os.startfile(os.path.abspath(output_folder))),
#                 TextButton(text='Abrir arquivo', on_click=lambda x: os.startfile(os.path.abspath(output_path))),
#             ]
#             self.show_dialog(
#                 title="Documento salvo",
#                 content="Deseja abrir no Explorer o(a) arquivo/pasta onde o arquivo foi salvo?",
#                 actions=saved_dialog_buttons
#             )
#         else:
#             self.show_dialog(title="Nenhum arquivo para salvar", content="Selecione um arquivo antes de salvá-lo")
#
#     def generate_form_components_from_data(self) -> None:
#         for page_number, path in enumerate(self.document_manager.path_pages_images):
#             text_fields, check_boxes = self.document_manager.fields_data[page_number].values()
#             components_data = ComponentsData()
#
#             for x1, y1, x2, y2, value, text_size in text_fields:
#                 components_data.add(
    #                 component_type=TextField,
    #                 page_number=page_number,
    #                 bbox=(x1, y1, x2, y2),
    #                 value=value,
    #                 args={'text_size': text_size, 'multiline': False}
#                 )
#
#             for x1, y1, x2, y2, value in check_boxes:
    #                 components_data.add(
    #                 component_type=Checkbox,
    #                 page_number=page_number,
    #                 bbox=(x1, y1, x2, y2),
    #                 value=value, args={}
#                 )
#
#             self.viewer.controls.append(PDFPageViewer(path, components_data))
#
#         self.viewer.update()
#
#     def pick_files(self, func: Callable) -> None:
#         self.file_picker.on_result = func
#         self.file_picker.pick_files(dialog_title='Abrir documento', allowed_extensions=["doc", "docx", "pdf"])
#
#     def pick_path(self, func: Callable) -> None:
#         self.file_picker.on_result = func
#         self.file_picker.get_directory_path(dialog_title='Selecionar pasta')
#
#     def save_file(
#             self,
#             func: Callable,
#             allowed_extensions: List[str],
#             file_name: str
#     ) -> None:
#         self.file_picker.on_result = func
#         self.file_picker.save_file(
#             dialog_title='Salvar como',
#             file_name=file_name,
#             allowed_extensions=allowed_extensions
#         )
#
#     def open_file(self, *args) -> None:
#         def pick_file_result(e: FilePickerResultEvent) -> None:
#             if not e.files:
#                 return
#
#             new_path = e.files[0].path
#
#             if not new_path:
#                 return
#
#             self.viewer.clean()
#             self.document_manager.clear()
#             self.loading_start()
#
#             etx = self.document_manager.file_info(new_path)[3]
#
#             if etx == 'doc' or etx == 'docx':
#                 self.document_manager.docx_path = new_path
#                 self.document_manager.docx2pdf(save_path=True)
#             elif etx == 'pdf':
#                 self.document_manager.pdf_path = new_path
#                 self.document_manager.pdf2docx(save_path=True)
#
#             self.document_manager.pdf2images(save_path=True)
#             self.document_manager.get_form_fields_data()
#
#             self.generate_form_components_from_data()
#             self.loading_end()
#
#         self.pick_files(func=pick_file_result)
#
#     def save_document(self, *args) -> None:
#         def pick_file_result(e: FilePickerResultEvent) -> None:
#             output_path = e.path
#             if output_path:
#                 output_folder = os.path.dirname(p=output_path)
#                 self.document_manager.pdf2docx(output_path=output_path)
#                 self.show_dialog_saved_file(saved=True, output_folder=output_folder, output_path=output_path)
#
#         if file_name := self.document_manager.docx_path:
#             file_name = self.document_manager.file_info(file_name)[1]
#             self.save_file(func=pick_file_result, file_name=file_name, allowed_extensions=["doc", "docx"])
#         else:
#             self.show_dialog_saved_file(saved=False)
#
#     def save_pdf(self, *args) -> None:
#         def pick_file_result(e: FilePickerResultEvent) -> None:
#             output_path = e.path
#             if output_path:
#                 output_folder = os.path.dirname(p=output_path)
#                 self.document_manager.docx2pdf(output_path=output_path)
#                 self.show_dialog_saved_file(saved=True, output_folder=output_folder, output_path=output_path)
#
#         if file_name := self.document_manager.pdf_path:
#             file_name = self.document_manager.file_info(file_name)[1]
#             self.save_file(func=pick_file_result, file_name=file_name, allowed_extensions=["pdf"])
#         else:
#             self.show_dialog_saved_file(saved=False)
#
#     def save_images(self, *args) -> None:
#         def pick_file_result(e: FilePickerResultEvent) -> None:
#             output_folder = e.path
#             if output_folder:
#                 self.document_manager.pdf2images(output_folder=output_folder)
    #                 self.show_dialog_saved_file(
    #                 saved=True,
    #                 output_folder=output_folder,
    #                 output_path=self.document_manager.pdf_path
#                 )
#
#         if self.document_manager.pdf_path:
#             self.pick_path(pick_file_result)
#         else:
#             self.show_dialog_saved_file(saved=False)
#
#     def clear_form(self, *args) -> None:
#         if self.document_manager.docx_path or self.document_manager.pdf_path:
#             def clear(*arg) -> None:
#                 for view_control in self.viewer.controls:
#                     view_control: PDFPageViewer
#                     view_control.clear_values()
#
#                 self.close_dialog()
#
#             button = TextButton(text='Sim', on_click=clear)
#             self.show_dialog(
    #             title='Confirmação de exclusão',
    #             content='Tem certeza que quer excluir o que foi preenchido?',
    #             actions=[button]
#             )
#         else:
#             self.show_dialog(title='Nada para apagar', content='Carregue um documento antes de apagar seus campos')


def MainPage(root: Page) -> Control:
    root_row = Row(
        expand=True,
        adaptive=True,
        alignment=MainAxisAlignment.CENTER,
        vertical_alignment=CrossAxisAlignment.CENTER,
    )
    document_manager: DocumentManager = DocumentManager()
    root_dialog: AlertDialog = AlertDialog()
    root_file_picker: FilePicker = FilePicker()
    load = ProgressRing(visible=False, disabled=True)
    viewer: UserControl = UserControl()
    menu: UserControl = UserControl()

    def on_page_resize(e: ControlEvent) -> None:
        page_control: Page = e.control
        page_control.update(viewer, menu)

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

    def build() -> Control:
        nonlocal root_row, viewer, menu, root_file_picker, load
        viewer = setup_viewer()
        menu = setup_menu()

        root_row.controls = [viewer, menu, root_file_picker, load]
        return root_row

    def setup_viewer() -> ListView:
        nonlocal viewer
        viewer = ListView(expand=True, spacing=10)
        return viewer

    def setup_menu() -> GridView:
        nonlocal menu
        menu = GridView(spacing=10, width=50)

        menu_buttons = [
            IconButton(icon=icons.FILE_UPLOAD, on_click=open_file, icon_color=colors.YELLOW_ACCENT_700),
            IconButton(icon=icons.SAVE_ROUNDED, on_click=save_document, icon_color=colors.YELLOW_ACCENT_700),
            IconButton(icon=icons.PICTURE_AS_PDF, on_click=save_pdf, icon_color=colors.YELLOW_ACCENT_700),
            IconButton(icon=icons.PHOTO_LIBRARY, on_click=save_images, icon_color=colors.YELLOW_ACCENT_700),
            IconButton(icon=icons.SUNNY, on_click=change_theme, icon_color=colors.YELLOW_ACCENT_700),
            IconButton(icon=icons.DELETE, on_click=clear_form, icon_color=colors.YELLOW_ACCENT_700),
        ]
        [menu.controls.append(button) for button in menu_buttons]
        return menu

    def close_dialog() -> None:
        root_dialog.open = False
        root_dialog.update()

    def show_dialog(
            title: str | Text | None = None,
            content: str | Text | None = None,
            actions: List[TextButton] | None = None
    ) -> None:
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

    def show_dialog_saved_file(saved: bool, output_folder: str = '', output_path: str = ''):
        if saved:
            saved_dialog_buttons = [
                TextButton(text='Abrir pasta', on_click=lambda x: os.startfile(os.path.abspath(output_folder))),
                TextButton(text='Abrir arquivo', on_click=lambda x: os.startfile(os.path.abspath(output_path))),
            ]
            show_dialog(title="Documento salvo",
                        content="Deseja abrir no Explorer o(a) arquivo/pasta onde o arquivo foi salvo?",
                        actions=saved_dialog_buttons)
        else:
            show_dialog(title="Nenhum arquivo para salvar", content="Selecione um arquivo antes de salvá-lo")

    def generate_form_components_from_data():
        for page_number, page_image in enumerate(document_manager.path_pages_images):
            text_fields, check_boxes = document_manager.fields_data[page_number].values()
            fields_data = FieldsData()

            for x1, y1, x2, y2, value, text_size in text_fields:
                fields_data.add(
                    component_type=TextField,
                    page_number=page_number,
                    bbox=(x1, y1, x2, y2),
                    value=value,
                    args={'text_size': text_size}
                )

            for x1, y1, x2, y2, value in check_boxes:
                fields_data.add(
                    component_type=Checkbox,
                    page_number=page_number,
                    bbox=(x1, y1, x2, y2),
                    value=value,
                    args={}
                )

            viewer.controls.append(PDFPageViewer(page_image=page_image, fields_data=fields_data))

        viewer.update()

    def pick_files(func: Callable, allowed_extensions: List[str]) -> None:
        root_file_picker.on_result = func
        root_file_picker.pick_files(dialog_title='Abrir documento', allowed_extensions=allowed_extensions)

    def pick_path(func: Callable) -> None:
        root_file_picker.on_result = func
        root_file_picker.get_directory_path(dialog_title='Selecionar pasta')

    def save_file(
            func: Callable,
            allowed_extensions: List[str],
            file_name: str
    ) -> None:
        root_file_picker.on_result = func
        root_file_picker.save_file(
            dialog_title='Salvar como',
            file_name=file_name,
            allowed_extensions=allowed_extensions
        )

    def open_file(*args):
        def pick_file_result(e: FilePickerResultEvent) -> None:
            nonlocal document_manager, viewer

            if not e.files:
                return

            new_path = e.files[0].path

            if not new_path:
                return

            etx = document_manager.file_info(path=new_path)[3]

            viewer.clean()
            document_manager.clear()
            loading_start()

            if etx == '.doc' or etx == '.docx':
                document_manager.docx_path = new_path
                document_manager.docx2pdf(save_path=True)
            elif etx == '.pdf':
                document_manager.pdf_path = new_path
                document_manager.pdf2docx(save_path=True)

            document_manager.pdf2images(save_path=True)
            document_manager.get_form_fields_data()

            generate_form_components_from_data()
            loading_end()

        pick_files(func=pick_file_result, allowed_extensions=["doc", "docx", "pdf"])

    def save_document(*args):
        def pick_file_result(e: FilePickerResultEvent) -> None:
            output_path = e.path
            if output_path:
                output_folder = os.path.dirname(p=output_path)
                document_manager.pdf2docx(output_path=output_path)
                show_dialog_saved_file(saved=True, output_folder=output_folder, output_path=output_path)

        if word_path := document_manager.docx_path:
            save_file(
                func=pick_file_result,
                allowed_extensions=["doc", "docx"],
                file_name=document_manager.file_info(path=word_path)[2]
            )
        else:
            show_dialog_saved_file(saved=False)

    def save_pdf(*args):
        def pick_file_result(e: FilePickerResultEvent) -> None:
            output_path = e.path
            if output_path:
                output_folder = os.path.dirname(p=output_path)
                document_manager.docx2pdf(output_path=output_path)
                show_dialog_saved_file(saved=True, output_folder=output_folder, output_path=output_path)

        if word_path := document_manager.pdf_path:
            save_file(
                func=pick_file_result,
                allowed_extensions=["pdf"],
                file_name=document_manager.file_info(path=word_path)[2]
            )
        else:
            show_dialog_saved_file(saved=False)

    def save_images(*args):
        def pick_file_result(e: FilePickerResultEvent) -> None:
            output_folder = e.path
            if output_folder:
                document_manager.pdf2images(output_folder=output_folder)
                show_dialog_saved_file(saved=True, output_folder=output_folder, output_path=document_manager.pdf_path)

        if document_manager.pdf_path:
            pick_path(func=pick_file_result)
        else:
            show_dialog_saved_file(saved=False)

    def clear_form(*args) -> None:
        if document_manager.docx_path or document_manager.pdf_path:
            def clear(*arg) -> None:
                for view_control in viewer.controls:
                    view_control: PDFPageViewer
                    view_control.clear_values()

                close_dialog()

            button = TextButton(text='Sim', on_click=clear)
            show_dialog(title='Confirmação de exclusão', content='Tem certeza que quer excluir o que foi preenchido?',
                        actions=[button])
        else:
            show_dialog(title='Nada para apagar', content='Carregue um documento antes de apagar seus campos')

    root.on_resize = on_page_resize
    root.add(root_dialog)
    return build()
