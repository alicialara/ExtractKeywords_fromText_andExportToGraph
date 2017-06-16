# coding: utf-8
import os
from Documento import Documento

os.environ['JAVA_HOME'] = "C:\Program Files\Java\jdk1.8.0_121"
# os.environ['JAVA_HOME'] = "C:\Program Files\Java\jdk1.7.0_79"

# from KeywordExtraction import KeywordExtraction
from SimpleTextRank import SimpleTextRank

print ("Starting...")
print ("Step 1 - Setting config...")


select_all_default = input("Select default values? (True/False): ")
if not select_all_default:
    language = raw_input("Select language (E english / S spanish): ")
    extract_from_url = input("Extract information from URL? (True/False): ")
    if extract_from_url:
        select_tagged_file = False
        file_selected = False
        print "If you want to extract the information from a list of URLs, " \
              "write the file name that contains that list:"
        file_path = raw_input("Input the path to de file: ")
    else:
        dir_with_data = raw_input("Input the path to the directory that contains the data: ")
        select_tagged_file = input("Select tagged file? (True/False): ")
        file_selected = raw_input("Add file ('False' selects all files): ")
        if file_selected == 'False':
            file_selected = False
    window = input("Add window number (values 1, ..., 5): ")
else:
    language = 'E'
    extract_from_url = False
    select_tagged_file = True
    file_selected = False
    dir_with_data = 'contags'
    file_path = False
    window = 5


# Ejemplo con una URL:
# file_path = 'seed_url_extraction.txt'
# language = 'S'
# extract_from_url = True
# select_tagged_file = False
# # file_selected = '1.txt'
# file_selected = False
# dir_with_data = 'wwwmuseodelpradoes'
# window = '2'

if extract_from_url:
    print ("Primer paso. Extracción de información a partir de URLs")
    print ("Fichero seleccionado: " + file_path)
    print ("Idioma de los documentos HTML: " + language)
    documentos = Documento(file_path)
    dir_with_data = documentos.dir_output_name

print ("Práctica Final v2.0: Uso de la clase SimpleTextRank")
# 'C-41.txt.final'
# keywords = SimpleTextRank(window, file_selected, select_tagged_file)
keywords = SimpleTextRank()
keywords.select_tagged_file = select_tagged_file
keywords.file_selected = file_selected
keywords.select_tagged_file = select_tagged_file
keywords.dir_with_data = dir_with_data
keywords.window = int(window)
keywords.language = language
keywords.execute()



