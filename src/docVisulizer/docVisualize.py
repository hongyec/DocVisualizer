from os import lseek
import sectionDevision
import argparse
import RAKEBERT
import WordCloud
import numpy as np
from PIL import Image
import pdfkit
#config = pdfkit.configuration(wkhtmltopdf="/Users/hongyechen/opt/miniconda3/lib/python3.9/site-packages/wkhtmltopdf")
def transform_format(val):
    if val == 0:
        return 255
    else:
        return val

def main():
    parser = argparse.ArgumentParser(description='Metadata of research paper help researchers quickly classify cate-gories, identify contents, and organize resources. Meanwhile, visu-alization of metadata can reinforce the benefit. Nevertheless, manyexisting research website failed to visualize their meta-data prop-erly. To address this absence of the visualization, we propose apipeline and a toolVisoothat could produce meaningful metadatavisualization based on the existing paper. Visoo is a python scriptthat could extract the structural metadata from existing paper andproduce a word cloud based on the frequency and the position ofthe word. We tested our tool based on several existing researchsources online. Demo of Visoo: https://github.com/hongyec/Visoo')
    parser.add_argument("-i", "--input", help="The Target file you want to parse")
    parser.add_argument("-f", "--font", help = "The font that word cloud will use. The default will be 'Cotton Butter'")
    parser.add_argument("-a", "--algorithm", help = "The algorithm you want to use. The options are 'BERT' and 'RAKE'")
    parser.add_argument("-k", "--keycolor", help = "The color for the words that is in abstract and title, the default color will be 'yellow'")
    parser.add_argument("-d", "--defaultcolor", help = "The color for the words that is in the rest of the article, the default will be 'green'")
    parser.add_argument("-w", "--width", help = "The width of your figure, the default will be 1600")
    parser.add_argument("-l", "--height", help = "The height of your figure, the default will be 800")
    parser.add_argument("-t", "--title", help = "Specify the title of the figure, the default will be the same as the target File")
    parser.add_argument("-b", "--background", help  = "background color for the word cloud")
    parser.add_argument("--image", help = "The image pattern of the word cloud")
    parser.add_argument("--website", action='store_true', help = "whether the input is a website" )

    arguments = parser.parse_args()
    input = arguments.input
    keycolor = arguments.keycolor
    defaultcolor = arguments.defaultcolor
    font = arguments.font
    algorithm = arguments.algorithm
    width = arguments.width
    height = arguments.height
    title = arguments.title
    background = arguments.background
    image = arguments.image
    website = arguments.website

    if website:
        pdfkit.from_url(input, 'hello.pdf')
        input = 'hello'+'.pdf'

    # set up the default value for the user input
    keycolor = "yellow" if not keycolor else keycolor
    defaultcolor = "green" if not defaultcolor else defaultcolor
    font = "../font/Cotton_Butter.ttf" if not arguments.font else font
    algorithm = "RAKEBERT" if not algorithm else algorithm
    width = 1600 if not width else width
    height = 800 if not height else height
    background = "black" if not background else background
    mask = np.array(Image.open(image)) if image else None
    transformed_mask = None
    if image:
        transformed_mask = np.ndarray((mask.shape[0],mask.shape[1]), np.int32)

        for i in range(len(mask)):
            transformed_mask[i] = list(map(transform_format, mask[i]))

    sectionalContent = sectionDevision.sectionDevider(input)

    title = sectionalContent["title"] if not title else title

    # if the algorithm is BERT switch to BERT
    if (algorithm == "BERT"):
        WordCloud.keywordCloud(sectionalContent)
    # else use the combination of BERT and RAKE
    else:
        color_to_words = {}
        color_to_words[keycolor] = []
        sectionalContent = sectionDevision.sectionDevider(input)
        top_words, thesisCorpus = RAKEBERT.RAKEBERT(sectionalContent)
        data = top_words.set_index('Word').to_dict()['Freq']

        for word,value in data.items():
            # Assign the keycolor and more weight for the word that exist in the title or abstract
            if word in thesisCorpus:
                data[word] = value*2
                color_to_words[keycolor].append(word)
        RAKEBERT.plotWordCloud(data, title, color_to_words, defaultcolor, font, width, height, background, transformed_mask)

if __name__ == '__main__':
    main()
