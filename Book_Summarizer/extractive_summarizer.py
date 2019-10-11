"""
This file has the functions for the extractive summarizer.
Create an extractive summary from chapters of a large document.
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from data import get_data_filename


def find_relevant_quote(book_id, chapter, num_sentences=1):
    """
    Create an extractive summary for a chapter of the book.

    Parameters:
    book_id: is the project gutenberg identifier
    chapter: is the chapter number to summarize
    num_sentences: how many sentences to extract

    Returns:
    sentences: the extracted sentences
    """
    chapter_filename = get_data_filename(book_id, 'book_chapters', chapter)
    parser = PlaintextParser.from_file(chapter_filename, Tokenizer("english"))
    summarizer = LuhnSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return summary
