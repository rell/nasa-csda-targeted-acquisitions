from os import path, mkdir
from json import dump


def write_output(output_file, output_folder, data):
    if path.exists(output_folder):
        dump(data, open(output_file, "w"), indent=2)
    else:
        mkdir(output_folder)
        dump(data, open(output_file, "w"), indent=2)