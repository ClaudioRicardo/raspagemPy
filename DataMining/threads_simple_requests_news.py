# -*- coding: utf-8 -*-
# author:Claudio Azevedo (claudioric.azevedo@gmail.com, claudwolf@hotmail.com)
'''
    Esse simples script coleta as notícias do dia no site G1
    A proposta aqui é bem simples.Considerando que os links dos sites de notícias
    de hoje em dia são organizados por categorias, datas e slugs (que geralmente são compostas pelo
    título da matéria em questão).Dá para intuir que podemos encontrar e filtrar as notícias que queremos
    checando os links contidos nas páginas.
'''

import requests, re, json
from threading import Thread
from bs4 import BeautifulSoup
from datetime import date


links_relevantes = []


def get_data(url):
    '''
        Função receberá uma url e com a ajuda do método get da bateria
        requests retornará um documento HTML ou uma mensagem de erro e um
        return False caso o status_code for diferente de 200.
        :param url:
        :return: result
    '''
    try:
        result = requests.get(url.strip())
        if result.status_code != 200:
            result = False
    except requests.exceptions.ConnectionError as r:
        print("ERROR: " + str(r))
        return False
    return result


def get_links(HTMLContext):
    '''
        Função pega todos os links de "noticias" da página
        :param HTMLContext:
        :return: links_noticias
    '''
    links_noticias = []

    if not HTMLContext == False:
        obj_dom = BeautifulSoup(HTMLContext.text, "html.parser")
        obj_dom.prettify()
        tags_a = obj_dom.findAll("a", href= re.compile(r"(/noticia/)"))
        if tags_a:
            for a in tags_a:
                #if "noticia" in a['href']:
                if a.text.strip() == "":
                    text = get_title(a['href'])
                else:
                    text = a.text.strip()

                links_noticias.append("{\"titulo\": \""+text+"\", \"url\":\""+a['href']+"\"}")

    return links_noticias


def get_title(url):
    '''
        Função entra na página em questão e pega o titulo
        :param url:
        :return: title
    '''
    #print(url)

    HTMLContext = get_data(url)
    obj_dom = BeautifulSoup(HTMLContext.text, "html.parser")
    obj_dom.prettify()
    title = obj_dom.find("h1", {"class": "content-head__title"})

    return title.text



def get_links_relevantes(links):
    '''
        Função vai filtrar os links relevantes.
        O critério de relevância nesse caso é a data atual
        :param links:
        :return: relevantes
    '''
    hoje = date.today()
    relevantes = []
    if links:

        for l in links:
            obj = json.loads(l)
            #print(obj)
            if hoje.strftime("%Y/%m/%d") in obj['url']:
                #title = get_title(l)
                relevantes.append(l)
    return relevantes


def get_next_page(HTMLContext):
    '''
    Função pega ao final de cada página ,no botão "Veja mais", o link de referência para a próxima página
    :param HTMLContext:
    :return: next
    '''
    next = False
    if not HTMLContext == False:
        obj_dom = BeautifulSoup(HTMLContext.text, "html.parser")
        obj_dom.prettify()
        div = obj_dom.find("div", {"class": "load-more"})
        if div:
            if div.a:
                next = div.a['href']
    return next


def thr_run(url):
    print("Thread: ",url)
    HTMLCntxt = get_data(url)
    l = get_links(HTMLCntxt)
    lr = get_links_relevantes(l)
    global links_relevantes
    links_relevantes = list(set(lr + links_relevantes))
    next = get_next_page(HTMLCntxt)

    while len(lr) > 0:
        HTMLCntxt = get_data(next)
        l = get_links(HTMLCntxt)
        lr = get_links_relevantes(l)
        links_relevantes = list(set(lr + links_relevantes))
        next = get_next_page(HTMLCntxt)

    for rel in links_relevantes:
        obj = json.loads(rel)

        print(obj,"\n")
        #print(obj['titulo'])
        #print(obj['url'])

    print(len(links_relevantes))



if __name__ == "__main__":
    urls = [
        "https://g1.globo.com/",
        "https://g1.globo.com/go/goias/",
        "https://g1.globo.com/df/distrito-federal/",
        "https://g1.globo.com/mt/mato-grosso/",
        "https://g1.globo.com/ms/mato-grosso-do-sul/",
        "https://g1.globo.com/rj/norte-fluminense/",
        "https://g1.globo.com/al/alagoas/"

    ]
    Arrthreads = []
    ind = 0
    for url in urls:
        Arrthreads.append(Thread(target=thr_run,args=[url]))
        Arrthreads[ind].start()
        ind+=1

        #thr_run(url)
