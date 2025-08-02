import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Union, TextIO, Optional

class FileHandler:
    def __init__(self, file_path: str, file_obj: Optional[TextIO] = None):
        self.file_path = file_path
        self.file_obj = file_obj
        self.modified = False
        self.content = []
        
        if self.file_obj:
            self.content = self.file_obj.readlines()

class Moudle:
    class new:
        @staticmethod
        def file(filename: str, directory: str = '.'):
            """创建新文件"""
            full_path = Path(directory) / filename
            try:
                with open(full_path, 'w'):
                    pass
            except Exception as e:
                raise Exception(f"无法创建文件: {e}")

        @staticmethod
        def dir(dirname: str, directory: str = '.'):
            """创建新目录"""
            full_path = Path(directory) / dirname
            try:
                os.makedirs(full_path, exist_ok=True)
            except Exception as e:
                raise Exception(f"无法创建目录: {e}")

    @staticmethod
    def open(filename: str, file_handler: FileHandler, directory: str = '.') -> FileHandler:
        """打开文件"""
        full_path = Path(directory) / filename
        try:
            file_obj = open(full_path, 'r+')
            return FileHandler(str(full_path), file_obj)
        except Exception as e:
            raise Exception(f"无法打开文件: {e}")

    @staticmethod
    def write(content: str, line: int, file_handler: FileHandler):
        """写入内容到指定行"""
        if line < 1 or line > len(file_handler.content) + 1:
            raise ValueError("行号超出范围")
        
        if line == len(file_handler.content) + 1:
            # 追加到末尾
            file_handler.content.append(content + '\n')
        else:
            # 插入到指定行
            file_handler.content[line-1] = file_handler.content[line-1].rstrip() + content + '\n'
        
        file_handler.modified = True

    @staticmethod
    def save(file_handler: FileHandler):
        """保存更改到文件"""
        if not file_handler.modified:
            return
            
        try:
            with open(file_handler.file_path, 'w') as f:
                f.writelines(file_handler.content)
            file_handler.modified = False
        except Exception as e:
            raise Exception(f"保存文件失败: {e}")

    @staticmethod
    def close(file_handler: FileHandler):
        """关闭文件"""
        if file_handler.file_obj and not file_handler.file_obj.closed:
            file_handler.file_obj.close()

    class look:
        @staticmethod
        def dir(file_handler: FileHandler) -> FileHandler:
            """打开目录选择对话框"""
            root = tk.Tk()
            root.withdraw()
            dir_path = filedialog.askdirectory()
            if dir_path:
                file_handler.file_path = dir_path
            return file_handler

        @staticmethod
        def file(file_handler: FileHandler) -> FileHandler:
            """打开文件选择对话框"""
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename()
            if file_path:
                file_handler.file_path = file_path
                try:
                    file_handler.file_obj = open(file_path, 'r+')
                    file_handler.content = file_handler.file_obj.readlines()
                except Exception as e:
                    raise Exception(f"无法打开文件: {e}")
            return file_handler

    # 支持 with 语句的上下文管理器
    @staticmethod
    def Open(filename: str, directory: str = '.'):
        """支持 with 语句的文件打开方式"""
        return MoudleContextManager(filename, directory)

class MoudleContextManager:
    def __init__(self, filename: str, directory: str = '.'):
        self.filename = filename
        self.directory = directory
        self.file_handler = None

    def __enter__(self):
        self.file_handler = Moudle.open(self.filename, FileHandler(self.filename), self.directory)
        return self.file_handler

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_handler:
            if self.file_handler.modified:
                Moudle.save(self.file_handler)
            Moudle.close(self.file_handler)