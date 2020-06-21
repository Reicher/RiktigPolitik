from typing import Dict
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont

import numpy as np
import random
import re
import logging
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

    wordcloud = WordCloud(max_font_size=40,
                          min_font_size=3,
                          collocations=False,
                          background_color="white",
                          mask=transformed_mask).generate(text)
    filename = f'{parti.name}_wordcloud_{id}.png'
    wordcloud.to_file(f'pics/draft/{filename}')
    logging.info(f'Saved file {filename}')

    return filename


def add_text_information(parti: riksdagen.Parti,
                         filename: str,
                         statistics: Dict[riksdagen.Parti, Dict[str, int]]):
    # create Image object with the input image
    image = Image.open(f'pics/draft/{filename}')
    w, h = image.size

    # initialise the drawing context with
    # the image object as background
    draw = ImageDraw.Draw(image)

    # create font object with the font file and specify
    # desired size
    # font = ImageFont.truetype('fonts/Roboto-Italic.ttf', size=17)

    color = 'rgb(0, 0, 0)'  # black color

    # Partiname
    font = ImageFont.truetype("fonts/Roboto-LightItalic.ttf", 45)
    source = f'{riksdagen.parti_namn[parti]}'
    text_w, text_h = draw.textsize(source, font)
    draw.text(((w - text_w) / 2, 65), source, color, font=font)

    # Förklaring
    font = ImageFont.truetype("fonts/Roboto-LightItalic.ttf", 17)
    source = f'Sammanställning av {statistics["ord"]} ord från {statistics["anföranden"]} anförande-rubriker av ' \
             f'{parti.name} sedan riksmötet 1993/94.\nDe 75 ord {parti.name} använder betydligt mer än övriga partier.'
    text_w, text_h = draw.textsize(source, font)
    draw.text(((w - text_w) / 2, (h-text_h)-30), source, color, font=font, align='center')

    font = ImageFont.truetype("fonts/Roboto-LightItalic.ttf", 15)
    # Fotnötter
    source = "Källa: Sveriges riksdag"
    text_w, text_h = draw.textsize(source, font)
    draw.text(((w - text_w)-10, (h - text_h * 2)-5), source, color, font=font)

    source = "Bearbetning: reicher@github"
    text_w, text_h = draw.textsize(source, font)
    draw.text(((w - text_w)-10, (h - text_h)-5), source, color, font=font)

    # save the edited image
    image.save(f'pics/draft/processed/{filename}')


def get_party_words(api, size: int):

    stats: Dict[riksdagen.Parti, Dict[str, int]] = {}
    text: Dict[riksdagen.Parti, str] = {}

    for parti in riksdagen.Parti:
        stats[parti] = {}
        anforande_lista = []
        for rm in [riksdagen.riksmoten[20]]:
            anforande_lista += api.get_anforande(rm=rm, parti=parti.name, anftyp='Nej', antal=size)
        stats[parti]['anföranden'] = len(anforande_lista)

        text[parti] = ''
        for anforande in anforande_lista:
            if anforande.avsnittsrubrik is not None:
                clean = re.sub("[!#?.,()/]", "", anforande.avsnittsrubrik)
                text[parti] += clean + ' '  # full uncleaned string

        stats[parti]['ord'] = len(text[parti].split(" "))
        print(f'Got {stats[parti]["ord"]} words from {stats[parti]["anföranden"]} '
              f'anföranden from {riksdagen.parti_namn[parti]}.')

    return text, stats


def prepare(text):
    usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
    for p in riksdagen.Parti:
        words = [w.lower() for w in text[p].split(' ')]
        usage[p] = {}
        for word in words:
            if word in usage[p]:
                usage[p][word] += 1
            elif word != '':
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


def create_fake_text(relative_usage: Dict[str, float], length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    big_string = ''
    for position in range(length):  # best to worst
        copies = int(relative_usage[sort[position]] * 2)
        for cp in range(copies):
            big_string += sort[position] + ' '

    return big_string


api = riksdagen.API()

text, statistics = get_party_words(api, 2000)
relative_usage = prepare(text)

for parti in [riksdagen.Parti.V]: # riksdagen.Parti: #
    clouds = 1
    logging.info(f'Creating {clouds} clouds for {parti}.')
    full_text = create_fake_text(relative_usage[parti], 60)
    #print_party_common_words(relative_usage[parti], 10)
    for i in range(clouds):
        filename = do_cloud(i, full_text, parti)
        add_text_information(parti, filename, statistics[parti])
        print(f'Created wordcloud {filename} for {riksdagen.parti_namn[parti]}')
