"""
This file has the functions for the extractive summarizer.
Create an extractive summary from chapters of a large document.
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.random import RandomSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from data import get_data_filename


def find_relevant_quote(book_id, chapter, num_sentences=1, technique='luhn'):
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
    if technique=='lsa':
        summarizer = LsaSummarizer()
    elif technique=='lexrank':
        summarizer = LexRankSummarizer()
    elif technique=='textrank':
        summarizer = TextRankSummarizer()
    elif technique=='kl':
        summarizer = KLSummarizer()
    elif technique=='random':
        summarizer = RandomSummarizer()
    elif technique=='reduction':
        summarizer = ReductionSummarizer()
    elif technique=='sumbasic':
        summarizer = SumBasicSummarizer()
    else:
        summarizer = LuhnSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return summary
