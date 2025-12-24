import os
import shutil

def clean_destination(source_name, destination_name):
    if os.path.exists(destination_name):
        shutil.rmtree(destination_name)
    os.mkdir(destination_name)
    repeat_copy(source_name, destination_name)





def repeat_copy(source_name, destination_name):
    for item in os.listdir(source_name):
        source_path = os.path.join(source_name, item)
        destination_path = os.path.join(destination_name, item)
        if os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
        else:
            os.mkdir(destination_path)
            repeat_copy(source_path, destination_path)