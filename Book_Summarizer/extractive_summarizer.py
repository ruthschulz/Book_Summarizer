# extractive summarizer
# create an extractive summary from chapters of a large document

import shutil
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.models import TfDocumentModel
from sumy.evaluation import cosine_similarity
from sumy.evaluation import rouge_n, rouge_l_sentence_level, rouge_l_summary_level
import pathlib
import pandas as pd
import csv

from data_download_and_stats import get_text_filename, get_chapter_filename, get_clean_book_filename

# analyze_summary(book_id)
#
# analyze the summary using ROUGE n score and cosine similarity
def analyze_summary(book_id):
    combined_filename = '../data/combined_summaries/' + \
        str(book_id) + '.txt'
    summary_filename = '../data/summaries/' + \
        str(book_id) + '.txt'
    parser_s = PlaintextParser.from_file(
        summary_filename, Tokenizer("english"))
    parser_e = PlaintextParser.from_file(
        combined_filename, Tokenizer("english"))
    summary_s = parser_s.document.sentences
    summary_e = parser_e.document.sentences
    rouge_n_score = rouge_n(summary_s, summary_e)
    model1 = TfDocumentModel(str(summary_s), Tokenizer("en"))
    model2 = TfDocumentModel(str(summary_e), Tokenizer("en"))
    cosine_sim_score = cosine_similarity(model1, model2)
    return [rouge_n_score, cosine_sim_score]


# combine_extractive_summaries(book_id)
#
# combines the extractive summaries into a single text file to be analyzed
def combine_extractive_summaries(book_id):
    chapter = 0
    chapter_filename = '../data/extractive_summaries/' + \
        str(book_id) + '-' + str(chapter) + '.txt'
    combined_filename = '../data/extractive_summaries/' + \
        str(book_id) + '.txt'
    path = pathlib.Path(chapter_filename)
    combined_summary = open(combined_filename, 'w')
    while path.exists():
        summary = open(chapter_filename, 'r')
        for s in summary:
            combined_summary.write(s)
        summary.close()
        chapter += 1
        chapter_filename = '../data/extractive_summaries/' + \
            str(book_id) + '-' + str(chapter) + '.txt'
        path = pathlib.Path(chapter_filename)
    combined_summary.close()


# create_extractive_summary_chapter(book_id, chapter, summarizer, size)
#
# create an extractive summary for a chapter of the book
# book_id is the project gutenberg identifier
# chapter is the chapter number to summarize
# (refers to file break down, may not actually be that chapter in the book)
# summarizer is the sumy summarizer that will create the summary
def create_extractive_summary_chapter(book_id, chapter, summarizer, size):
    if not os.path.exists('../data/extractive_summaries'):
        os.makedirs('../data/extractive_summaries')
    chapter_filename = '../data/book_chapters/' + \
        str(book_id) + '-' + str(chapter) + '.txt'
    parser = PlaintextParser.from_file(chapter_filename, Tokenizer("english"))
    summary = summarizer(parser.document, size)
    file = '../data/extractive_summaries/' + \
        str(book_id) + '-' + str(chapter) + '.txt'
    with open(file, 'w') as f:
        for sentence in summary:
            f.write(str(sentence) + '\n')
    f.close()


# create_extractive_summary_chapter(book_id, chapter, summarizer, size)
#
# create an extractive summary for a chapter of the book
# book_id is the project gutenberg identifier
# chapter is the chapter number to summarize
# (refers to file break down, may not actually be that chapter in the book)
# summarizer is the sumy summarizer that will create the summary
def find_relevant_quote(book_id, chapter):
    chapter_filename = get_chapter_filename(book_id, chapter)
    parser = PlaintextParser.from_file(chapter_filename, Tokenizer("english"))
    summarizer = LuhnSummarizer()
    summary = summarizer(parser.document, 1)
    return summary


# create_extractive_summary_book(book_id, summarizer, size)
#
# iterates through chapters of book that have already been saved in the book_chapters folder
# calling create_extractive_summary_segment
# to put together a complete extractive summary of the book
def create_extractive_summary_book(book_id, size, summarizer=LuhnSummarizer()):
    chapter_filename = '../data/book_chapters/' + \
        str(book_id) + '-' + str(0) + '.txt'
    path = pathlib.Path(chapter_filename)
    chapter = 0
    while path.exists():
        create_extractive_summary_chapter(book_id, chapter, summarizer, size)
        chapter += 1
        chapter_filename = '../data/book_chapters/' + \
            str(book_id) + '-' + str(chapter) + '.txt'
        path = pathlib.Path(chapter_filename)
    combine_extractive_summaries(book_id)

# for all books listed in data_stats.csv
# create extractive summary using sumy standard summarizer Luhn
def test_create_luhn_extractive_summaries():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    summarizer = LuhnSummarizer()
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        create_extractive_summary_book(pg_index, 3, summarizer)


# for all books listed in data_stats.csv
# create extractive summary using sumy standard summarizer LSA
def test_create_lsa_extractive_summaries():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    summarizer = LsaSummarizer()
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        create_extractive_summary_book(pg_index, 3, summarizer)


# for all books listed in data_stats.csv
# create extractive summary using sumy standard summarizer TextRank
def test_create_tr_extractive_summaries():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    summarizer = TextRankSummarizer()
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        create_extractive_summary_book(pg_index, 3, summarizer)


# for all books listed in data_stats.csv
# create extractive summary using sumy standard summarizer LexRank
def test_create_lr_extractive_summaries():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    summarizer = LexRankSummarizer()
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        create_extractive_summary_book(pg_index, 3, summarizer)


# for all books listed in data_stats.csv
# combine extractive summaries into one text file
def test_combine_extractive_summaries():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        combine_extractive_summaries(pg_index)


# for all combined summaries
# print analysis of the summary compared to the supplied summary
def test_analyze_summary():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    scores = []
    for index, row in df.iterrows():
        pg_index = row[1]
        print(pg_index)
        combined_filename = '../data/combined_summaries/' + \
            str(pg_index) + '.txt'
        path = pathlib.Path(combined_filename)
        if path.exists():
            scores.append(analyze_summary(pg_index))
            print(scores[-1])
    with open('combined_summary_scores.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(scores)
    csvFile.close()


# for one book, print analysis of the summary compared to the supplied summary
def test_analyze_summary1(book_id):
    print(analyze_summary(book_id))
