# abstractive summarizer
# create an abstractive summary from chapters of a large document

import re
import os
import sys
import shutil
import spacy
import pathlib
from extractive_summarizer import create_extractive_summary_book
from data_download_and_stats import get_chapter_filename, get_extractive_summary_filename, get_abstractive_summary_filename

def process_book(input_data):
    nlp = spacy.load('en_core_web_sm', disable=['tagger', 'ner'])
    article = input_data
    summary = 'summary'
    title = 'title'
    if article == None or summary == None or title == None:
        return ''
    article = nlp(article)
    summary = nlp(summary)
    title = nlp(title)
    sen_arr = []
    for sen in article.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        #sen = ['<s>']+sen+['</s>']
        sen = ' '.join(sen)
        sen_arr.append(sen)
    article = ' '.join(sen_arr)
    sen_arr = []
    for sen in summary.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        sen = ['<s>']+sen+['</s>']
        sen = ' '.join(sen)
        sen_arr.append(sen)
    summary = ' '.join(sen_arr)
    sen_arr = []
    for sen in title.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        sen = ['<s>']+sen+['</s>']
        sen = ' '.join(sen)
        sen_arr.append(sen)
    title = ' '.join(sen_arr)
    sen_arr = [title, summary, article]
    
    #return '<sec>'.join(sen_arr)
    return title + summary + '<sec>' + article


def process_file(file_in,file_out):
    # book may also be extractive summary
    book = open(file_in, 'rb')
    book_text = ''
    # remove special characters
    # make lower case
    for line in book:
        line = line.decode('utf-8').encode('ascii', 'ignore').decode('ascii')
        book_text = book_text + ' ' + line.lower()
    book.close()
    if len(book_text) > 1000000:
        book_text = book_text[:1000000]
    # tokenize using spacy
    # add <s>, </s>, and <sec> tags
    tokenized_book = process_book(book_text)
    processed_book = open(file_out,'w')
    processed_book.write(tokenized_book)
    processed_book.close()


def process_chapter_summaries(book_id):
    if not os.path.exists('../data/abstractive_summaries'):
        os.makedirs('../data/abstractive_summaries')
    chapter = 0
    extractive_summary_filename = get_extractive_summary_filename(book_id,chapter)
    abstractive_summary_filename = get_abstractive_summary_filename(book_id,chapter)
    book_abstractive_summary_filename = get_abstractive_summary_filename(book_id)
    path = pathlib.Path(extractive_summary_filename)
    book_summary = open(book_abstractive_summary_filename, 'w')
    while path.exists():
        process_file(extractive_summary_filename, abstractive_summary_filename)
        chapter_summary = open(abstractive_summary_filename,'r')
        for l in chapter_summary:
            book_summary.write(l)
        book_summary.write('\n')
        chapter_summary.close()
        chapter += 1
        extractive_summary_filename = get_extractive_summary_filename(book_id,chapter)
        abstractive_summary_filename = get_abstractive_summary_filename(book_id,chapter)
        path = pathlib.Path(extractive_summary_filename)
    book_summary.close()


def create_abstractive_summary_book(book_id):
    # create extractive summaries for chapters
    create_extractive_summary_book(book_id, 5)
    # process extractive summaries into test.txt for input to abstractive summarizer
    # (lower case, remove special characters, tokenize)
    process_chapter_summaries(book_id)
    # run abstractive summarizer
    if not os.path.exists('../../sum_data'):
        os.makedirs('../../sum_data')
    shutil.copyfile(get_abstractive_summary_filename(book_id), '../../sum_data/test.txt')
    os.system('python ../../LeafNATS/run.py --task beam')
    # process abstractive summary summaries.txt into abstractive summary
    # (detokenize)

