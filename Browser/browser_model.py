import os
import pathlib

class BrowerModel():
    def __init__(self):
        self.base_folder = os.path.abspath(".")
        self.base_svg_folder = os.path.join(self.base_folder, "mixList")

    def get_file_list(self):
        """return the list of saved file in the svg folder"""
        list_dir = os.listdir(self.base_svg_folder)
        files = [f for f in list_dir if pathlib.Path(f).suffix == ".json"]
        return files

    def get_path(self, file_name):
        """return full path of a file from the given file_name"""
        return os.path.join(self.base_svg_folder, file_name)