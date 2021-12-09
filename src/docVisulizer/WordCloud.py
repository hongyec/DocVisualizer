import numpy as np
import itertools
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import colorByGroup as colorByGroup
import random
import json

def plotWordCloud(keywords, title, stop_words, color_to_words, default_color):
    wordcloud = WordCloud(
    background_color='white',
    stopwords=stop_words,
    max_words=100,
    max_font_size=50,
    random_state=42
    ).generate(" ".join(keywords))

    # Create a color function with multiple tones
    grouped_color_func = colorByGroup.GroupedColorFunc(color_to_words, default_color)

    wordcloud.recolor(color_func=grouped_color_func)

    fig = plt.figure(0)
    plt.title(title)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.show()
    fig.savefig(f"figures/{title}.png",dpi=900)

def max_sum_sim(doc_embedding, candidate_embeddings, candidates, top_n, nr_candidates):
    # Calculate distances and extract keywords
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    distances_candidates = cosine_similarity(candidate_embeddings,
                                            candidate_embeddings)

    # Get top_n words as candidates based on cosine similarity
    words_idx = list(distances.argsort()[0][-nr_candidates:])
    words_vals = [candidates[index] for index in words_idx]
    distances_candidates = distances_candidates[np.ix_(words_idx, words_idx)]

    # Calculate the combination of words that are the least similar to each other
    min_sim = np.inf
    candidate = None
    for combination in itertools.combinations(range(len(words_idx)), top_n):
        sim = sum([distances_candidates[i][j] for i in combination for j in combination if i != j])
        if sim < min_sim:
            candidate = combination
            min_sim = sim

    return [words_vals[idx] for idx in candidate]

def mmr(doc_embedding, word_embeddings, words, top_n, diversity):
    # Extract similarity within words, and between words and the document
    word_doc_similarity = cosine_similarity(word_embeddings, doc_embedding)
    word_similarity = cosine_similarity(word_embeddings)

    # Initialize candidates and already choose best keyword/keyphras
    keywords_idx = [np.argmax(word_doc_similarity)]
    candidates_idx = [i for i in range(len(words)) if i != keywords_idx[0]]

    for _ in range(top_n - 1):
        # Extract similarities within candidates and
        # between candidates and selected keywords/phrases
        candidate_similarities = word_doc_similarity[candidates_idx, :]
        target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

        # Calculate MMR
        mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
        mmr_idx = candidates_idx[np.argmax(mmr)]

        # Update keywords & candidates
        keywords_idx.append(mmr_idx)
        candidates_idx.remove(mmr_idx)

    return [words[idx] for idx in keywords_idx]

def keywordCloud(sectionalContent):
    n_gram_range = (1, 3)
    stop_words = "english"

    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

    color_to_words = {}
    keywords = []
    for k, v in sectionalContent.items():
        if k == "title":
            continue
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        sectionalCount = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([v])
        sectionalCandidates = sectionalCount.get_feature_names_out()
        sectionalCandidate_embeddings = model.encode(sectionalCandidates)
        sectionalDoc_embedding = model.encode([sectionalContent])
        sectionalKeywords = mmr(sectionalDoc_embedding, sectionalCandidate_embeddings, sectionalCandidates, top_n=10, diversity=0.2)
        sectionalKeywords = [word.replace(" ", "_") for word in sectionalKeywords]
        color_to_words[color] = sectionalKeywords
    print(color_to_words)
    with open("responseCache/ColorToWord.json", "w") as f:
        json.dump(color_to_words, f, indent=4)

    # Extract candidate words/phrases
    count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([str(sectionalContent)])
    candidates = count.get_feature_names_out()

    doc_embedding = model.encode([sectionalContent])
    candidate_embeddings = model.encode(candidates)
    keywords = mmr(doc_embedding, candidate_embeddings, candidates, top_n=100, diversity=0.2)
    keywords = [word.replace(" ", "_") for word in keywords]

    plotWordCloud(keywords, sectionalContent["title"], stop_words, color_to_words, "red")
