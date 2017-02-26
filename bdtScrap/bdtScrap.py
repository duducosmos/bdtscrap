#!/usr/bin/env python
# -*- Coding: UTF-8 -*-

_author = "Eduardo S. Pereira"
_date = "23/02/2017"

import re
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import Tag
import requests
import codecs


"""
Copyright (c) 2016, Big Data Tec
All rights reserved.
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

    Neither the name of the Big Data Tec nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Bibliografy
# https://tuhrig.de/extracting-meaningful-content-from-raw-html/


class BdtScrap:

    def __init__(self, link=None, deep=0, minCaracter=140, html=None):
        """
        link: The news link
        deep: Number of parents considered to get the news
        html: a local file name
        minCaracter: The minimal of character by parent to consider as part of the news.
        """

        self.minCaracter = minCaracter

        header = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0', }

        self.html = html

        if(html is not None):
            with open(html, 'r') as htf:
                self.html = ' '.join(list(htf.readlines()))

        if(html is None and link is not None):
            r = requests.get(
                link, headers=header)

            try:
                soup = BeautifulSoup(r.content,  'html.parser')
                encod = self.get_encoding(soup)
                print("Page encode %s" % encod)
                r.encoding = encod
            except:
                r.encoding = 'utf-8'
            self.html = r.content

        self.meaningfulText = None

        #self.html = toUnicode(self.html)

        try:
            self.soup = BeautifulSoup(self.html,  'html.parser')
        except:
            raise NameError("html parser problem")

        self.socialImage = self.get_sociaImage(self.soup)

        self._first_clean()

        self.NEGATIVE = re.compile(
            ".*comment.*|.*meta.*|.*footer.*|.*foot.*|.*cloud.*|.*head.*|.*hide.*|.*nav.*")
        self.POSITIVE = re.compile(
            ".*post.*|.*hentry.*|.*entry.*|.*content.*|.*text.*|.*body.*|.*news.*|.*News.*|.*article.*")
        self.soup = self._topParent(deep=deep)

        self._finalResult(deep=deep, minCaracter=minCaracter)

    def get_encoding(self, soup):
        encod = soup.meta.get('charset')
        if encod == None:
            encod = soup.meta.get('content-type')
            if encod == None:
                content = soup.meta.get('content')
                match = re.search('charset=(.*)', content)
                if match:
                    encod = match.group(1)
                else:
                    raise ValueError('unable to find encoding')
        return encod

    def get_sociaImage(self, soup):
        imageLink = soup.find('meta', property="og:image")['content']
        return imageLink

    def _finalResult(self, deep, minCaracter):

        if(deep > 0):
            self._second_clean()

        self.meaningfulText = self.soup.get_text(" ")
        self.meaningfulText = self.meaningfulText.split("\n")
        n = len(self.meaningfulText)
        #tmp = []

        # tmp = [self.meaningfulText[i] for i in range(0, n - 3)
        #       if(self.meaningfulText[i + 3].isspace() is False)
        #       ]
        # tmp += [self.meaningfulText[i] for i in range(n - 3, n)
        #        if (self.meaningfulText[i].isspace() is False)]

        tmp = filter(lambda x: x.isspace() is False and len(x)
                     > minCaracter, self.meaningfulText)

        self.meaningfulText = '\n'.join(tmp)

    def _first_clean(self):
        [s.extract()
         for s in self.soup(['style', 'script', '[document]', 'head', 'title',
                             'code', 'link'])]

    def getMeaningfulText(self):
        return self.meaningfulText

    def _topParent(self, tag="p", deep=0):
        tParent = None
        parents = []

        for paragraph in self.soup.findAll(tag):

            parent = paragraph.parent

            if (parent not in parents):
                parents.append(parent)
                parent.score = 0

                if (parent.has_attr("class")):
                    if (self.NEGATIVE.match(str(parent["class"]))):
                        parent.score -= 50
                    elif (self.POSITIVE.match(str(parent["class"]))):

                        parent.score += 25

                if (parent.has_attr("id")):
                    if (self.NEGATIVE.match(str(parent["id"]))):
                        parent.score -= 50
                    elif (self.POSITIVE.match(str(parent["id"]))):
                        parent.score += 25

            if (len(paragraph.renderContents()) > self.minCaracter):
                if(parent.score == None):
                    parent.score = 0
                parent.score += 15

        tParent = max(parents, key=lambda x: x.score)
        if(deep == 2):
            parents.remove(tParent)
            if(len(parents) > 0):
                tParent2 = max(parents, key=lambda x: x.score)
                newHTML = '<html>' + tParent.prettify() + \
                    tParent2.prettify() + '</html>'
                tParent = BeautifulSoup(newHTML,  'html.parser')
        return tParent

    def _second_clean(self):
        self._delete_by_min_size(self.soup, "td", 10, 2)
        self._delete_by_min_size(self.soup, "tr", 10, 2)
        self._delete_by_min_size(self.soup, "div", 10, 2)
        self._delete_by_min_size(self.soup, "table", 10, 2)
        self._delete_by_min_size(self.soup, "p", 50, 2)

    def _delete_by_min_size(self, soup, tag, length, children):
        [p.extract() for p in soup.findAll(tag)
         if((len(p.text) < length) and (len(p) <= children))
         ]


if(__name__ == "__main__"):
    #"http://www.jb.com.br/heloisa-tolipan/noticias/2017/02/22/" +
    #"saia-justa-volta-com-novo-elenco-no-dia-internacional-da-mulher/"

    #"https://corporate.canaltech.com.br/noticia/samsung/" +
    #"mercado-preve-alta-de-40-no-lucro-da-samsung-no" +
    #"-1o-trimestre-de-2017-89684/"

    #"https://canaltech.com.br/dica/apps/kayak-planeje-sua-viagem-agora-dicadeapp/"

    #"http://oglobo.globo.com/brasil/" +
    #"acao-da-pf-contra-roubo-de-carga-em-goias-df-mira-51-alvos-20962742"

    # "http://oglobo.globo.com/economia/"+
    #"vale-reverte-prejuizo-tem-lucro-liquido-de-133-bilhoes-em-2016-20967908"

    #"http://www.jb.com.br/ciencia-e-tecnologia/noticias/2017/02/22/" +
    #"nasa-descobre-tres-planetas-em" +
    #"-zona-habitavel-de-estrela-proxima-a-terra/"

    import time
    t1 = time.time()
    obj = BdtScrap(
        "http://gizmodo.uol.com.br/iphone-7-plus-explodiu-eua/",
        deep=2)

    print("Total time %s" % (time.time() - t1))
    print obj.meaningfulText
