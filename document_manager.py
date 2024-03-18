from docx import Document as ReadWord
from pdf2image import convert_from_path
from pdf2docx import Converter
from docx2pdf import convert

from typing import List, Tuple, Dict

import shutil
import os
import re


class DocumentManager:
    def __init__(self):
        self.word_path: str = ''
        self.pdf_path: str = ''
        self.default_folder = './.documents/'
        self.poppler_path: str = './.poppler/Library/bin'

    def open_path(self, path: str) -> None:
        path = self.file_info(path)['abs_path']
        os.startfile(filepath=path)

    def change_file_path(self, path: str, folder: str = '', file_name: str = '', ext: str = ''):
        _, folder_info, _, file_name_info, ext_info = self.file_info(path=path).values()
        folder = folder or folder_info
        file_name = file_name or file_name_info
        ext = ext or ext_info
        return os.path.join(folder, file_name + ext)

    def create_dir(self, path: str, is_dir: bool = False) -> None:
        folder = self.file_info(path=path, is_dir=is_dir)['abs_folder']
        os.makedirs(name=folder, exist_ok=True)

    @staticmethod
    def file_info(path: str, is_dir: bool = False) -> Dict[str, str]:
        abs_path = os.path.abspath(path=path)
        abs_folder = abs_path if is_dir or os.path.isdir(s=abs_path) else os.path.dirname(p=abs_path)
        base_name, ext = os.path.splitext(p=os.path.basename(p=abs_path))
        complete_name = base_name + ext

        return {
            'abs_path': abs_path,
            'abs_folder': abs_folder,
            'full_name': complete_name,
            'base_name': base_name,
            'ext': ext
        }

    @staticmethod
    def copy_file_to(input_path: str, output_path: str) -> bool:
        try:
            shutil.copy(src=input_path, dst=output_path)
            return True
        except shutil.SameFileError:
            return False

    def docx2pdf(self, output_folder: str = '', save_path: bool = False) -> None:
        output_folder = output_folder if output_folder else self.default_folder
        abs_path = self.file_info(path=self.word_path)['abs_path']
        output_path = self.change_file_path(path=abs_path, folder=output_folder, ext='.pdf')
        
        self.create_dir(path=output_path)
        convert(input_path=abs_path, output_path=output_path, keep_active=True)

        if save_path:
            self.pdf_path = output_path

    def pdf2docx(self, output_folder: str = '', save_path: bool = False) -> None:
        output_folder = output_folder if output_folder else self.default_folder
        abs_path = self.file_info(path=self.pdf_path)['abs_path']
        output_path = self.change_file_path(path=abs_path, folder=output_folder, ext='.docx')

        self.create_dir(path=output_path)
        cv = Converter(pdf_file=abs_path)
        cv.convert(docx_filename=output_path, start=0)
        cv.close()

        if save_path:
            self.word_path = output_path

    def pdf2images(self, output_folder: str = '', single_file: bool = False) -> None:
        output_folder = output_folder if output_folder else self.default_folder + 'images/'
        file_name = self.file_info(path=self.pdf_path)['base_name']
        self.create_dir(path=output_folder, is_dir=True)

        convert_from_path(
            pdf_path=self.pdf_path,
            fmt='png',
            thread_count=6,
            output_folder=output_folder,
            single_file=single_file,
            output_file=file_name,
            poppler_path=self.poppler_path,
            paths_only=True,
        )

    def extract_form_rows(self) -> list[tuple[list[str], str]]:
        word = ReadWord(self.word_path)
        paragraphs = []

        for paragraph in word.paragraphs:
            text = paragraph.text.strip('\n')
            if paragraph.alignment:
                align = paragraph.alignment.name
            else:
                align = 'LEFT'

            if text:
                text = re.sub(r'_+', '#SL@TF#SL', text)
                text = re.sub(r':(.*?)(?<!\()\s\s', lambda match: '#SL' + match.group(0) + '@TF' + '#SL', text)
                text = re.sub(r'\(\s*(?:[Xx]\s*)?\)', '#SL@CB#SL', text)
                parts = text.split('#SL')
                paragraph.text = ''.join(parts)
                paragraphs.append((parts, align))

        word.save(self.word_path)
        return paragraphs

    def save_changes(self, save_path: str, field_values: List[Tuple]) -> None:
        word = ReadWord(self.word_path)
                
        for paragraph in word.paragraphs:
            for new_text, mark in field_values[:]:
                if mark in paragraph.text:
                    paragraph.text = paragraph.text.replace(mark, new_text, 1)
                    field_values.remove((new_text, mark))
                    
        word.save(save_path)

    def clear(self) -> None:
        if abs_word_path := os.path.abspath(self.word_path):
            if os.path.isfile(abs_word_path):
                os.remove(abs_word_path)

        self.word_path = ''

        if abs_pdf_path := os.path.abspath(self.pdf_path):
            if os.path.isfile(abs_pdf_path):
                os.remove(abs_pdf_path)

        self.pdf_path = ''
