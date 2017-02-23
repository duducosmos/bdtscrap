#!/usr/bin/env python
# -*- Coding: UTF-8 -*-

_author = "Eduardo S. Pereira"
_date = "23/02/2017"

import re
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import Tag
import urllib


"""
Based on Arc90 Readability algorithm.
Source: https://tuhrig.de/extracting-meaningful-content-from-raw-html/
http://nirmalpatel.com/fcgi/hn.py
"""


class BdtScrap:

    def __init__(self, link=None, deep=0, html=None):

        html = html

        if(html is not None):
            with open(html, 'r') as htf:
                html = ' '.join(list(htf.readlines()))

        if(html is None and link is not None):
            html = urllib.urlopen(link).read()

        self.meaningfulText = None

        try:
            self.soup = BeautifulSoup(html,  'html.parser')
        except:
            raise NameError("html parser problem")

        self._first_clean()

        self.NEGATIVE = re.compile(
            ".*comment.*|.*meta.*|.*footer.*|.*foot.*|.*cloud.*|.*head.*|.*hide.*")
        self.POSITIVE = re.compile(
            ".*post.*|.*hentry.*|.*entry.*|.*content.*|.*text.*|.*body.*")
        self.soup = self._topParent()

        if(deep == 0):
            self.meaningfulText = self.soup.get_text(" ")
            self.meaningfulText = self.meaningfulText.split("\n")
            n = len(self.meaningfulText)
            tmp = [self.meaningfulText[i] for i in range(0, n - 2)
                   if self.meaningfulText[i].isspace() is False
                   ]
            tmp += [self.meaningfulText[i] for i in range(n - 2, n)
                    if ((self.meaningfulText[i].isspace() is False)
                        and (self.meaningfulText[i - 2].isspace() is False)
                        )]
            self.meaningfulText = '\n'.join(tmp)

        if(deep == 1):
            self._second_clean()
            self.meaningfulText = self.soup.get_text(" ")
            self.meaningfulText = self.meaningfulText.split("\n")
            n = len(self.meaningfulText)
            tmp = [self.meaningfulText[i] for i in range(0, n - 2)
                   if self.meaningfulText[i].isspace() is False
                   ]
            tmp += [self.meaningfulText[i] for i in range(n - 2, n)
                    if ((self.meaningfulText[i].isspace() is False)
                        and (self.meaningfulText[i - 2].isspace() is False)
                        )]
            self.meaningfulText = '\n'.join(tmp)

        if(deep > 1):
            self._second_clean()
            self.meaningfulText = self.soup.get_text(" ")
            self.meaningfulText = self.meaningfulText.split("\n")
            n = len(self.meaningfulText)
            tmp = [self.meaningfulText[i] for i in range(0, n - 2)
                   if((self.meaningfulText[i].isspace() is False)
                      and (self.meaningfulText[i + 2].isspace() is False)
                      )
                   ]
            tmp += [self.meaningfulText[i] for i in range(n - 2, n)
                    if ((self.meaningfulText[i].isspace() is False)
                        and (self.meaningfulText[i - 2].isspace() is False)
                        )]
            self.meaningfulText = '\n'.join(tmp)

    def _first_clean(self):
        [s.extract()
         for s in self.soup(['style', 'script', '[document]', 'head', 'title',
                             'code', 'link'])]

    def getMeaningfulText(self):
        return self.meaningfulText

    def _topParent(self):
        tParent = None
        parents = []
        for paragraph in self.soup.findAll("p"):

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

            if (len(paragraph.renderContents()) > 10):
                parent.score += 1

            # you can add more rules here!

        tParent = max(parents, key=lambda x: x.score)
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
        "http://www.bbc.com/portuguese/geral-39053134",
        deep=1)

    print("Total time %s" % (time.time() - t1))
    print obj.meaningfulText
