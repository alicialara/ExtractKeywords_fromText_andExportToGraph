# coding: utf-8
import pickle
from pprint import pprint
import re
import itertools
import unicodedata
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import RegexpTokenizer
import matplotlib.pyplot as plt
import networkx as nx
from nltk.util import ngrams
import functions_files

__author__ = 'alicia'


class SimpleTextRank(object):
    def __init__(self):
        """
        Clase para la extraccin de palabras clave. Devuelve un Count con las palabras obtenidas
        :param window: int - Valor de ventana (palabras que coge antes y despus)
        :param archivo: string - Archivo seleccionado. False para coger todos los archivos disponibles
        """
        self.select_tagged_file = True
        self.file_selected = False
        self.select_tagged_file = False
        self.dir_with_data = 'contags'
        self.window = '5'
        self.language = 'E'
        self.jar = 'C:\stanford-postagger-full-2016-10-31\stanford-postagger.jar'
        # model = 'C:\stanford-postagger-full-2016-10-31\models\english-bidirectional-distsim.tagger'
        self.model = 'C:\stanford-postagger-full-2016-10-31\models\english-caseless-left3words-distsim.tagger'
        self.model = 'C:\stanford-postagger-full-2016-10-31\models\spanish-distsim.tagger'
        # variables auxiliares
        self.ngrams_window = {0: 1, 1: 3, 2: 5, 3: 7, 4: 9, 5: 11}
        # if not tagged -> 2 sections : abstract + content
        # else 1 section -> content
        self.texts_not_tagged_abstract = {}
        self.texts_not_tagged_content = {}
        self.texts_tagged_abstract = {}
        self.texts_tagged_content = {}
        self.texts_filtered_abstract = {}
        self.texts_filtered_content = {}

    def execute(self):
        use_abstract = True
        if self.select_tagged_file:
            use_abstract = False

        self.get_data_from_files()
        self.filter_tags_texts(use_abstract)

        with open('objs.pickle', 'w') as f:  # Python 3: open(..., 'wb')
            pickle.dump([self.texts_not_tagged_abstract, self.texts_not_tagged_content, self.texts_tagged_abstract,
                         self.texts_tagged_content, self.texts_filtered_abstract, self.texts_filtered_content], f)

        # with open('objs.pickle') as f:  # Python 3: open(..., 'rb')
        #     self.texts_not_tagged_abstract, self.texts_not_tagged_content, self.texts_tagged_abstract, self.texts_tagged_content, self.texts_filtered_abstract, self.texts_filtered_content = pickle.load(
        #         f)
        self.keywords_extraction(use_abstract)

    def keywords_extraction(self, abstract):

        if abstract:
            loop_tagged_attributes = {'CONTENT': self.texts_filtered_content,
                                      'ABSTRACT': self.texts_filtered_abstract}
        else:
            loop_tagged_attributes = {'CONTENT': self.texts_filtered_content}
        for name, item in loop_tagged_attributes.iteritems():
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name)
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/keyphrases')
            functions_files.create_dir_if_not_exists(
                self.dir_with_data + '/' + name + '/keyphrases/ventana_' + str(self.window))
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/calculated_textrank')
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/grafos_sin_pesos')
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/grafos_sin_pesos/capturas')
            functions_files.create_dir_if_not_exists(
                self.dir_with_data + '/' + name + '/grafos_sin_pesos/capturas/ventana_' + str(self.window))
            functions_files.create_dir_if_not_exists(
                self.dir_with_data + '/' + name + '/grafos_sin_pesos/ventana_' + str(self.window))
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/grafos_con_pesos')
            functions_files.create_dir_if_not_exists(self.dir_with_data + '/' + name + '/grafos_con_pesos/capturas')
            functions_files.create_dir_if_not_exists(
                self.dir_with_data + '/' + name + '/grafos_con_pesos/capturas/ventana_' + str(self.window))
            functions_files.create_dir_if_not_exists(
                self.dir_with_data + '/' + name + '/grafos_con_pesos/ventana_' + str(self.window))

            for file_name, array_ in item.iteritems():
                words = []  # array con las palabras de cada archivo ya filtradas
                for word in array_:
                    words.append(word)
                words = [x.lower() for x in words]

                # word_set_list = list(grams_list)
                unique_word_set = self.unique_everseen(words)
                word_set_list = list(unique_word_set)
                # pprint(word_set_list[:10])

                graph = self.create_graph(words, word_set_list)

                calculated_page_rank = nx.pagerank(graph,
                                                   weight='weight')  # cálculo de textRank con pesos (los pesos están en graph)

                self.save_textrank_results(calculated_page_rank, name, file_name)

                keywords = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
                keywords = keywords[0:((len(word_set_list) / 3) + 1)]
                # pprint(keywords)

                selected_keywords = self.select_keywords_windowed(words, keywords)
                # pprint(selected_keywords)

                # ya tengo las palabras clave, asi que ahora puedo construir al grafo teniendo en cuenta la ventana
                # recorro todas las palabras del texto (words), y resalto las que aparecen como palabras clave

                # Cuando acabe, creo el grafo con las palabras obtenidas que co-ocurren en el texto
                # sabiendo que cada union de palabras es una arista entre los vertices (palabras)

                file_name_ = file_name.replace(".txt", "")
                file_name_ = file_name_.replace(".txt.final", "")
                file_name_ = file_name_.replace(".txt.tagged", "")

                graph_windowed = self.create_graph_windowed(selected_keywords, False)

                self.paint_graph(graph_windowed,
                                 self.dir_with_data + '/' + name + '/grafos_sin_pesos/capturas/ventana_' + str(
                                     self.window) + '/' + file_name_ + '.png', False)
                nx.write_pajek(graph_windowed, self.dir_with_data + '/' + name + '/grafos_sin_pesos/ventana_' + str(
                    self.window) + '/' + file_name_ + '.net')

                functions_files.replace(self.dir_with_data + '/' + name + '/grafos_sin_pesos/ventana_' + str(
                    self.window) + '/' + file_name_ + '.net', '0.0 0.0 ellipse', '')

                graph_windowed = self.create_graph_windowed(selected_keywords, True)

                self.paint_graph(graph_windowed,
                                 self.dir_with_data + '/' + name + '/grafos_con_pesos/capturas/ventana_' + str(
                                     self.window) + '/' + file_name_ + '.png', False)
                nx.write_pajek(graph_windowed, self.dir_with_data + '/' + name + '/grafos_con_pesos/ventana_' + str(
                    self.window) + '/' + file_name_ + '.net')

                functions_files.replace(self.dir_with_data + '/' + name + '/grafos_con_pesos/ventana_' + str(
                    self.window) + '/' + file_name_ + '.net', '0.0 0.0 ellipse', '')

                self.save_keywords(selected_keywords, name, file_name_)

    def unique_everseen(self, iterable, key=None):
        """List unique elements, preserving order. Remember all elements ever seen."""
        # unique_everseen('AAAABBBCCDAABBB') --> A B C D
        # unique_everseen('ABBCcAD', str.lower) --> A B C D
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in itertools.ifilterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        else:
            for element in key:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element

    def create_graph(self, words, word_set_list):
        # creo un grafo como explica el paper, teniendo en cuenta el valor de ventana.
        # si divido words en n-gramas, siendo n la ventana, obtengo la lista de palabras que comparar. Por ejemplo:
        # si ventana = 2, words = [A, B, C, D, E, B, G] y keywords = [B, C, G]
        # obtengo los bigramas AB, BC, CD, DE, EB, BG.
        # De ahi selecciono los que existen en keywords y los anado: [BC, BG].
        # Para anadirlos, separo las palabras por un espacio: B + " " + G
        # * Si ventana = 3, hago primero ventana=2 y luego ventana=3
        print "Ngrams (window) selected: " + str(self.window)
        grams_ = ngrams(words, self.window)
        # grams_ = ngrams(words, 2)
        grams_ = list(grams_)
        graph = nx.Graph()
        array_valores = {}
        for i, val in enumerate(grams_):
            ant = 0
            for k in range(1, self.window):
                # print "Anado " + str(val[ant]) + " - " + str(val[k]) +
                # " con posiciones en : " + str(ant) + " - " + str(k)
                key = val[ant] + '/' + val[k]
                if key in array_valores:
                    array_valores[key] += 1
                else:
                    array_valores[key] = 1
                ant += 1
        # pprint(array_valores)
        for key, value in array_valores.items():
            clave = key.split("/")
            graph.add_edge(clave[0], clave[1], weight=value)

        return graph

    def select_keywords_windowed(self, words, keywords):
        # si divido words en n-gramas, siendo n la ventana, obtengo la lista de palabras que comparar. Por ejemplo:
        # si ventana = 2, words = [A, B, C, D, E, B, G] y keywords = [B, C, G]
        # obtengo los bigramas AB, BC, CD, DE, EB, BG.
        # De ahi selecciono los que existen en keywords y los anado: [BC, BG].
        # Para anadirlos, separo las palabras por un espacio: B + " " + G
        selected_keywords = []
        grams_ = ngrams(words, self.window)
        grams_ = list(grams_)
        for i, val in enumerate(grams_):
            keywords_aux = []
            aux = True
            for k in range(self.window):
                keywords_aux.append(val[k])
                if val[k] not in keywords:
                    aux = False
            if aux:
                new_keyword = " ".join(keywords_aux)
                selected_keywords.append(new_keyword)

        return selected_keywords

    def create_graph_windowed(self, selected_keywords, conPesos):
        # creo un grafo como explica el paper (figura 2), teniendo en cuenta el valor de ventana.

        graph = nx.Graph()
        array_valores = {}
        for val in selected_keywords:
            keywords = val.split(" ")
            ant = 0
            for i in range(1, len(keywords)):
                key = keywords[ant] + '/' + keywords[i]
                if key in array_valores:
                    array_valores[key] += 1
                else:
                    array_valores[key] = 1
                ant += 1
        for key, value in array_valores.items():
            clave = key.split("/")
            graph.add_edge(clave[0], clave[1], weight=value)
        return graph

    def paint_graph(self, graph, name, weighted=True):
        print(
        "graph %s has %d nodes with %d edges" % (graph.name, nx.number_of_nodes(graph), nx.number_of_edges(graph)))

        if weighted:
            elarge = [(u, v) for (u, v, d) in graph.edges(data=True) if d['weight'] > 2]
            esmall = [(u, v) for (u, v, d) in graph.edges(data=True) if d['weight'] <= 2]
        else:
            elarge = None
            esmall = None

        pos = nx.spring_layout(graph)  # positions for all nodes
        # nodes
        nx.draw_networkx_nodes(graph, pos, node_size=100)

        # edges
        nx.draw_networkx_edges(graph, pos, edgelist=elarge,
                               width=1)
        nx.draw_networkx_edges(graph, pos, edgelist=esmall,
                               width=1, alpha=1, edge_color='b', style='dashed')

        # labels
        nx.draw_networkx_labels(graph, pos, font_size=6, font_family='sans-serif')

        plt.axis('off')
        plt.savefig(name)  # save as png

    def save_keywords(self, keywords, name, file):

        file_write = self.dir_with_data + '/' + name + '/keyphrases/ventana_' + str(
            self.window) + '/' + file + '.txt.result'
        for word in keywords:
            with open(file_write, "a") as myfile:
                myfile.write(str(word) + "\n")

    def save_textrank_results(self, calculated_textrank, name, file):

        file_write = self.dir_with_data + '/' + name + '/calculated_textrank/' + '/' + file + '.textrank'
        for word, value in calculated_textrank.iteritems():
            with open(file_write, "a") as myfile:
                myfile.write(str(word) + " -> " + str(value) + "\n")


            # <editor-fold desc="Preprocesado">

    def get_data_from_files(self):
        directory_data = self.dir_with_data
        if self.file_selected:
            dirs = [self.file_selected]  # si quiero obtener los datos sólo para 1 archivo
        else:
            dirs = functions_files.read_dir("./" + directory_data)
        start_selection = False
        start_abstract = False
        # regex = re.compile('[^a-zA-Z]')
        for file in dirs:
            print ("Comienzo con el archivo... " + file)
            text = ''
            text_abstract = ''
            ruta = './' + directory_data + '/' + file
            if self.select_tagged_file:
                for line in open(ruta, 'r'):
                    fila = line.rstrip()
                    text += fila + ' '
                self.texts_tagged_content[file] = text
            else:
                print ("Empezando de leer el texto... ")
                for line in open(ruta, 'r'):
                    fila = line.rstrip()  # strip off newline and any other trailing whitespace
                    # tengo que coger desde la linea "ABSTRACT" hasta la linea "REFERENCES"
                    if fila.find('REFERENCES') != -1:
                        break
                    if start_abstract and not start_selection:
                        text_abstract += fila + ' '
                    if start_selection:
                        # primero elimino basura
                        # texto = re.sub(r'\([^)]*\)', '', fila)
                        # texto = re.sub(r'\([^\(]*?\)', r'', texto)
                        # texto = regex.sub(' ', texto)
                        text += fila + ' '
                    if (fila.find('ABSTRACT') != -1) and (start_abstract == False):
                        start_abstract = True
                    if (fila.find('1. INTRODUCTION') != -1) and (start_selection == False):
                        start_selection = True
                print ("Terminando de leer el texto... ")
                text = text.replace("ABSTRACT", "").replace('1. INTRODUCTION', "")
                text_abstract = text_abstract.replace("ABSTRACT", "").replace('1. INTRODUCTION', "").replace('<s>', "")

                if self.language == 'S':
                    text = self.elimina_tildes(text)
                    text_abstract = self.elimina_tildes(text_abstract)
                else:
                    text = text.decode('utf-8').encode('ascii', errors='ignore')
                    text_abstract = text_abstract.decode('utf-8').encode('ascii', errors='ignore')

                self.texts_not_tagged_content[file] = text
                self.texts_not_tagged_abstract[file] = text_abstract

                # calculate tags
                print ("Calculando tags... ")
                self.texts_tagged_content[file] = self.calcula_tags(text)
                self.texts_tagged_abstract[file] = self.calcula_tags(text_abstract)

    def filter_tags_texts(self, abstract):
        if abstract:
            loop_tagged_attributes = {'texts_tagged_content': self.texts_tagged_content,
                                      'texts_tagged_abstract': self.texts_tagged_abstract}
        else:
            loop_tagged_attributes = {'texts_tagged_content': self.texts_tagged_content}
        for name, item in loop_tagged_attributes.iteritems():
            for file, text in item.iteritems():
                # tengo que convertirlo en array y filtrar los datos que me interesan (nombres y adjetivos)
                data = []
                miarray = text.split(" ")
                for palabra in miarray:
                    if palabra != '' and palabra != '<s>' and palabra != '<f>':
                        aux = palabra.split("/")
                        # print file + " " + palabra
                        if (aux[1] == 'NN') or (aux[1] == 'NNS') or (aux[1] == 'JJ') or (aux[1] == 'JJR') or (
                                    aux[1] == 'JJS') or (aux[1] == 'ao0000') or (aux[1] == 'aq0000') or (
                                    aux[1] == 'nc00000') or (aux[1] == 'nc0n000') or (aux[1] == 'nc0p000') or (
                                    aux[1] == 'nc0s000') or (aux[1] == 'np00000'):
                            # entonces es buena
                            # a partir de ahora no me sirve pos POS TAGS (porque ya estn filtradas)
                            palabra = palabra.replace("/JJR", "").replace("/JJS", "").replace("/NNS", "") \
                                .replace("/JJ", "").replace("/NN", "").replace("/ao0000", "").replace("/aq0000",
                                                                                                      "").replace(
                                "/nc00000", "").replace("/nc0n000", "").replace("/nc0p000", "").replace("/nc0s000",
                                                                                                        "").replace(
                                "/np00000", "")
                            data.append(palabra)
                if name == 'texts_tagged_content':
                    self.texts_filtered_content[file] = data
                else:
                    self.texts_filtered_abstract[file] = data
        return True

    def calcula_tags(self, token):
        self.model = 'C:\stanford-postagger-full-2016-10-31\models\english-caseless-left3words-distsim.tagger'
        if self.language == 'S':
            self.model = 'C:\stanford-postagger-full-2016-10-31\models\spanish-distsim.tagger'

        # token = token.decode('utf-8')
        token = self.cleanhtml(token)
        token = re.sub(r'\([^)]*\)', '', token)  # elimino paréntesis y su contenido
        tokenizer = RegexpTokenizer(r'\w+')
        token = tokenizer.tokenize(token)
        token = token[:500]
        tags = StanfordPOSTagger(self.model, path_to_jar=self.jar, encoding='utf8').tag(token)
        text_tagged = ''
        for item in tags:
            text_tagged += item[0] + '/' + item[1] + ' '

        return text_tagged
        # token = string.decode('utf-8')
        # token = nltk.word_tokenize(token)
        # tags =  nltk.pos_tag(token)
        # return tags

    @staticmethod
    def filter_tags(tags):
        final_words = []
        for i in tags:
            word = i[0]
            tag = i[1]
            if tag == 'ao0000' or tag == 'aq0000' or tag == 'nc00000' or tag == 'nc0n000' or tag == 'nc0p000' or tag == 'nc0s000' or tag == 'np00000':
                final_words.append(word)
        return final_words

    @staticmethod
    def cleanhtml(raw_html):
        # return BeautifulSoup(raw_html).text
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def elimina_tildes(s):
        s = s.decode('utf-8')
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

# </editor-fold>
