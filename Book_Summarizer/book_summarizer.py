"""
This file is the entry point for calling the book summarizer
Create a summary of the book with features defined with command line arguments. 
"""

from entity_extraction import find_entities_book, find_entities_chapter, create_sentence
from entity_extraction import save_sorted_entities_book, save_sorted_entities_chapter
from data import first_lines_chapter, process_book, get_data_filename
from data import get_results_filename, get_analysis_filename
from extractive_summarizer import find_relevant_quote
from abstractive_summarizer import create_abstr_extr_summary_chapter, create_abstr_abstr_summary_chapter
from os import listdir, makedirs
from os.path import isfile, join, exists
from spacy import load
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.models import TfDocumentModel
from sumy.evaluation import cosine_similarity
import csv
import argparse


def summarize_book(book_id, num_chapters, args):
    """
    Summarize the book using the features specified in the command line arguments.
    
    Parameters:
    book_id: (int) the book identifier
    num_chapters: the number of chapters the book has been divided into
    args: the command line arguments provided
    
    Outputs:
    Saves the summary to file, with the name of the file determined by the arguments.
    """
    if not exists('../results/summaries'):
        makedirs('../results/summaries')
    summary_filename = get_results_filename(book_id, args)
    if isfile(summary_filename) and not args.w:
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
                    chapter_characters, about_book=False, about_characters=True)
                if (len(line) > 0):
                    complete_summary.write(line + '\n')
                line = create_sentence(
                    chapter_entities, about_book=False, about_characters=False)
                if (len(line) > 0):
                    complete_summary.write(line + '\n')
            if int(args.ex) != 0:
                # find quote using extractive summary techniques
                quote = find_relevant_quote(book_id, chapter, int(args.ex))
                # Print quote from chapter
                if len(quote) == 1:
                    complete_summary.write('Quote: ')
                else:
                    complete_summary.write('Quotes:\n')
                for q in quote:
                    line = '"' + str(q) + '"'
                    complete_summary.write(line + '\n')
            if args.ae:
                # Print abstractive summary for chapter
                abstr_extr_summary = create_abstr_extr_summary_chapter(
                    book_id, chapter)
                for line in abstr_extr_summary:
                    complete_summary.write(line)
            if args.aa != 'n':
                abstr_abstr_summary = create_abstr_abstr_summary_chapter(
                    book_id, chapter, args.aa == 's')
                for line in abstr_abstr_summary:
                    complete_summary.write(line)
            complete_summary.write('\n')
    if args.analysis:
        analyze_summaries(book_id, args)


def load_summary(filename):
    """
    Load the summary for analysis.
    
    Parameters:
    filename: the filename of the summary text file
    
    Returns:
    Spacy processed text and sumy processed text for analysis.
    """
    spacy_available = True
    try:
        nlp = load('en_core_web_lg')
    except:
        spacy_available = False
    if not isfile(filename):
        return '', '', ''
    if spacy_available:
        with open(filename, 'r') as summary_file:
            summary_text = ' '.join(summary_file)
            summary_doc = nlp(summary_text)
    else:
        summary_doc = ''
    summary_parser = PlaintextParser.from_file(
        filename, Tokenizer("english"))
    summary_model = TfDocumentModel(
        str(summary_parser.document.sentences), Tokenizer("en"))
    return summary_doc, summary_model


def analyze_summaries(book_id, args):
    """
    Analyze the summary.
    Compares the created summary with the ground truth summary.
    Expects the ground truth summary to be in the data/summaries directory.

    Parameters:
    book_id: (int) the book identifier
    args: the command line arguments, used to determine the filename for the created summary.

    Outputs:
    Saves the analysis to a csv file in the results/analysis directory
    """
    if not exists('../results/analysis'):
        makedirs('../results/analysis')
    analysis_data = []
    summary_doc, summary_model = load_summary(
        get_data_filename(book_id, 'summaries'))
    new_summary_doc, new_summary_model = load_summary(
        get_results_filename(book_id, args))
    if summary_doc != '':
        if new_summary_doc != '':
            analysis_data.append(
                ['word embeddings similarity', summary_doc.similarity(new_summary_doc)])
    if summary_model != '':
        if new_summary_model != '':
            analysis_data.append(
                ['cosine similarity', cosine_similarity(summary_model, new_summary_model)])
    with open(get_analysis_filename(book_id, args), 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(analysis_data)


def main():
    """
    Command line interface for the book summarizer

    The user specifies which elements to include in the summary.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=int, default=-1,
                        help='create a summary of a given book text file, indicated by number')
    parser.add_argument(
        "-en", help="include an entity summary of each chapter", action="store_true")
    parser.add_argument(
        "-ex", help="include an extractive summary of each chapter", nargs='?', const='1', default='0')
    parser.add_argument(
        "-ae", help="include an abstractive summary of each chapter", action="store_true")
    parser.add_argument(
        "-aa", help="include an abstractive summary of each chapter", nargs='?', const='s', default='n')
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
    if args.ex not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        print("For extractive summary, specify a number of sentences between 1 and 9")
        return
    if args.aa not in ['l', 's', 'n']:
        print("For abstractive from abstractive summary, specify l for long or s for short")
        return
    if not exists('../results'):
        makedirs('../results')
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
