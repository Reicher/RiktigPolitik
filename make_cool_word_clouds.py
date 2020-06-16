from typing import Dict

import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt

import sys

sys.path.append('RiksdagenPythonAPI/')
import riksdagen


def do_word_cloud(text: Dict[riksdagen.Parti, str]):

    clouds = []
    fig = plt.figure(figsize=(4, 2))

    # ax enables access to manipulate each of subplots
    ax = []
    columns = 4
    rows = 2
    for p in riksdagen.Parti:
        ax.append(fig.add_subplot(rows, columns, p.value + 1))
        word_cloud = WordCloud(max_font_size=40).generate(text[p])
        #ax[-1].set_title()  # set title
        plt.imshow(word_cloud,  interpolation="bilinear")
        plt.axis("off")

    plt.show()


def get_party_words(api, parti: riksdagen.Parti):

    common_words = {}
    anforande_lista = api.get_anforande(rm='2019/20', parti=parti.name, anftyp='Nej')

    word_sum = ""
    for anförande in anforande_lista:
        word_sum += anförande.avsnittsrubrik  # full uncleaned string
    word_list = word_sum.split(" ")

    for word in word_list:
        clean_word = word.lower()
        if clean_word in common_words:
            common_words[clean_word] += 1
        else:
            common_words[clean_word] = 1

    return common_words, word_sum


api = riksdagen.API()

full_text = {}
for p in riksdagen.Parti:
    #occurence, full_text[riksdagen.Parti.V] = get_party_words(api, riksdagen.Parti.V)
    occurence, full_text[p] = get_party_words(api, p)

do_word_cloud(full_text)

# do_word_cloud("The wealth of those societies in which the capitalist mode of production prevails, presents itself as "
#              "an “immense accumulation of commodities”, its unit being a single commodity. "
#              "(Translation by Samuel Moore and Edward Aveling, supervised by Friedrich Engels (Marx 1867/1965, 35))")
