# coding: utf-8
import re
import urlparse
import requests
import functions_files
from urlparse import urlparse
__author__ = 'alicia'
import cookielib
import urllib2
from lxml import html
from lxml.html.clean import Cleaner
import sys
reload(sys)
sys.setdefaultencoding('utf8')
class Documento(object):
    def __init__(self, directory_data):
        self.directory_data = directory_data
        self.dir_output_name = 'default_dir_urls'
        self.urls = []
        self.get_urls()
        self.get_documents()

    def get_urls(self):
        for line in open(self.directory_data, 'r'):
            self.urls.append(line)


    def get_documents(self):
        "Obtencion del codigo HTML"
        self.dir_output_name = self.get_dir_name(self.urls[0])
        functions_files.create_dir_if_not_exists(self.dir_output_name)
        count_name_files = 0
        if len(self.urls) == 1:
            count_loop = 0
            while len(self.urls) < 21:
                self.add_crawled_urls(self.urls[count_loop])
                count_loop += 1
                if count_loop == 10:
                    break

        for url in self.urls:
            count_name_files += 1
            file_name = str(count_name_files) # calculo el nombre del archivo

            cookiejar= cookielib.LWPCookieJar()
            opener= urllib2.build_opener( urllib2.HTTPCookieProcessor(cookiejar) )
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            page = html.fromstring(opener.open(url).read()) # html de la página

            cleaner = Cleaner()
            cleaner.javascript = True # This is True because we want to activate the javascript filter
            cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter

            page_sin_javascript = cleaner.clean_html(html.fromstring(opener.open(url).read())) # html de la página

            # Podría utilizar esto para obtener el nombre del archivo... pero no.
            title = ''
            for atag in page.xpath('//title'):
                title += atag.text_content() + " "
            title = ' '.join(title.split())
            title = title.encode('utf-8')

            meta_description = ''
            for atag in page.xpath('//meta[@name="description"]/@content'):
                meta_description += atag + " "
            meta_description = ' '.join(meta_description.split())
            meta_description = meta_description.encode('utf-8')

            body_content = ''
            for atag in page_sin_javascript.xpath('//body'):
                body_content += atag.text_content() + " "
            body_content = ' '.join(body_content.split())
            body_content = body_content.encode('utf-8')

            file_write = self.dir_output_name + '/' + file_name + '.txt'
            with open(file_write, "a") as myfile:
                myfile.write('ABSTRACT' + "\n")
                myfile.write(title + ' ' + meta_description + "\n")
                myfile.write('1. INTRODUCTION' + "\n")
                myfile.write(body_content)

    def get_dir_name(self, url):
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        print domain
        return domain.replace('.', '')

    def add_crawled_urls(self, url_seed):
        cookiejar = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        page = html.fromstring(opener.open(url_seed).read()) # html de la página
        for atag in page.xpath('//a/@href'):
            regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            existe = regex.match(atag)
            if not existe:
                # no es válida...
                print "Encuentro URL '" + atag + "' pero NO está bien formada"
            else:
                #suponemos que si es buena. Pero sólo quiero los enlaces hacia el mismo dominio.
                dominio_del_enlace = self.get_dir_name(atag)
                if dominio_del_enlace == self.dir_output_name:
                    self.urls.append(atag)
                    with open(self.directory_data, "a") as myfile:
                        myfile.write(atag + "\n")
            if len(self.urls) > 21:
                break