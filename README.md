# BooksDistilled

## A personalized book summarizer

BooksDistilled is a natural language summarization tool that takes in the plain text of a very long document and outputs a summary using NLP tools and a neural text summarizer. The summary can optionally include for each chapter: first lines, characters and key words, quotes, and an abstractive summary.

The project was a consulting project completed as part of the [Insight AI program](https://www.insightdata.ai/) in Silicon Valley.
[Tolstoy.ai](https://tolstoy.ai/) provided the inspiration and NLP advice.

[Here](http://bit.ly/BookSummarizerSlides) are the slides for the Book Summarizer project.

## Project contents:
- **Book_Summarizer** : All source code
- **data** : Sample data 
- **examples** : Example setup and run
- **nats_results** : Folder for model
- **results** : Sample results 

## Setup Environment

The following setup instructions are for you to clone the repo to run locally.

Clone repository
```
git clone https://github.com/ruthschulz/Book_Summarizer
cd Book_Summarizer
```

Install requirements
```
pip install -r requirements.txt
```


Additional nltk dependencies
```bash
python -c "import nltk; nltk.download('punkt')"

```

Additional spaCy dependencies
```bash
python -m spacy download en_core_web_lg

```

If you are not able to download the large spaCy model, it is possible to use the small model, but the entity summary will not perform as well and the word embedding analysis will not be available:
```bash
python -m spacy download en_core_web_sm

```

This project uses another repository for the abstractive summarizer module.
The abstractive summarizer module is a forked version of the [LeafNATS](https://github.com/ruthschulz/LeafNATS) repository.
Run these to copy the required directories of the LeafNATS repository into the appropriate place in the Book Summarizer repository.
```
git clone https://github.com/ruthschulz/LeafNATS
mv LeafNATS/* Book_Summarizer
```

The [model](https://drive.google.com/file/d/1mL8l2p7YMPVlV5bhzsOMxYx3NXwdkqNG/view?usp=sharing) also needs to be downloaded and extracted into the Book_Summarizer/nats_results directory.

The [vocab](https://drive.google.com/file/d/1Kn14TMg0-ZLpnAUyJVhcuLXVWzZCD0Yg/view?usp=sharing) file also needs to be downloaded into the Book_Summarizer/sum_data directory.

Change directory to Book_Summarizer/Book_Summarizer and you are ready to summarize books.

```
cd Book_Summarizer
```

## Run Book Summarizer

Place the text file of the book that you wish to summarize in the data/raw_books directory.
The filename needs to be in the format book_id.txt

For example, 11.txt is the text of "Alice's Adventures in Wonderland" downloaded from Project Gutenberg and included in the data/raw_books directory.

Note that the system assumes that there are double empty lines between chapters, as this matches the format of many of the books available on Project Gutenberg.


```
usage: book_summarizer.py [-h] [-b B] [-en] [-ex [EX]]
                          [-exTechnique [EXTECHNIQUE]] [-ae] [-aa [AA]] [-fl]
                          [-analysis] [-w]

optional arguments:
  -h, --help            show this help message and exit
  -b B                  create a summary of a given book text file, indicated
                        by number, if not included, all books in
                        data/raw_books will be summarized
  -en                   include an entity summary of each chapter
  -ex [EX]              include an extractive summary of each chapter,
                        optionally choose how many sentences up to 9 (default
                        is 1)
  -exTechnique [EXTECHNIQUE]
                        choose the technique for extractive summarization by
                        name, options: luhn, lsa, lexrank, textrank, sumbasic,
                        kl, reduction, random
  -ae                   include an abstractive summary from an extractive
                        summary of each chapter
  -aa [AA]              include an abstractive summary from an abstractive
                        summary of each chapter, optionally choose short (s)
                        or long (l) summary (default is short)
  -fl                   include the first lines of each chapter
  -analysis             analyze the summary
  -w                    write over the existing summary
```

### Examples

To create a summary for a book with filename 11.txt including the first lines, and to write over an existing summary, the command would be:

```
python book_summarizer.py -b 11 -fl -w
```

This will save a summary called 11-fl.txt in the results/summaries directory.

To create a summary for a book with filename 11.txt including the first lines, entities, extractive summary, and abstractive summary of abstractive summary, and to write over an existing summary, the command would be:
```
python book_summarizer.py -b 11 -fl -en -ex -aa -w
```

This will save a summary called 11-fl-en-ex-aa.txt as well as an entities csv file called 11-en.csv in the results/summaries directory.

It is also possible to analyze the created summaries, comparing them to a ground truth summary in the data/summaries directory.

```
python book_summarizer.py -b 11 -aa -analysis
```

This would save 11.csv in the results/analysis directory with the word embedding similarity and cosine similarity between the created and ground truth summary.

### Data

You can use your own book and summary files, or you can download matched books from [Project Gutenberg](http://www.gutenberg.org/wiki/Main_Page) and summaries from the [CMU Book Summary Dataset](http://www.cs.cmu.edu/~dbamman/booksummaries.html) using data.py:

```
python data.py
```

If you use your own book files, they should be plain text files and should be placed in the data/raw_books directory.

