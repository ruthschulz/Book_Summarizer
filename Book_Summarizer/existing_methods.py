# test of existing extractive summerizer methods

from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.models import TfDocumentModel
from sumy.evaluation import cosine_similarity
from sumy.evaluation import rouge_n, rouge_l_sentence_level, rouge_l_summary_level
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

import os
import pandas as pd
import shutil
import csv

sizes = [5, 10, 20, 50]
sizes_ranges = [[4,6],[9,11],[19,22],[43,57]]

# set up set of documents for each size abstract
set_of_documents = [[]]
df = pd.read_csv("data_stats.csv",sep=',',header=None)
for s in range(4):
  if s>0:
    set_of_documents.append([])
  for index, row in df.iterrows():
    pg_index = row[1]
    summary_sentences = row[7]
    if (sizes_ranges[s][0] < summary_sentences <= sizes_ranges[s][1]):
      text_filename = str(pg_index) + ".txt"
      set_of_documents[s].append(text_filename)

if not os.path.exists('../data/extractive_summaries')
  os.makedirs('../data/extractive_summaries')

for t in range(4):
  scores = [[],[],[],[]]
  for s in range(4):
    size = sizes[s]
    for d in set_of_documents[s]:
      print(d)
      parser_b = PlaintextParser.from_file('../data/books/' + d, Tokenizer("english"))
      parser_s = PlaintextParser.from_file('../data/summaries/' + d, Tokenizer("english"))
      summary_0 = parser_s.document.sentences
      for t in [0]:
        if t==0:
          summarizer = LuhnSummarizer()
        elif t==1:
          summarizer = TextRankSummarizer()
        elif t==2:
          summarizer = LsaSummarizer()
        elif t==3:
          summarizer = LexRankSummarizer()
        summary = summarizer(parser_b.document,size)
        file = '../data/extractive_summaries/' + str(t) + d
        with open(file,'w') as f:
          for sentence in summary:
            f.write(str(sentence) + '\n')
        rouge_n_score = rouge_n(summary_0,summary)
        rouge_l_sentence_score = rouge_l_sentence_level(summary_0,summary)
        rouge_l_summary_score = rouge_l_summary_level(summary_0,summary)
        model1 = TfDocumentModel(str(summary_0), Tokenizer("en"))
        model2 = TfDocumentModel(str(summary), Tokenizer("en"))
        cosine_sim_score = cosine_similarity(model1, model2)
        scores[s].append([rouge_n_score,rouge_l_sentence_score,rouge_l_summary_score,cosine_sim_score])
        print([rouge_n_score,rouge_l_sentence_score,rouge_l_summary_score,cosine_sim_score])
    with open('extractive_summary_scores_' + str(t) + '_size' + str(size) + '.csv', 'w') as csvFile:
      writer = csv.writer(csvFile)
      writer.writerows(scores[s])
    csvFile.close()



