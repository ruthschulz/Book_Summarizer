# entry point for calling the book summarizer
# command line interface
# if no arguments given, all raw books in raw_books folder will be summarized
# otherwise argument following book_summarizer.py should be -b book_id,
# and a book text file named book_id.txt should be found in raw_books folder
# no additional tag -> print all information
# if any tags, print only information specified by tags
# -fl for first line(s) - number specifies how many lines, default is one
# -en for entities
# -ex for extractive summary - number specifies how many sentences
# -ae for abstractive from extractive summary
# -aa for abstractive from abstractive summary

from entity_extraction import find_entities_book, find_entities_chapter, create_sentence
from entity_extraction import save_sorted_entities_book, save_sorted_entities_chapter
from data_download_and_stats import first_lines_chapter, process_book, get_data_filename
from data_download_and_stats import get_results_filename, get_analysis_filename
from extractive_summarizer import find_relevant_quote
from abstractive_summarizer import create_abstractive_summary_chapter
from abstractive_2_summarizer import create_abstractive_2_summary_chapter
import os
import sys
from os import listdir
from os.path import isfile, join
import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.models import TfDocumentModel
from sumy.evaluation import cosine_similarity, rouge_n
import csv
import argparse


def summarize_book(book_id, num_chapters, args):
    if not os.path.exists('../results/summaries'):
        os.makedirs('../results/summaries')
    summary_filename = get_results_filename(book_id,args)
    if os.path.isfile(summary_filename) and not args.w:
        return
    with open(summary_filename, 'w') as complete_summary:
        if args.en:
            # find characters and key words for book
            book_characters, book_entities = find_entities_book(book_id)
            # Print out sentence for characters and key words
            line = create_sentence(
                book_characters, about_book=True, about_characters=True)
            complete_summary.write(line + '\n')
            line = create_sentence(
                book_entities, about_book=True, about_characters=False)
            complete_summary.write(line + '\n')
            save_sorted_entities_book(book_characters, book_entities, book_id)
            complete_summary.write('\n')
        # for each chapter
        for chapter in range(num_chapters):
            line = "Chapter " + str(chapter)
            complete_summary.write(line + '\n')
            if args.fl:
                line = "Starting:"
                complete_summary.write(line + '\n')
                # find first two non-empty lines of chapter
                # Print first two non-empty lines of chapter
                line = first_lines_chapter(book_id, chapter)
                complete_summary.write(line)
            if args.en:
                # find characters and key words
                chapter_characters, chapter_entities = find_entities_chapter(
                    book_id, chapter, book_characters, book_entities)
                save_sorted_entities_chapter(
                    chapter_characters, chapter_entities, book_id, chapter)
                # Print sentence for characters and key words from chapter
                line = create_sentence(
                    chapter_characters, about_book=False, about_characters=True, chapter=chapter)
                if (len(line) > 0):
                    complete_summary.write(line + '\n')
                line = create_sentence(
                    chapter_entities, about_book=False, about_characters=False, chapter=chapter)
                if (len(line) > 0):
                    complete_summary.write(line + '\n')
            if args.ex:
                # find quote using extractive summary techniques
                quote = find_relevant_quote(book_id, chapter)
                # Print quote from chapter
                for q in quote:
                    line = 'Quote: "' + str(q) + '"'
                    complete_summary.write(line + '\n')
            if args.ae:
                # Print abstractive summary for chapter
                abstractive_summary = create_abstractive_summary_chapter(book_id,chapter)
                for line in abstractive_summary:
                    complete_summary.write(line)
            if args.aa:
                abstractive_2_summary = create_abstractive_2_summary_chapter(book_id,chapter)
                for line in abstractive_2_summary:
                    complete_summary.write(line)
            complete_summary.write('\n')
    if args.analysis:
        analyze_summaries(book_id, args)


def load_summary(filename):
    spacy_available = True
    try:
        nlp = spacy.load('en_core_web_lg')
    except:
        spacy_available = False
    if not os.path.isfile(filename):
        return '', '', ''
    if spacy_available:
        with open(filename,'r') as summary_file:
            summary_text = ' '.join(summary_file)
            summary_doc = nlp(summary_text)
    else:
        summary_doc = ''
    summary_parser = PlaintextParser.from_file(
        filename, Tokenizer("english"))
    summary_model = TfDocumentModel(str(summary_parser.document.sentences), Tokenizer("en"))
    return summary_doc, summary_model


def analyze_summaries(book_id, args):
    if not os.path.exists('../results/analysis'):
        os.makedirs('../results/analysis')
    analysis_data = []
    summary_doc, summary_model = load_summary(
        get_data_filename(book_id,'summaries'))
    new_summary_doc, new_summary_model = load_summary(
        get_results_filename(book_id,args))
    if summary_doc != '':
        if new_summary_doc != '':
            analysis_data.append(['word embeddings similarity', summary_doc.similarity(new_summary_doc)])
    if summary_model != '':
        if new_summary_model != '':
            analysis_data.append(['cosine similarity', cosine_similarity(summary_model, new_summary_model)])
    with open(get_analysis_filename(book_id,args), 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(analysis_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=int, default=-1,
                        help='create a summary of a given book text file, indicated by number')
    parser.add_argument(
        "-en", help="include an entity summary of each chapter", action="store_true")
    parser.add_argument(
        "-ex", help="include an extractive summary of each chapter", action="store_true")
    parser.add_argument(
        "-ae", help="include an abstractive summary of each chapter", action="store_true")
    parser.add_argument(
        "-aa", help="include an abstractive summary of each chapter", action="store_true")
    parser.add_argument(
        "-fl", help="include the first lines of each chapter", action="store_true")
    parser.add_argument(
        "-analysis", help="analyze all summaries", action="store_true")
    parser.add_argument(
        "-w", help="write over existing summaries", action="store_true")
    args = parser.parse_args()
    # if -b is not given, all raw books in raw_books folder will be summarized
    # otherwise argument following -b should be an integer book_id,
    # where a book text file named book_id.txt is in the raw_books folder
    if not os.path.exists('../results'):
        os.makedirs('../results')
    if (args.b == -1):
        book_files = [f for f in listdir(
            '../data/raw_books') if isfile(join('../data/raw_books', f))]
        for f in book_files:
            book_id = int(f.strip('.txt'))
            # break down into chapters / segments, then summarize book
            book_id, num_chapters = process_book(book_id)
            if (book_id != -1):
                summarize_book(book_id, num_chapters, args)
    else:
        # break down into chapters / segments, then summarize book
        book_id, num_chapters = process_book(args.b)
        if (book_id != -1):
            summarize_book(book_id, num_chapters, args)


if __name__ == "__main__":
    main()
