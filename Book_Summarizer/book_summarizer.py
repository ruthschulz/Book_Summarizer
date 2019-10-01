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

from entity_extraction import find_entities_book, find_entities_chapter, create_sentence
from data_download_and_stats import find_book, first_lines_chapter, process_book, get_basic_summary_filename
from extractive_summarizer import find_relevant_quote
import os
import sys
from os import listdir
from os.path import isfile, join

def summarize_book(book_id, num_chapters):
    if not os.path.exists('../data/basic_summaries'):
        os.makedirs('../data/basic_summaries')
    book_filename = get_basic_summary_filename(book_id)
    basic_summary = open(book_filename, 'w')
    # Print out number of segments found in book
    line = "Book '" + str(book_id) + "' has been divided into " + str(num_chapters) + " segments" 
    print(line)
    basic_summary.write(line + '\n')
    # find characters and key words for book
    book_characters, book_entities = find_entities_book(book_id)
    # Print out sentence for characters and key words
    line = create_sentence(book_characters, about_book=True, about_characters=True) 
    basic_summary.write(line + '\n')
    print(line)
    #print(create_sentence(book_characters, about_book=True, about_characters=True))
    line = create_sentence(book_entities, about_book=True, about_characters=False) 
    basic_summary.write(line + '\n')
    print(line)
    # for each chapter
    for chapter in range(num_chapters):
        line = "\nSegment " + str(chapter) + ", starting:"
        basic_summary.write(line + '\n')
        print(line)
        # find first two non-empty lines of chapter
        # Print first two non-empty lines of chapter
        line = first_lines_chapter(book_id, chapter)
        basic_summary.write(line)
        print(line, end='')
        # find characters and key words
        chapter_characters, chapter_entities = find_entities_chapter(
            book_id, chapter, book_characters, book_entities)
        # Print sentence for characters and key words from chapter
        line = create_sentence(chapter_characters, about_book=False, about_characters=True)
        if (len(line)>0):
            basic_summary.write(line + '\n')
            print(line)
        line = create_sentence(chapter_entities, about_book=False, about_characters=False)
        if (len(line)>0):
            basic_summary.write(line + '\n')
            print(line)
        # find quote using extractive summary techniques
        quote = find_relevant_quote(book_id, chapter)
        # Print quote from chapter
        for q in quote:
            line = 'Quote from segment: "' + str(q) + '"' 
            basic_summary.write(line + '\n')
            print(line)
        # generate abstractive summary based on context of chapter
        # Print abstractive summary for chapter
    basic_summary.close()


def main():
    book_id = -1
    if len(sys.argv)>1:
        if sys.argv[1][0]!='-':
            book_id = int(sys.argv[1])
    os.system('cls||clear')
    print("Book Summarizer:")
    print("Understanding your books for you")
    print()
    # if no arguments given, all raw books in raw_books folder will be summarized
    # otherwise argument following book_summarizer.py should be book_id,
    # and book text file named book_id.txt should be found in raw_books folder
    if (book_id==-1):
        book_files = [f for f in listdir('../data/raw_books') if isfile(join('../data/raw_books', f))]
        for f in book_files:
            print(f.strip('.txt'),end=', ')
        for f in book_files:
            book_id=int(f.strip('.txt'))
            # break down into chapters / segments, then summarize book
            book_id,num_chapters = process_book(book_id)
            if (book_id!=-1):
                summarize_book(book_id,num_chapters)
    else:
        # break down into chapters / segments, then summarize book
        book_id,num_chapters = process_book(book_id)
        if (book_id!=-1):
            summarize_book(book_id,num_chapters)


if __name__ == "__main__":
    main()
