# entry point for calling the book summarizer
# command line interface
# requrires title and author
# [or just title and confirm which author]
# [or just author and confirm which title]
# options: all = book characters, key terms, number of chapters / segments;
# chapter first line, characters, key words, quote, generated sentence from chapter context
# other options could remove these
# no additional tag -> print all information
# if any tags, print only information specified by tags
# or somehow allow remove all except for specified by tags?
# c for characters
# k for key terms
# q for quote
# f for first line
# g for generated sentence


# reduce these to just the functions that are needed:
from entity_extraction import find_entities_book, find_entities_chapter, create_sentence
from data_download_and_stats import find_book
from extractive_summarizer import create_extractive_summary_chapter, divide_book_into_chapters, analyze_summary


def summarize_book(book_title, book_author=''):
    # find the book title in the data base, match the author name
    book_id, book_title, book_author = find_book(book_title, book_author)
    print(str(book_id) + ':' + book_title + ' by ' + book_author)
# confirm whether the correct book title and author have been found
# download the book
# Print book title and author
# break down into chapters / segments
# work out whether to exclude any chapters due to size or content
# Print out number of segments found in book
# find characters and key words for book
# Print out sentence for characters and key words
# for each chapter
#     find first line of chapter
#     Print first line of chapter
#     find quote using extractive summary techniques
#     Print qute from chapter
#     find characters and key words
#     Print sentence for characters and key words from chapter
#     generate sentences based on context of chapter and choose most similar to chapter
#     Print generated sentence for chapter
