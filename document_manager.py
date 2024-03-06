from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LTChar, LAParams, LTTextBox

from docx2pdf import convert
from pdf2docx import Converter
from pdf2image import convert_from_path
from PIL import Image as PILImage

from typing import List, Tuple, Dict

import concurrent.futures
import os
import re


class DocumentManager:
    def __init__(self):
        self.docx_path: str = ''
        self.pdf_path: str = ''
        self.poppler_path: str = './.poppler/Library/bin'
        self.path_pages_images: List[Dict[str, PILImage.Image]] = []
        self.fields_data: Dict[int, Dict[str, List]] = {}

    @staticmethod
    def open_path(path: str) -> None:
        os.startfile(path=path)

    @staticmethod
    def file_info(path: str) -> Tuple[str, str, str, str]:
        abs_path = os.path.abspath(path=path)
        abs_folder = os.path.dirname(abs_path)
        base_name, ext = os.path.splitext(os.path.basename(abs_path))
        return abs_path, abs_folder, base_name, ext

    def docx2pdf(self, output_path: str = './.documents/pdf.pdf', save_path: bool = False) -> None:
        abs_path, abs_folder, file_name, _ = self.file_info(path=output_path)
        output_path = os.path.join(abs_folder, file_name + '.pdf')

        os.makedirs(name=abs_folder, exist_ok=True)
        convert(input_path=self.docx_path, output_path=output_path, keep_active=True)

        if save_path:
            self.pdf_path = output_path

    def pdf2docx(self, output_path: str = './.documents/docx.docx', save_path: bool = False) -> None:
        abs_path, abs_folder, file_name, _ = self.file_info(path=output_path)
        output_path = os.path.join(abs_folder, file_name + '.docx')

        os.makedirs(name=abs_folder, exist_ok=True)
        cv = Converter(pdf_file=self.pdf_path)
        cv.convert(docx_filename=output_path)
        cv.close()

        if save_path:
            self.docx_path = output_path

    def save_image(self, path: str, img: PILImage.Image, save_path: bool = False) -> None:
        if save_path:
            self.path_pages_images.append({path: img})

        img.save(fp=path, bitmap_format='png')

    def pdf2images(
        self,
        output_folder: str = './.documents/images/',
        single_file: bool = None,
        save_path: bool = False,
    ) -> None:
        images = convert_from_path(
            pdf_path=self.pdf_path,
            single_file=single_file,
            poppler_path=self.poppler_path,
            thread_count=6,
        )

        file_name = self.file_info(self.pdf_path)[2]
        os.makedirs(name=output_folder, exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                lambda args: (self.save_image(*args)),
                [
                    (os.path.join(output_folder, f'{file_name}_{index}.png'), img, save_path)
                    for index, img in enumerate(images)
                ]
            )

        self.path_pages_images = sorted(self.path_pages_images, key=lambda d: list(d.keys()))

    def get_form_fields_data(self) -> None:
        with open(file=self.pdf_path, mode='rb') as file:
            resource_manager = PDFResourceManager()
            device = PDFPageAggregator(rsrcmgr=resource_manager, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr=resource_manager, device=device)

            for page_number, pdf_page in enumerate(PDFPage.get_pages(fp=file)):
                interpreter.process_page(page=pdf_page)
                layout = device.get_result()

                self.fields_data[page_number] = {'text_fields': [], 'check_boxes': []}

                for element in layout:
                    if isinstance(element, LTTextBox):
                        for text_line in element:
                            line_text = text_line.get_text()

                            for match in re.finditer(pattern=r'_+|:\s{2,}.+', string=line_text):
                                initial_index, final_index = match.span()
                                match_text: str = ''
                                min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')

                                for index, character in enumerate(iterable=text_line):
                                    if isinstance(character, LTChar):
                                        if initial_index <= index < final_index:
                                            size = character.size
                                            match_text += character.get_text()
                                            char_bbox = character.bbox
                                            min_x = min(min_x, char_bbox[0])
                                            min_y = min(min_y, char_bbox[1])
                                            max_x = max(max_x, char_bbox[2])
                                            max_y = max(max_y, char_bbox[3])

                                self.fields_data[page_number]['text_fields'].append(
                                    (min_x, min_y, max_x, max_y, match_text, size)
                                )

                            for match in re.finditer(pattern=r'\(\s*[Xx]?\s*\)', string=line_text):
                                initial_index, final_index = match.span()
                                selected: bool = False
                                min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')

                                for index, character in enumerate(iterable=text_line):
                                    if isinstance(character, LTChar):
                                        if initial_index <= index < final_index:
                                            selected = selected or 'x' in character.get_text().lower()
                                            char_bbox = character.bbox
                                            min_x = min(min_x, char_bbox[0])
                                            min_y = min(min_y, char_bbox[1])
                                            max_x = max(max_x, char_bbox[2])
                                            max_y = max(max_y, char_bbox[3])

                                self.fields_data[page_number]['check_boxes'].append(
                                    (min_x, min_y, max_x, max_y, selected)
                                )
    #
    # def get_form_fields_data(self) -> None:
    #     self.fields_data = {}
    #
    #     with fitz.open(self.pdf_path) as pdf:
    #         for page_number in range(len(pdf)):
    #             page = pdf.load_page(page_number)
    #
    #             self.fields_data[page_number] = {'text_fields': [], 'check_boxes': []}
    #
    #             lines = {}
    #             words: List[Tuple] = page.get_textpage().extractWORDS()
    #             for word in words:
    #                 lines[word[6]] = word
    #
    #
    #             # for match in re.search(pattern=r'_+|:\s{2,}', string=text):
    #             #     self.fields_data[page_number]['text_fields'].append((x1, y1, x2, y2, text, font_size))
    #             # for match in re.search(pattern=r'\(\s*[Xx]?\s*\)', string=text):
    #             #     selected = any('x' in char.lower() for char in text)
    #             #     self.fields_data[page_number]['check_boxes'].append((x1, y1, x2, y2, selected))

    def save_changes_on_docx(self):
        pass

    def clear(self):
        self.docx_path = ''
        self.pdf_path = ''
        self.path_pages_images = []
        self.fields_data = {}
