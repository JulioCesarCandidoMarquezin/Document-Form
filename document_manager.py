from docx import Document as ReadWord
from docx2pdf import convert
from pdf2docx import Converter
from pdf2image import convert_from_path

from typing import List, Tuple, Dict

import pythoncom
import shutil
import os
import re


class DocumentManager:
    def __init__(self):
        self.word_path: str = ''
        self.pdf_path: str = ''
        self.images_paths: List = []
        self.default_path: str = './_internal/'
        self.poppler_path: str = os.path.abspath(path=self.default_path + '.poppler/Library/bin')

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
        """
        Returns a dictionary containing information about the specified file or directory.

        Parameters
        ----------
        path : str
            The path of the file or directory.
        is_dir : bool, optional
            Indicates whether the specified path is a directory. The default is False.

        Returns
        -------
        Dict[str, str]
            A dictionary containing the following keys and values:

            - abs_path (str): The absolute path of the file or directory.
            - abs_folder (str): The absolute path of the directory that contains the file or directory.
            - full_name (str): The full name of the file or directory, including the extension.
            - base_name (str): The base name of the file or directory, without the extension.
            - ext (str): The extension of the file, including the dot (".").

        """
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
    def copy_file_to(input_path: str, output_path: str) -> None:
        try:
            shutil.copy(src=input_path, dst=output_path)
            return True
        except shutil.SameFileError:
            return False

    def docx2pdf(self, output_folder: str = '', save_path: bool = False) -> None:
        output_folder = output_folder or self.default_path + '.documents/'
        output_folder = os.path.abspath(output_folder)
        output_path = self.change_file_path(path=self.word_path, folder=output_folder, ext='.pdf')
                
        self.create_dir(path=output_path)
        pythoncom.CoInitialize()
        file = open(output_path, "wb")
        file.close()
        convert(input_path=self.word_path, output_path=output_path)
        
        if save_path:
            self.pdf_path = output_path

    def pdf2docx(self, output_folder: str = '', save_path: bool = False) -> None:
        output_folder = output_folder or self.default_path + '.documents/'
        output_folder = os.path.abspath(output_folder)
        abs_path = self.file_info(path=self.pdf_path)['abs_path']
        output_path = self.change_file_path(path=abs_path, folder=output_folder, ext='.docx')

        self.create_dir(path=output_path)
        cv = Converter(pdf_file=abs_path)
        cv.convert(docx_filename=output_path, start=0)
        cv.close()

        if save_path:
            self.word_path = output_path
            
    def pdf2images(self, output_folder: str = '', single_file: bool = False, save_path: bool = False) -> List[str]:
        output_folder = output_folder or self.default_path + '.documents/images'
        output_folder = os.path.abspath(output_folder)
        file_name = self.file_info(path=self.pdf_path)['base_name']
        self.create_dir(path=output_folder, is_dir=True)

        images = convert_from_path(
            pdf_path=self.pdf_path,
            fmt='png',
            thread_count=6,
            output_folder=output_folder,
            single_file=single_file,
            output_file=file_name,
            poppler_path=self.poppler_path,
            paths_only=True,
        )
        
        if save_path:
            self.images_paths = images
        
        return images

    def extract_form_rows(self) -> List[Tuple[List[str], str]]:
        """ Extracts form rows from a docx file 
        
        Types:
        -----
        - @TF (TextField) 
        - @CB (CheckBox)
        
        Example:
        -------
            Paragraph: "Something ____ ( X )" align: CENTER \n
            Paragraph: "Something too" align: LEFT \n
            return [
                (
                    ["Something ", "___ @TF", "( X )@CB"], CENTER
                ),
                (
                    ["Something too"], LEFT
                )
            ] 
        
        Matches:
        -------
            - '____'
            - ': Something'
            - '01/01/2000'
            - '2010' or 'n°2010' or 'n° 2010' Not for while
            - '( X )' or '( )' ...
            
        Returns:
        -------
            List[Tuple[List[str], str]]: list of tuples (texts list, align)
        """
        word = ReadWord(self.word_path)
        paragraphs = []

        for paragraph in word.paragraphs:     
            text = paragraph.text
            align = paragraph.alignment.name if paragraph.alignment else 'LEFT'         
                    
            text = re.sub(r'_+', lambda match: # '____'   
                "#SM" + match.group(0) + "@TF#SM", text)  
            
            text = re.sub(r':(\s\w+[^.]*(?!.)*)+', # ': Something'
                lambda match: "#SM" + match.group(0) + "@TF#SM", text)
                        
            text = re.sub(r'(:\s*(?!\s*\(|\s{0,1}\b|\s*#))', # ':        '
                lambda match: "#SM" + match.group(1) + "@TF#SM", text)
                                    
            text = re.sub(r'\d{2}/\d{2}/\d{4}', lambda match: # '01/01/2000'
                "#SM" + match.group(0) + "@TF#SM", text)
            
            text = re.sub(r'\d{2} de \w+ de (\d{4})', # '01 de julho de 2004'
                lambda match: "#SM" + match.group(0) + "@TF#SM", text)
            
            # text = re.sub(r'(n°)*(\s{0,1}\d{4})\s', # '2010' or 'n°2010' or 'n° 2010'
            #     lambda match: "#SM" + match.group(0) + "@TF#SM", text, flags=re.IGNORECASE)
            
            text = re.sub(r'\(\s*(?:x\s*)?\)', # '( X )' or '( )' ...
                '#SM@CB#SM', text, flags=re.IGNORECASE)
            
            # '#SM' Is a Split Mark what will be used to split the text in the list "paragraphs".
            parts = text.split('#SM')
            paragraphs.append((parts, align))

        return paragraphs

    def save_changes(self, save_folder: str = '', paragraphs: List[str] = []) -> None:
        """
        Saves the changes made to the Word document.

        Parameters:
        -----------
        - save_path (str): The path where the changes should be saved.
        - paragraphs (List[str]): The list of paragraphs that have been modified.
        """
        pythoncom.CoUninitialize()
        word = ReadWord(self.word_path)
        
        save_folder = save_folder or self.default_path + '.documents/'
        save_folder = os.path.abspath(save_folder)
        save_path = self.change_file_path(self.word_path, folder=save_folder)
                
        for index, paragraph in enumerate(word.paragraphs):
            paragraph.text = paragraphs[index]
                
        word.save(save_path)

    def clear(self) -> None:
        """
        Clears the internal state of the DocumentManager class. \n
        Temporary Word and PDF files are removed from the disk including the extracted images.
        """                
        try:
            os.remove(self.word_path)
        except:
            pass
        finally:
            self.word_path = ''

        try:
            os.remove(self.pdf_path)
        except:
            pass
        finally:
            self.pdf_path = ''
            
        for image in self.images_paths:
            try:
                os.remove(image)
            except:
                pass
        self.images_paths = []
