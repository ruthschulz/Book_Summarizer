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

from entity_extraction import find_entities_book, find_entities_chapter, create_sentence
from data_download_and_stats import find_book, first_lines_chapter
from extractive_summarizer import find_relevant_quote


def summarize_book(book_title, book_author=''):
    # find the book title in the data base, match the author name
    # confirm whether the correct book title and author have been found
    # download the book
    # Print book title and author
    # break down into chapters / segments
    book_id, book_title, book_author, num_chapters = find_book(
        book_title, book_author)
    print('\n' + str(book_id) + ':' + book_title + ' by ' + book_author)
    # Print out number of segments found in book
    print(book_title + " has been divided into " +
          str(num_chapters) + " segments")
    # find characters and key words for book
    book_characters, book_entities = find_entities_book(book_id)
    # Print out sentence for characters and key words
    print(create_sentence(book_characters, about_book=True, about_characters=True))
    print(create_sentence(book_entities,
                          about_book=True, about_characters=False))
    # for each chapter
    for chapter in range(num_chapters):
        print("\nSegment " + str(chapter) + ", starting:")
        # find first two non-empty lines of chapter
        # Print first two non-empty lines of chapter
        print(first_lines_chapter(book_id, chapter), end='')
        # find characters and key words
        chapter_characters, chapter_entities = find_entities_chapter(
            book_id, chapter, book_characters, book_entities)
        # Print sentence for characters and key words from chapter
        print(create_sentence(chapter_characters,
                              about_book=False, about_characters=True))
        print(create_sentence(chapter_entities,
                              about_book=False, about_characters=False))
        # find quote using extractive summary techniques
        quote = find_relevant_quote(book_id, chapter)
        # Print quote from chapter
        for q in quote:
            print('Quote from segment: "' + str(q) + '"')
        # generate sentences based on context of chapter and choose most similar to chapter
        # Print generated sentence for chapter
