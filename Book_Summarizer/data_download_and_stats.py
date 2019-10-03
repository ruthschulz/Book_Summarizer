import pandas as pd
import wget
import shutil
import os
from zipfile import ZipFile
from fuzzywuzzy import fuzz
import csv
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

def get_text_filename(book_id):
    return str(book_id) + ".txt"

def get_zip_filename(book_id):
    return str(book_id) + ".zip"

def get_raw_book_filename(book_id):
    return '../data/raw_books/' + get_text_filename(book_id)

def get_clean_book_filename(book_id):
    return '../data/books/' + get_text_filename(book_id)

def get_chapter_filename(book_id, chapter_num):
    return '../data/book_chapters/' + str(book_id) + '-' + str(chapter_num) + '.txt'

def get_summary_filename(book_id):
    return '../data/summaries/' + str(book_id) + '.txt'

def get_complete_summary_filename(book_id):
    return '../data/complete_summaries/' + str(book_id) + '.txt'

def get_extractive_summary_filename(book_id, chapter_num=-1):
    if (chapter_num==-1):
        return '../data/extractive_summaries/' + str(book_id) + '.txt'
    else:
        return '../data/extractive_summaries/' + str(book_id) + '-' + str(chapter_num) + '.txt'

def get_abstractive_summary_filename(book_id, chapter_num=-1):
    if (chapter_num==-1):
        return '../data/abstractive_summaries/' + str(book_id) + '.txt'
    else:
        return '../data/abstractive_summaries/' + str(book_id) + '-' + str(chapter_num) + '.txt'

def get_key_concept_summary_filename(book_id):
    return '../data/key_concept_summaries/' + str(book_id) + '.txt'

# calculate_data_stats(book_filename,summary_filename)
#
# calculates number of sentences, number of words, file size
# for books and summaries
def calculate_data_stats(book_filename, summary_filename):
    parser = PlaintextParser.from_file(book_filename, Tokenizer("english"))
    num_sentences_in_book = len(parser.document.sentences)
    num_words_in_book = len(parser.document.words)
    file_info = os.stat(book_filename)
    file_size_book = file_info.st_size
    parser = PlaintextParser.from_file(summary_filename, Tokenizer("english"))
    num_sentences_in_summary = len(parser.document.sentences)
    num_words_in_summary = len(parser.document.words)
    file_info = os.stat(summary_filename)
    file_size_summary = file_info.st_size
    return [num_sentences_in_book, num_words_in_book, file_size_book,
            num_sentences_in_summary, num_words_in_summary, file_size_summary]


# data_list()
#
# load book summaries
# load metadata about Project Gutenberg books
# match summaries and books on title
# return list of matched books and summaries
# also saves this list to file
# also return list of titles and summaries
def data_list():
    # otherwise the summaries are cropped
    pd.set_option("display.max_colwidth", 100000)
    df = pd.read_csv("../data/booksummaries.txt", sep='\t', header=None)
    df[2] = df[2].map(lambda x: x.lower())
    pg_df = pd.read_csv("../data/SPGC-metadata-2018-07-18.csv")
    pg_df["title"] = pg_df["title"].map(lambda x: str(x).lower())
    # match summaries and books on title
    # requires exact title, does not check author
    # multiple books may be assigned to a summary
    df_combined = df.merge(pg_df, left_on=2, right_on='title')
    # save a list of the titles and authors
    df_titles = df_combined[['title', 'author', 3, 'id']]
    df_titles.to_csv('matched_titles.csv')
    df_summaries = df[[2, 6]]
    return df_titles, df_summaries


# calculate_author_match(author1,author2)
#
# calculates the match between author names
# returns a value between 0 and 100
# 0 indicates no match, 100 indicates perfect match
# with different orders of names and extra information about 40 is a good threshold
# assumption made that if no author is provided there is a match
def calculate_author_match(author1, author2):
    if isinstance(author1, str) and isinstance(author2, str):
        return fuzz.partial_ratio(author1, author2)
    else:
        return 100


# download_from_gutenberg(pg_id)
#
# downloads the book zip file from Project Gutenberg into the current directory
# some of the links do not work
# for PGabcde, the address is http://aleph.gutenberg.org/a/b/c/d/abcde/abcde.zip
def download_from_gutenberg(pg_id):
    web_page = "http://aleph.gutenberg.org/"
    for d in str(pg_id)[:-1]:
        web_page = web_page + str(d) + "/"
    web_page = web_page + str(pg_id) + "/" + str(pg_id) + ".zip"
    file_exists = True
    try:
        wget.download(web_page)
    except:
        print("404 error")
        file_exists = False
    return file_exists


# extract_book(pg_index)
#
# unzip the book and move to books folder
# remove zip file afterwards
def extract_book(pg_index, zip_filename='', text_filename='', book_filename=''):
    if not os.path.exists('../data/raw_books'):
        os.makedirs('../data/raw_books')
    if len(zip_filename)==0:
        zip_filename = get_zip_filename(pg_index)
        #zip_filename = str(pg_index) + ".zip"
    if len(text_filename)==0:
        text_filename = get_text_filename(pg_index)
        #text_filename = str(pg_index) + ".txt"
    if len(book_filename)==0:
        book_filename = get_raw_book_filename(pg_index)
        #book_filename = '../data/raw_books/' + text_filename
    with ZipFile(zip_filename, 'r') as zipObj:
        zipObj.extractall()
    if os.path.exists(text_filename):
        shutil.move(text_filename, book_filename)
    else:
        # some files have an extra folder before the file
        shutil.move(str(pg_index) + '/' + text_filename, book_filename)
        shutil.rmtree(str(pg_index))
    os.remove(zip_filename)


# save_summary(df_summaries, new_title, summary_filename)
#
# saves the summary to the summary folder
def save_summary(df_summaries, new_title, summary_filename):
    if not os.path.exists('../data/summaries'):
        os.makedirs('../data/summaries')
    new_summary = df_summaries[df_summaries[2] == new_title][6].to_string()[6:]
    with open(summary_filename, 'w') as f:
        f.write(new_summary)


# save_clean_book(pg_index)
#
# removes information about project gutenberg from the book
# replaces the book file with the cleaned book
def save_clean_book(pg_index):
    if not os.path.exists('../data/books'):
        os.makedirs('../data/books')
    text_filename = get_text_filename(pg_index)
    book_filename = get_raw_book_filename(pg_index)
    clean_book_filename = get_clean_book_filename(pg_index)
    book = open(book_filename, 'r', encoding='latin-1')
    clean_book = open(clean_book_filename, 'w')
    write_lines = False
    for l in book:
        if (l[:12] == '*** START OF') or (l[:11] == '***START OF') or (l[:11] == '*END*THE SM'):
            write_lines = True
        elif (l[:10] == '*** END OF') or (l[:9] == '***END OF'):
            write_lines = False
        elif write_lines:
            clean_book.write(l)
    book.close()
    clean_book.close()
    # if the formatting didn't match the above, just use the complete
    # book with project gutenberg information
    if os.stat(clean_book_filename).st_size == 0:
        book = open(book_filename, 'r', encoding='latin-1')
        clean_book = open(clean_book_filename, 'w')
        for l in book:
            clean_book.write(l)
        book.close()
        clean_book.close()


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
    if not os.path.exists('../data/book_chapters'):
        os.makedirs('../data/book_chapters')
    book_filename = get_clean_book_filename(book_id)
    count_chapters = 0
    count_lines_in_chapter = 0
    previous_blank_line = False
    book = open(book_filename, 'r', encoding='latin-1')
    book_chapter = open(get_chapter_filename(book_id,count_chapters), 'w')
    for l in book:
        if (count_lines_in_chapter < 3000) and ((len(l) > 1) or (count_lines_in_chapter < 20)):
            previous_blank_line = False
            count_lines_in_chapter += 1
            book_chapter.write(l)
        elif (len(l) == 1) and ((previous_blank_line == True) or (count_lines_in_chapter >= 3000)):
            count_lines_in_chapter = 0
            count_chapters += 1
            book_chapter.close()
            book_chapter = open(get_chapter_filename(book_id,count_chapters), 'w')
        elif (len(l) == 1):
            count_lines_in_chapter += 1
            previous_blank_line = True
            book_chapter.write(l)
        else:
            count_lines_in_chapter += 1
            book_chapter.write(l)
    book_chapter.close()
    book.close()
    return count_chapters


def create_book_dataset():
    # load info about books and summaries
    df_titles, df_summaries = data_list()
    # for each item, check if title is already in database
    # if it isn't, check if it can be downloaded
    # move to books folder
    # process book to remove metadata and license information
    if os.path.exists('../data/books'):
        shutil.rmtree('../data/books')
    if os.path.exists('../data/summaries'):
        shutil.rmtree('../data/summaries')
    if os.path.exists('../data/raw_books'):
        shutil.rmtree('../data/raw_books')
    os.makedirs('../data/books')
    os.makedirs('../data/summaries')
    os.makedirs('../data/raw_books')
    titles = dict()
    stats = []
    for index, row in df_titles.iterrows():
        new_title = row['title']
        pg_index = row['id'][2:]
        pg_author = row['author']
        summaries_author = row[3]
        if ((new_title not in titles) and (calculate_author_match(pg_author, summaries_author) > 40)):
            file_exists = download_from_gutenberg(pg_index)
            if (file_exists):
                zip_filename = get_zip_filename(pg_index)
                text_filename = get_text_filename(pg_index)
                book_filename = get_raw_book_filename(pg_index)
                clean_book_filename = get_clean_book_filename(pg_index)
                summary_filename = get_summary_filename(pg_index)
                extract_book(pg_index, zip_filename,
                             text_filename, book_filename)
                save_summary(df_summaries, new_title, summary_filename)
                save_clean_book(pg_index)
                titles[new_title] = pg_index
                print(new_title)
                b_s_stats = calculate_data_stats(
                    clean_book_filename, summary_filename)
                new_stats = [new_title, pg_index, pg_author, summaries_author]
                new_stats.extend(b_s_stats)
                stats.append(new_stats)
    with open('data_stats.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(stats)
    csvFile.close()


# for all books listed in data_stats.csv
# divide into chapters and save in book_chapters folder
def test_divide_into_chapters():
    df = pd.read_csv("data_stats.csv", sep=',', header=None)
    for index, row in df.iterrows():
        pg_index = row[1]
        divide_book_into_chapters(pg_index)


def first_lines_chapter(book_id,chapter_num):
    book_chapter = open(get_chapter_filename(book_id,chapter_num), 'r')
    lines = ''
    num_lines = 0
    if book_chapter.readable():
        for l in book_chapter:
            if len(l)>1:
                lines = lines + l.strip('\n') + ' '
                num_lines += 1
            if (num_lines>=2):
                break
    book_chapter.close()
    return (lines + '...\n')


def find_book(book_title='', book_author=''):
    book_id = -1
# if only book_title provided
#     find book_title in list of titles
#     print list of authors asking which author or confirming if only one found
    if len(book_title)>0:
        book_title = book_title.lower()
        pg_df = pd.read_csv("../data/SPGC-metadata-2018-07-18.csv")
        pg_df["title"] = pg_df["title"].map(lambda x: str(x).lower())
        possible_matches = pg_df[pg_df["title"]==book_title]
        possible_matches = possible_matches[possible_matches['type']=='Text']
        print("Please specify which book to summarize:")
        row_index = 0
        for index, row in possible_matches.iterrows():
            print(str(row_index) + ":" + row['title'] + ' by ' + row['author'] + '(' + row['id'] + ')')
            row_index += 1
        match_index = int(input())
        row_index = 0
        for index, row in possible_matches.iterrows():
            if match_index==row_index:
                book_title = row['title']
                book_author = row['author']
                book_id = row['id'][2:]
            row_index += 1
# if only book_author provided
#     find book_author in list of titles
#     print list of titles asking which title
# if both book_title and book_author provided
#     find book_title in list of titles
#     find book_author in list of authors
#     if there is a match
#         attempt to download book
#         return identifier for book
    download_from_gutenberg(book_id)
    extract_book(book_id)
    save_clean_book(book_id)
    num_chapters = divide_book_into_chapters(book_id)
    return book_id, book_title, book_author, num_chapters

def process_book(book_id):
    num_chapters = 0
    if not os.path.isfile(get_raw_book_filename(book_id)):
        book_id=-1
    if book_id>=0:
        save_clean_book(book_id)
        num_chapters = divide_book_into_chapters(book_id)
    return book_id, num_chapters
