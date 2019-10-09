# extractive summarizer
# create an extractive summary from chapters of a large document

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from data_download_and_stats import get_data_filename


# create_extractive_summary_chapter(book_id, chapter, summarizer, size)
#
# create an extractive summary for a chapter of the book
# book_id is the project gutenberg identifier
# chapter is the chapter number to summarize
# (refers to file break down, may not actually be that chapter in the book)
# summarizer is the sumy summarizer that will create the summary
def find_relevant_quote(book_id, chapter, num_sentences=1):
    chapter_filename = get_data_filename(book_id, 'book_chapters', chapter)
    parser = PlaintextParser.from_file(chapter_filename, Tokenizer("english"))
    summarizer = LuhnSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return summary
