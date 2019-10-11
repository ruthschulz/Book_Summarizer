# BooksDistilled

## A personalized book summarizer

BooksDistilled is a natural language summarization tool that takes in the plain text of a very long document and outputs a variety of summaries using NLP tools and a neural text summarizer.

The project was a consulting project completed as part of the Insight AI program in Silicon Valley.
Tolstoy.ai provided the inspiration and NLP advice.

[Here](http://bit.ly/BookSummarizerSlides) are the slides for the Book Summarizer project.

## Project contents:
- **Book_Summarizer** : All source code
- **data** : Sample data 
- **results** : Sample results 
- **nats_results** : Model

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
Run these to copy the required folders of the LeafNATS repository into the appropriate place in the Book Summarizer repository.
```
git clone https://github.com/ruthschulz/LeafNATS
mv LeafNATS/* Book_Summarizer
```

The [model](https://drive.google.com/file/d/1EuLYK3k-U65xMtazqYskt6A97ZLe2a-n/view?usp=sharing) also needs to be downloaded and extracted into the Book_Summarizer/nats_results directory.

The [vocab](https://drive.google.com/file/d/1Kn14TMg0-ZLpnAUyJVhcuLXVWzZCD0Yg/view?usp=sharing) file also needs to be downloaded and extracted into the Book_Summarizer/sum_data directory.

## Run Book Summarizer

Place the text file of the book that you wish to summarize in the data/raw_books folder.
The filename needs to be in the format book_id.txt where book_id comprises only numbers.
E.g. 11.txt

"Alice's Adventures in Wonderland" was downloaded from Project Gutenberg and has been included in this repository.


```
cd Book_Summarizer
python book_summarizer.py -b 11 -fl -w
```

The options for use with book_summarizer.py are:
-b This is followed by a book_id for a specific book to be summarized, if not included all books in the data/books directory will be summarized.
-fl The first lines of each chapter will be added to the summary.
-en The entities (characters and key words) for each chapter will be added to the summary.
-ex The extractive summary (informative sentences) for each chapter will be added to the summary. The default is one sentences. This option can be followed by a number up to 9 to specify how many informative sentences to include per chapter.
-ae The abstractive summary of the extractive summary of each chapter will be added to the summary.
-aa The abstractive summary of the abstractive summary of each chapter will be added to the summary. This option can be followed by l to indicate that a long abstractive summary (between 5 and 20 sentences) should be included. The default is a short abstractive summary (between 1 and 4 sentences).
-w This indicates that if a summary already exists, it should be written over.

For example, to create a summary for a book with filename 11.txt including the first lines, entities, extractive summary, and abstractive summary of abstractive summary, and to write over an existing summary, the command would be:
```
python book_summarizer.py -b 11 -fl -en -ex -aa -w
```

This will save a summary called 11-fl-en-ex-aa.txt as well as an entities csv file called 11-en.csv in the results/summaries directory.


It is also possible to analyze the created summaries, comparing them to a ground truth summary in the data/summaries folder. Currently this is ex:
```
python book_summarizer.py -b 11 -aa -analysis
```

The program will then save a summary of the book in the appropriate results folder.

You can use your own book and summary files, or you can download matched books from [Project Gutenberg](http://www.gutenberg.org/wiki/Main_Page) and summaries from the [CMU Book Summary Dataset](http://www.cs.cmu.edu/~dbamman/booksummaries.html) using data.py:
```
python data.py
```

