from typing import Dict

import numpy as np
from PIL import Image
import random
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt

import sys

sys.path.append('RiksdagenPythonAPI/')
import riksdagen

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val

def do_cloud(id: int, text: str, parti: riksdagen.Parti):

    mask_filename = f'{parti.name}.png'
    mask = np.array(Image.open(f'mask/{mask_filename}'))
    # Transform your mask into a new one that will work with the function:
    transformed_mask = np.ndarray((mask.shape[0], mask.shape[1]), np.int32)

    for i in range(len(mask)):
        transformed_mask[i] = list(map(transform_format, mask[i]))

    wordcloud = WordCloud(max_font_size=30, background_color="white", mask=transformed_mask).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    #plt.show()

    filename = f'{parti.name}_wordcloud_{id}.png'
    wordcloud.to_file(f'pics/{filename}')


def get_party_words(api, parti: riksdagen.Parti, size: int):

    anforande_lista = api.get_anforande(parti=parti.name, anftyp='Nej', antal=size)
    print(f'Anföranden {parti.name}: {len(anforande_lista)}')

    word_sum = ""
    for anförande in anforande_lista:
        clean = re.sub("[!#?.,()/]", "", anförande.avsnittsrubrik)
        word_sum += clean + ' '  # full uncleaned string

    return word_sum

def prepare(api, size):
    full_text = {}
    usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
    for p in riksdagen.Parti:
        full_text = get_party_words(api, p, size)
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

    rel_usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
    for p in riksdagen.Parti:
        rel_usage[p] = {}
        for k, v in usage[p].items():
            rel_usage[p][k] = v / mean_usage[k]

    return rel_usage

def print_party_common_words (relative_usage, length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    for position in range(length):
        print(f'{position+1}. {sort[position]}, {relative_usage[sort[position]]:.0f} % mer än snittet')

def test_data():
    text = ''
    for i in range(300):
        for j in range(random.randint(2, 9)):
            text += random.choice(["a", "b", "c", "d", "e", "f"])
        text += ' '
    return text


def create_fake_text(relative_usage: Dict[str, float], length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    big_string = ''
    for position in range(length): # best to worst
        copies = 1#int(relative_usage[sort[position]] * 10)
        for cp in range(copies):
            big_string += sort[position] + ' '

    return big_string




api = riksdagen.API()
relative_usage = prepare(api, 500)

# parti = riksdagen.Parti.M
# print_party_common_words(relative_usage[parti], 15)

for parti in riksdagen.Parti:
    full_text = create_fake_text(relative_usage[parti], 70)
    for i in range(5):
        do_cloud(i, full_text, parti)
