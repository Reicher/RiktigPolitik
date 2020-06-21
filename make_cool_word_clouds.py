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


def do_cloud(id: int, text: str, num_anforanden: int, parti: riksdagen.Parti, debug=True):

    mask_filename = f'{parti.name}.png'
    mask = np.array(Image.open(f'mask/{mask_filename}'))
    # Transform your mask into a new one that will work with the function:
    transformed_mask = np.ndarray((mask.shape[0], mask.shape[1]), np.int32)

    for i in range(len(mask)):
        transformed_mask[i] = list(map(transform_format, mask[i]))

    wordcloud = WordCloud(max_font_size=40, min_font_size=3, background_color="white", mask=transformed_mask).generate(text)

    if debug:
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        logging.info(f'Showed plot.')
        plt.show()
    else:
        filename = f'{parti.name}_wordcloud_{id}.png'
        wordcloud.to_file(f'pics/draft/{filename}')
        logging.info(f'Saved file {filename}')

        add_text_information(parti, filename, len(text.split(" ")), num_anforanden)


def add_text_information(parti: riksdagen.Parti,
                         filename: str,
                         word_count: int,
                         speeches: int):
    # post processing

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
    source = f'Sammanställning av {speeches} anförande-rubriker av {parti.name} sedan riksmötet 1993/94\n' \
             f'De 75 ord {parti.name} använder betydligt mer än övriga partier.'
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


def get_party_words(api, parti: riksdagen.Parti, size: int):

    rms = riksdagen.riksmoten

    anforande_lista = []
    for rm in rms:
        anforande_lista += api.get_anforande(rm=rm, parti=parti.name, anftyp='Nej', antal=size)
    print(f'Anföranden {parti.name}: {len(anforande_lista)}')

    word_sum = ''
    for anförande in anforande_lista:
        if anförande.avsnittsrubrik is not None:
            clean = re.sub("[!#?.,()/]", "", anförande.avsnittsrubrik)
            word_sum += clean + ' '  # full uncleaned string

    print(f'Ord {parti.name}: {len(word_sum.split(" "))}')
    return word_sum, len(anforande_lista)

def prepare(api, size):
    usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
    num_a : Dict[riksdagen.Parti, int] = {}
    for p in riksdagen.Parti:
        text, num_a[p] = get_party_words(api, p, size)
        words = [w.lower() for w in text.split(' ')]
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

    return rel_usage, num_a

def print_party_common_words (relative_usage, length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    for position in range(length):
        print(f'{position+1}. {sort[position]}, {relative_usage[sort[position]]:.0f} % mer än snittet')

def create_fake_text(relative_usage: Dict[str, float], length):
    sort = sorted(relative_usage, key=relative_usage.get, reverse=True)
    big_string = ''
    for position in range(length): # best to worst
        copies = 1#int(relative_usage[sort[position]] * 10)
        for cp in range(copies):
            big_string += sort[position] + ' '

    return big_string


logging.basicConfig(filename='logs/last.log')
api = riksdagen.API()
#usage: Dict[riksdagen.Parti, Dict[str, float]] = {}
#text, num_a = get_party_words(api, 200)
relative_usage, num_anforande = prepare(api, 10)

# parti = riksdagen.Parti.M
# print_party_common_words(relative_usage[parti], 15)

for parti in [riksdagen.Parti.V]: # riksdagen.Parti: #
    clouds = 3
    logging.info(f'Creating {clouds} clouds for {parti}.')
    full_text = create_fake_text(relative_usage[parti], 75)
    #print_party_common_words(relative_usage[parti], 10)
    for i in range(clouds):
        do_cloud(i, full_text, num_anforande[parti], parti, debug=False)
