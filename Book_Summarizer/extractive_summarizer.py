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
import pathlib
import pandas as pd

# divide_book_into_chapters(book_id)
#
# divides the book file into separate chapter files
# book file is in the data/books folder
# chapter files are saved in the data/book_chapters folder
# assumes chapter breaks occur when there are two empty lines in a row
# makes chapters at least 20 lines long
# as there are often two double spaces at the start of a chapter
# limits chapters to the end of the next paragraph after 3000 lines


def divide_book_into_chapters(book_id):
    book_filename = '../data/books/' + str(book_id) + '.txt'
    chapter_filename = '../data/book_chapters/' + str(book_id) + '-'
    count_chapters = 0
    count_lines_in_chapter = 0
    previous_blank_line = False
    book = open(book_filename, 'r', encoding='latin-1')
    book_chapter = open(chapter_filename + str(count_chapters) + '.txt', 'w')
    for l in book:
        if (count_lines_in_chapter < 3000) and ((len(l) > 1) or (count_lines_in_chapter < 20)):
            previous_blank_line = False
            count_lines_in_chapter += 1
            book_chapter.write(l)
        elif (len(l) == 1) and ((previous_blank_line == True) or (count_lines_in_chapter > 3000)):
            count_lines_in_chapter = 0
            count_chapters += 1
            book_chapter.close()
            book_chapter = open(chapter_filename +
                                str(count_chapters) + '.txt', 'w')
        elif (len(l) == 1):
            count_lines_in_chapter += 1
            previous_blank_line = True
            book_chapter.write(l)
        else:
            count_lines_in_chapter += 1
            book_chapter.write(l)
    book_chapter.close()
    book.close()


# calls analyze_summary for each of the summaries to analyze
# def analyze_summaries():


# analyze the summary using ROUGE and cosine similarity
# def analyze_summary():


# create_extractive_summary_chapter(book_id, chapter, summarizer, size)
#
# create an extractive summary for a chapter of the book
# book_id is the project gutenberg identifier
# chapter is the chapter number to summarize
# (refers to file break down, may not actually be that chapter in the book)
# summarizer is the sumy summarizer that will create the summary
def create_extractive_summary_chapter(book_id, chapter, summarizer, size):
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


# create_extractive_summary_book(book_id, summarizer, size)
#
# iterates through chapters of book that have already been saved in the book_chapters folder
# calling create_extractive_summary_segment
# to put together a complete extractive summary of the book
def create_extractive_summary_book(book_id, summarizer, size):
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


# for all books listed in data_stats.csv
# divide into chapters and save in book_chapters folder
df = pd.read_csv("data_stats.csv", sep=',', header=None)
for index, row in df.iterrows():
    pg_index = row[1]
    divide_book_into_chapters(pg_index)

# for all books listed in data_stats.csv
# create extractive summary using sumy standard summarizer
# (Luhn, TextRank, Lsa, LexRank)
# summarizer = TextRankSummarizer()
# summarizer = LsaSummarizer()
# summarizer = LexRankSummarizer()
df = pd.read_csv("data_stats.csv", sep=',', header=None)
summarizer = LuhnSummarizer()
for index, row in df.iterrows():
    pg_index = row[1]
    print(pg_index)
    create_extractive_summary_book(pg_index, summarizer, 3)
