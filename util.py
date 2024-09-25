import os


def create_file(file_path, headers=None, overwrite=False):
    if overwrite or (not os.path.exists(file_path)):
        with open(file_path, 'w') as file:
            if headers:
                file.write(headers)


def create_folder_if_not_exist(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
