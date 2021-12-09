# Libraries for text preprocessing
import re
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
from wordcloud import WordCloud
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
#nltk.download('wordnet')
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas
import sectionDevision
import colorByGroup


def plotWordCloud(keywordFreq, title, color_to_words, default_color, font, width, height, background, mask):
    # del keywordFreq["word"]
    # del keywordFreq["key"]
    # del keywordFreq["paper"]
    # del keywordFreq["data"]
    wordcloud = WordCloud(
    font_path=font,
    width= width, height=height,
    max_words=100,
    background_color=background,
    mask = mask,
    #max_font_size=50,
    #random_state=42
    ).generate_from_frequencies(keywordFreq)

    # Create a color function with multiple tones
    grouped_color_func = colorByGroup.GroupedColorFunc(color_to_words, default_color)

    wordcloud.recolor(color_func=grouped_color_func)

    fig = plt.figure(figsize=(20,10), facecolor='k')
    #plt.title(title)
    plt.imshow(wordcloud)
    plt.tight_layout(pad=0)
    plt.axis('off')
    plt.show()
    fig.savefig(f"figures/{title}.png", facecolor="k", bbox_inches = "tight")



#Most frequently occuring words
def get_top_n_words(corpus, stop_words, n=None):
    vec = CountVectorizer(max_df=0.8,stop_words=stop_words, max_features=10000, ngram_range=(1,1)).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in
                   vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1],
                       reverse=True)
    return words_freq[:n]

#Most frequently occuring Bi-grams
def get_top_n2_words(corpus, n=None):
    vec1 = CountVectorizer(ngram_range=(2,2),
            max_features=2000).fit(corpus)
    bag_of_words = vec1.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in
                  vec1.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1],
                reverse=True)
    return words_freq[:n]

#Most frequently occuring Tri-grams
def get_top_n3_words(corpus, n=None):
    vec1 = CountVectorizer(ngram_range=(3,3),
           max_features=2000).fit(corpus)
    bag_of_words = vec1.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in
                  vec1.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1],
                reverse=True)
    return words_freq[:n]


def RAKEBERT(sectionalContent):

    ##Creating a list of stop words and adding custom stopwords
    stop_words = set(stopwords.words("english"))
    corpus = []
    thesisCorpus = ""
    for k, v in sectionalContent.items():

        # Remove the url
        urlR = "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)";
        text = re.sub(urlR, ' ', v)

        urlR = "http?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)";
        text = re.sub(urlR, ' ', v)


        #Remove punctuations
        text = re.sub('[^a-zA-Z]', ' ', v)

        #Convert to lowercase
        text = text.lower()

        #remove tags
        text=re.sub("&lt;/?.*?&gt;"," &lt;&gt; ",text)

        # remove special characters and digits
        text=re.sub("(\\d|\\W)+"," ",text)

        ##Convert to list from string
        text = text.split()

        ##Stemming
        #ps=PorterStemmer()
        #Lemmatisation
        lem = WordNetLemmatizer()
        text = [lem.lemmatize(word) for word in text if not word in
                stop_words]
        text = " ".join(text)
        if k == "abstract" or k == "title":
            thesisCorpus+= text
        corpus.append(text)

    # Get top 30 1-gram word, top 30 2-gram word, and top 20 3-gram word
    top_words = get_top_n_words(corpus, stop_words, n=30)
    top2_words = get_top_n2_words(corpus, n=30)
    top3_words = get_top_n3_words(corpus, n=20)
    # Convert most freq words to dataframe for plotting bar plot
    top_df = pandas.DataFrame(top_words).append(pandas.DataFrame(top2_words)).append(pandas.DataFrame(top3_words))

    top_df.columns=["Word", "Freq"]
    #Barplot of most freq words
    sns.set(rc={'figure.figsize':(13,8)})
    g = sns.barplot(x="Word", y="Freq", data=top_df)
    g.set_xticklabels(g.get_xticklabels(), rotation=30)
    fig = g.get_figure()
    fig.savefig("output.png")
    return top_df, thesisCorpus



# if __name__ == "__main__":
#     color_to_words = {}
#     color_to_words["yellow"] = []
#     input = "targetFolder/APIScanner.pdf"
#     stop_words = set(stopwords.words("english"))
#     sectionalContent = sectionDevision.sectionDevider(input)
#     top_words, thesisCorpus = RAKEBERT(sectionalContent)
#     data = top_words.set_index('Word').to_dict()['Freq']
#     for word,value in data.items():
#         if word in thesisCorpus:
#             data[word] = value*2
#             color_to_words["yellow"].append(word)
#     plotWordCloud(data, sectionalContent["title"],stop_words, color_to_words, "green")