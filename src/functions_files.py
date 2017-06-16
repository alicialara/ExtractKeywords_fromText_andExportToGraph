__author__ = 'alicia'
import os
from tempfile import mkstemp
from shutil import move
from os import remove, close
def read_dir(path):
    print "Voy a leer todos los nombres de archivos dentro de la ruta --> " + path
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))
        print "path to all filenames."
        list = []
        for filename in filenames:
            list.append(os.path.join(filename))
        return filenames
    # for file in os.listdir(path):
    #     # if file.endswith(".txt"):
    #     print(os.path.join(path, file))

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def rename_extension_file(dir, old_pattern, new_pattern):
    for filename in os.listdir(dir):
        filename_ = filename.replace(old_pattern, new_pattern)
        os.rename(filename, filename_)