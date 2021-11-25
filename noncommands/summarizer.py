from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
import pandas as pd
import nltk
import re
import numpy as np
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from trafilatura import bare_extraction
import trafilatura
import discord

nltk.download('punkt')
nltk.download('stopwords')

def scoreSent(sent, scoreMatrix, scoreCol):
    score = 0
    for word in sent.split(" "):
        #print(word)
        if word in scoreMatrix.index:
            filt = scoreMatrix.filter(items=[word], axis='index')
            score += filt[scoreCol].values[0]
            #print("WORD:", word, "Score:", scoreMatrix.iloc[i][scoreCol])
            #print("VALUE", filt["abs_topic1"].values[0])
    #print(score)
    return score/len(sent)


def filterStopwords(sent):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(sent)

    return " ".join([w for w in word_tokens if w not in stop_words])

def getSummarySpread(filePath, numSent):
    
    f = open(filePath, "r")
    text = f.read()
    #text = text.replace("\n", " ").replace("\t", " ")
    text = " ".join(text.split())

    for i in range(100):
        text = text.replace("[" + str(i) + "]", "")
    
    doc = nltk.tokenize.sent_tokenize(text)
    #print(doc[0])
    docFilt = [filterStopwords(s) for s in doc]
    #print(docFilt[0])
    vectorizer = CountVectorizer()
    bag_of_words = vectorizer.fit_transform(docFilt)

    svd = TruncatedSVD(n_components = numSent)
    lsa = svd.fit_transform(bag_of_words)

    col = ["topic" + str(i) for i in range(numSent)]

    absCol = ["abs_topic" + str(i) for i in range(numSent)]

    topic_encoded_df = pd.DataFrame(lsa, columns=col)
    topic_encoded_df["docFilt"] = docFilt
    topic_encoded_df["doc"] = doc
    #display(topic_encoded_df.sort_values("topic1"))
    # for c in col:
    #     print(topic_encoded_df.sort_values(c).iloc[-1]["doc"])
    dictionary = vectorizer.get_feature_names_out()
    encoding_matrix=pd.DataFrame(svd.components_,index=col,columns=dictionary).T

    for i in range(numSent):
        encoding_matrix[absCol[i]] = np.abs(encoding_matrix[col[i]])

    #final_matrix = encoding_matrix.sort_values('abs_topic2', ascending=False)
    #display(final_matrix)
    #print(scoreSent("rock", final_matrix, 'abs_topic0'))

    cl = dict()
    for c in absCol:
        cl[c] = []


    for c in absCol:
        for s in doc:
            cl[c].append([s, scoreSent(s, encoding_matrix, c)])
    chosen = []
    for c in absCol:
        s = [d for d in sorted(cl[c], key=lambda x: x[1]) if d[0] not in [f[0] for f in chosen]][::-1]
        chosen.append(s[0])

    for i in chosen:
        print(i[0])

    #print(final_matrix)
    #sentence1= final_matrix[final_matrix["abs_topic2"]>=0.1]
    #print(sentence1[['abs_topic2']])


def getSummaryMono(text, numSent):

    text = " ".join(text.split())

    for i in range(100):
        text = text.replace("[" + str(i) + "]", "")
    
    doc = nltk.tokenize.sent_tokenize(text)

    docFilt = [filterStopwords(s) for s in doc]

    vectorizer = CountVectorizer()
    bag_of_words = vectorizer.fit_transform(docFilt)

    svd = TruncatedSVD(n_components = 1)
    lsa = svd.fit_transform(bag_of_words)

    col = ["topic1"]

    absCol = ["abs_topic1"]

    topic_encoded_df = pd.DataFrame(lsa, columns=col)
    topic_encoded_df["docFilt"] = docFilt
    topic_encoded_df["doc"] = doc

    dictionary = vectorizer.get_feature_names_out()
    encoding_matrix=pd.DataFrame(svd.components_,index=col,columns=dictionary).T

    for i in range(len(col)):
        encoding_matrix[absCol[i]] = np.abs(encoding_matrix[col[i]])

    cl = dict()
    for c in absCol:
        cl[c] = []

    for c in absCol:
        for s in doc:
            cl[c].append([s, scoreSent(s, encoding_matrix, c)])
    chosen = []
    
    for i in range(numSent):
        for c in absCol:
            s = [d for d in sorted(cl[c], key=lambda x: x[1]) if d[0] not in [f[0] for f in chosen]][::-1]
            chosen.append(s[0])

    return [i[0] for i in chosen]


def getSummary(config, url):
    numSent = 5
    downloaded = trafilatura.fetch_url(url)
    article = bare_extraction(downloaded)
    embed = discord.Embed(
        color=config["success"]
    )
    embed.add_field(
        name = "Title:",
        value = article["title"],
        inline = True
    )
    embed.add_field(
        name="Summary:",
        value="\n".join(getSummaryMono(article["text"], numSent)),
        inline = True
    )

    return embed