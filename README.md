# Book Summarizer

## Summarizing very long text for you

Book Summarizer is a natural language summarization tool that takes in the plain text of a very long document and outputs a variety of summaries using NLP tools and a neural text summarizer.

The project was a consulting project completed as part of the Insight AI program in Silicon Valley.
Tolstoy.ai provided the inspiration and NLP advice.

[Here](http://bit.ly/BookSummarizerSlides) are the slides for the Book Summarizer project.

## Project contents:
- **Book_Summarizer** : All source code
- **data** : Sample data 
- **results** : Sample results 
- **configs** : Files for modification of all preset variables

## Setup Environment

The following setup instructions are for you to clone the repo to run locally.

Clone repository
```
git clone https://github.com/ruthschulz/Book_Summarizer
cd Book_Summarizer
```

Additional nltk dependencies
```bash
python -c "import nltk; nltk.download('punkt')"

```

Additional spaCy dependencies
```bash
python -m spacy download en_vectors_web_lg

```

If you are not able to download the large spaCy model, it is possible to use the small model, but the entity summary will not perform as well and the word embedding analysis will not be available:
```bash
python -m spacy download en_vectors_web_sm

```

This project uses another repository for the abstractive summarizer module.
The abstractive summarizer module is a forked version of the [LeafNATS](https://github.com/ruthschulz/LeafNATS) repository.
Run these to copy the required folders of the LeafNATS repository into the appropriate place in the Book Summarizer repository.
```
git clone https://github.com/ruthschulz/LeafNATS
mv LeafNATS/* Book_Summarizer
```



## Run Book Summarizer

Place the text file of the book that you wish to summarize in the data/raw_books folder.


```
cd Book_Summarizer
python book_summarizer.py -technique
```

Technique can be one of the following:
```
python book_summarizer.py -entity
python book_summarizer.py -extractive
python book_summarizer.py -abstractive
python book_summarizer.py -abstractive2
python book_summarizer.py -combined
```




It is also possible to analyze the summaries, comparing them to an existing summary in the data/summaries folder:
```
python book_summarizer.py -analysis
```

The program will then save a summary of the book in the appropriate results folder.


