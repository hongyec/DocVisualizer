import WordCloud
import sectionDevision
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")

    arguments = parser.parse_args()
    input = arguments.input
    sectionalContent = sectionDevision.sectionDevider(input)
    WordCloud.keywordCloud(sectionalContent)

if __name__ == '__main__':
    main()
