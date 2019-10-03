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

# combine_extractive_summaries(book_id)
#
# combines the extractive summaries into a single text file to be analyzed
def combine_extractive_summaries(book_id):
    chapter = 0
    chapter_filename = '../results/extractive_summaries/' + \
        str(book_id) + '-' + str(chapter) + '.txt'
    combined_filename = '../results/extractive_summaries/' + \
        str(book_id) + '.txt'
    path = pathlib.Path(chapter_filename)
    combined_summary = open(combined_filename, 'w')
    while path.exists():
        summary = open(chapter_filename, 'r')
        for s in summary:
            combined_summary.write(s)
        summary.close()
        chapter += 1
        chapter_filename = '../results/extractive_summaries/' + \
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
    if not os.path.exists('../results/extractive_summaries'):
        os.makedirs('../results/extractive_summaries')
    chapter_filename = '../data/book_chapters/' + \
        str(book_id) + '-' + str(chapter) + '.txt'
    parser = PlaintextParser.from_file(chapter_filename, Tokenizer("english"))
    summary = summarizer(parser.document, size)
    file = '../results/extractive_summaries/' + \
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
