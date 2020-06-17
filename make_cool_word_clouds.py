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
        plt.imshow(word_cloud,  interpolation="bilinear")
        plt.axis("off")

    plt.show()


def get_party_words(api, parti: riksdagen.Parti):

    anforande_lista = api.get_anforande(rm='2019/20', parti=parti.name, anftyp='Nej')

    word_sum = ""
    for anförande in anforande_lista:
        word_sum += anförande.avsnittsrubrik + ' '  # full uncleaned string

    return word_sum

def print_party_common_words (relative_usage, length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    for position in range(length):
        print(f'{position+1}. {sort[position]}, {relative_usage[sort[position]]:2f} % mer än snittet')

def test_data(parti):
    text = {riksdagen.Parti.V:  "Ett Två Tre Tre",
            riksdagen.Parti.C:  "Ett Två Tre Fyra",
            riksdagen.Parti.KD: "Ett Två Tre",
            riksdagen.Parti.M:  "Ett Två Tre",
            riksdagen.Parti.L:  "Ett Två Tre",
            riksdagen.Parti.SD: "Ett Två Tre",
            riksdagen.Parti.MP: "Ett Två Tre",
            riksdagen.Parti.S:  "Ett Två Tre"}
    return text[p]

api = riksdagen.API()

full_text = {}
#full_text[riksdagen.Parti.V] = get_party_words(api, riksdagen.Parti.V)
usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
for p in riksdagen.Parti:
    full_text = get_party_words(api, p)
    #full_text = test_data(p)
    words = [w.lower() for w in full_text.split(' ')]
    usage[p] = {}
    for word in words:
        if word in usage[p]:
            usage[p][word] += 1
        else:
            usage[p][word] = 1

    for k, v in usage[p].items():
        usage[p][k] = 100 * (v / len(words))

mean_usage: Dict[str, float] = {}
for p in riksdagen.Parti:
    for k, v in usage[p].items():
        if usage[p][k] in mean_usage:
            mean_usage[k] += v / 8
        else:
            mean_usage[k] = v / 8

relative_usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
for p in riksdagen.Parti:
    relative_usage[p] = {}
    for k, v in usage[p].items():
        relative_usage[p][k] = v / mean_usage[k]

print_party_common_words(relative_usage[riksdagen.Parti.SD], 15)

#do_word_cloud(full_text)

# do_word_cloud("The wealth of those societies in which the capitalist mode of production prevails, presents itself as "
#              "an “immense accumulation of commodities”, its unit being a single commodity. "
#              "(Translation by Samuel Moore and Edward Aveling, supervised by Friedrich Engels (Marx 1867/1965, 35))")
