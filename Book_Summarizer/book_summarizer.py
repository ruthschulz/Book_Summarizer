# entry point for calling the book summarizer
# command line interface
# if no arguments given, all raw books in raw_books folder will be summarized
# otherwise argument following book_summarizer.py should be book_id,
# and book text file named book_id.txt should be found in raw_books folder
# options: all = book characters, key terms, number of chapters / segments;
# chapter first line, characters, key words, quote, generated sentence from chapter context
# other options could remove these
# no additional tag -> print all information
# if any tags, print only information specified by tags
# -c for characters
# -k for key terms
# -q for quote
# -f for first line
# -g for generated sentence

from entity_extraction import find_entities_book, find_entities_chapter, create_sentence, create_key_concept_summary_book
from data_download_and_stats import first_lines_chapter, process_book, get_complete_summary_filename, get_key_concept_summary_filename, get_summary_filename, get_extractive_summary_filename, get_abstractive_summary_filename, get_abstractive_2_summary_filename
from extractive_summarizer import find_relevant_quote, create_extractive_summary_book
from abstractive_summarizer import create_abstractive_summary_book
from abstractive_2_summarizer import create_abstractive_2_summary_book
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


def create_complete_summary_book(book_id, num_chapters, chapter_abstractive_summaries):
    if not os.path.exists('../results/complete_summaries'):
        os.makedirs('../results/complete_summaries')
    summary_filename = get_complete_summary_filename(book_id)
    complete_summary = open(summary_filename, 'w')
    # find characters and key words for book
    book_characters, book_entities = find_entities_book(book_id)
    # Print out sentence for characters and key words
    line = create_sentence(book_characters, about_book=True, about_characters=True) 
    complete_summary.write(line + '\n')
    line = create_sentence(book_entities, about_book=True, about_characters=False) 
    complete_summary.write(line + '\n')
    # for each chapter
    for chapter in range(num_chapters):
        line = "\nChapter " + str(chapter) + ", starting:"
        complete_summary.write(line + '\n')
        # find first two non-empty lines of chapter
        # Print first two non-empty lines of chapter
        line = first_lines_chapter(book_id, chapter)
        complete_summary.write(line)
        # find characters and key words
        chapter_characters, chapter_entities = find_entities_chapter(
            book_id, chapter, book_characters, book_entities)
        # Print sentence for characters and key words from chapter
        line = create_sentence(chapter_characters, about_book=False, about_characters=True, chapter=chapter)
        if (len(line)>0):
            complete_summary.write(line + '\n')
        line = create_sentence(chapter_entities, about_book=False, about_characters=False, chapter=chapter)
        if (len(line)>0):
            complete_summary.write(line + '\n')
        # find quote using extractive summary techniques
        quote = find_relevant_quote(book_id, chapter)
        # Print quote from chapter
        for q in quote:
            line = 'Quote from chapter: "' + str(q) + '"' 
            complete_summary.write(line + '\n')
        # Print abstractive summary for chapter
        complete_summary.write(chapter_abstractive_summaries[chapter])
    complete_summary.close()


def summarize_book(book_id, num_chapters, args):
    if args.entity:
        create_key_concept_summary_book(book_id,num_chapters)
    if args.extractive:
        create_extractive_summary_book(book_id,3)
    if args.abstractive or args.combined:
        chapter_abstractive_summaries = create_abstractive_summary_book(book_id)
    if args.combined:
        create_complete_summary_book(book_id, num_chapters, chapter_abstractive_summaries)
    if args.abstractive2:
        create_abstractive_2_summary_book(book_id)
    #if args.entity and args.extractive and args.abstractive and args.combined:
    if args.analysis:
        compare_summaries(book_id)

def load_summary(filename):
    nlp = spacy.load('en_core_web_lg')
    if not os.path.isfile(filename):
        return '', '', ''
    summary_file = open(filename, 'r')
    summary_text = ' '.join(summary_file)
    summary_doc = nlp(summary_text)
    summary_parser = PlaintextParser.from_file(
        filename, Tokenizer("english"))
    summary_sentences = summary_parser.document.sentences
    summary_model = TfDocumentModel(str(summary_sentences), Tokenizer("en"))
    return summary_doc, summary_sentences, summary_model


def compare_summaries(book_id):
    if not os.path.exists('../results/analysis'):
        os.makedirs('../results/analysis')
    analysis_data = [['summary','spacy similarity','rouge_n','cosine similarity']]
    summary_doc, summary_sentences, summary_model = load_summary(get_summary_filename(book_id))
    key_concepts_doc, key_concepts_sentences, key_concepts_model = load_summary(get_key_concept_summary_filename(book_id))
    extractive_doc, extractive_sentences, extractive_model = load_summary(get_extractive_summary_filename(book_id))
    abstractive_doc, abstractive_sentences, abstractive_model = load_summary(get_abstractive_summary_filename(book_id))
    abstractive_2_doc, abstractive_2_sentences, abstractive_2_model = load_summary(get_abstractive_2_summary_filename(book_id))
    complete_doc, complete_sentences, complete_model = load_summary(get_complete_summary_filename(book_id))
    if summary_doc != '':
        if key_concepts_doc != '':
            analysis_data.append(['key concepts', summary_doc.similarity(key_concepts_doc), rouge_n(summary_sentences, key_concepts_sentences), cosine_similarity(summary_model, key_concepts_model)])
        if extractive_doc != '':
            analysis_data.append(['extractive', summary_doc.similarity(extractive_doc), rouge_n(summary_sentences, extractive_sentences), cosine_similarity(summary_model, extractive_model)])
        if abstractive_doc != '':
            analysis_data.append(['abstractive', summary_doc.similarity(abstractive_doc), rouge_n(summary_sentences, abstractive_sentences), cosine_similarity(summary_model, abstractive_model)])
        if abstractive_2_doc != '':
            analysis_data.append(['abstractive 2', summary_doc.similarity(abstractive_2_doc), rouge_n(summary_sentences, abstractive_2_sentences), cosine_similarity(summary_model, abstractive_2_model)])
        if complete_doc != '':
            analysis_data.append(['combined', summary_doc.similarity(complete_doc), rouge_n(summary_sentences, complete_sentences), cosine_similarity(summary_model, complete_model)])
    with open('../results/analysis/'+ str(book_id) + '.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(analysis_data)
    csvFile.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=int, default=-1, 
            help='create a summary of a given book text file, indicated by number')
    parser.add_argument("-entity", help="create an entity summary of the book", action="store_true")
    parser.add_argument("-extractive", help="create an extractive summary of the book", action="store_true")
    parser.add_argument("-abstractive", help="create an abstractive summary of the book", action="store_true")
    parser.add_argument("-abstractive2", help="create an abstractive summary of the book", action="store_true")
    parser.add_argument("-combined", help="create a combined summary of the book", action="store_true")
    parser.add_argument("-analysis", help="analyze all summaries", action="store_true")
    args = parser.parse_args()
    # if no arguments given, all raw books in raw_books folder will be summarized
    # otherwise argument following book_summarizer.py should be book_id,
    # and book text file named book_id.txt should be found in raw_books folder
    if not os.path.exists('../results'):
        os.makedirs('../results')
    if (args.b==-1):
        book_files = [f for f in listdir('../data/raw_books') if isfile(join('../data/raw_books', f))]
        for f in book_files:
            book_id=int(f.strip('.txt'))
            # break down into chapters / segments, then summarize book
            book_id,num_chapters = process_book(book_id)
            if (book_id!=-1):
                summarize_book(book_id,num_chapters, args)
    else:
        # break down into chapters / segments, then summarize book
        book_id,num_chapters = process_book(args.b)
        if (book_id!=-1):
            summarize_book(book_id,num_chapters, args)


if __name__ == "__main__":
    main()
