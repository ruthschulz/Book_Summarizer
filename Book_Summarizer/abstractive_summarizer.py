# abstractive summarizer
# create an abstractive summary from chapters of a large document

import re
import os
import sys
import shutil
import spacy
import pathlib
from regex import Regex, UNICODE, IGNORECASE
from extractive_summarizer import create_extractive_summary_book
from data_download_and_stats import get_chapter_filename, get_extractive_summary_filename, get_abstractive_summary_filename
from nats.pointer_generator_network.model import *
import argparse

CONTRACTIONS = (r'^\p{Alpha}+(\'(ll|ve|re|[dsm])|n\'t)$')
CURRENCY_OR_INIT_PUNCT = (r'^[\p{Sc}\(\[\{\¿\¡]+$')
NOPRESPACE_PUNCT = (r'^[\,\.\?\!\:\;\\\%\}\]\)]+$')
FINAL_PUNCT = (r'([\.!?])([\'\"\)\]\p{Pf}\%])*$')


def tokenize_book(input_data):
    nlp = spacy.load('en_core_web_sm', disable=['tagger', 'ner'])
    article = input_data
    summary = 'summary'
    title = 'title'
    if article == None or summary == None or title == None:
        return ''
    article = nlp(article)
    summary = nlp(summary)
    title = nlp(title)
    sen_arr = []
    for sen in article.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        sen = ' '.join(sen)
        sen_arr.append(sen)
    article = ' '.join(sen_arr)
    sen_arr = []
    for sen in summary.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        sen = ['<s>']+sen+['</s>']
        sen = ' '.join(sen)
        sen_arr.append(sen)
    summary = ' '.join(sen_arr)
    sen_arr = []
    for sen in title.sents:
        sen = [k.text for k in sen if '\n' not in k.text]
        sen = ['<s>']+sen+['</s>']
        sen = ' '.join(sen)
        sen_arr.append(sen)
    title = ' '.join(sen_arr)
    sen_arr = [title, summary, article]
    return title + summary + '<sec>' + article


def tokenize_file(file_in,file_out):
    # book may also be extractive summary
    book = open(file_in, 'rb')
    book_text = ''
    # remove special characters and make lower case
    for line in book:
        line = line.decode('utf-8').encode('ascii', 'ignore').decode('ascii')
        book_text = book_text + ' ' + line.lower()
    book.close()
    if len(book_text) > 1000000:
        book_text = book_text[:1000000]
    # tokenize using spacy and add <s>, </s>, and <sec> tags
    tokenized_book = tokenize_book(book_text)
    processed_book = open(file_out,'w')
    processed_book.write(tokenized_book)
    processed_book.close()


def tokenize_chapter_summaries(book_id):
    if not os.path.exists('../results/abstractive_summaries'):
        os.makedirs('../results/abstractive_summaries')
    chapter = 0
    extractive_summary_filename = get_extractive_summary_filename(book_id,chapter)
    abstractive_summary_filename = get_abstractive_summary_filename(book_id,chapter)
    book_abstractive_summary_filename = get_abstractive_summary_filename(book_id)
    path = pathlib.Path(extractive_summary_filename)
    book_summary = open(book_abstractive_summary_filename, 'w')
    while path.exists():
        tokenize_file(extractive_summary_filename, abstractive_summary_filename)
        chapter_summary = open(abstractive_summary_filename,'r')
        for l in chapter_summary:
            book_summary.write(l)
        book_summary.write('\n')
        chapter_summary.close()
        chapter += 1
        extractive_summary_filename = get_extractive_summary_filename(book_id,chapter)
        abstractive_summary_filename = get_abstractive_summary_filename(book_id,chapter)
        path = pathlib.Path(extractive_summary_filename)
    book_summary.close()


# adapted from:
# https://github.com/ufal/mtmonkey/blob/master/worker/src/util/fileprocess.py
def detokenize_summary(filename_in,filename_out):
    file_in = open(filename_in, 'r')
    file_out = open(filename_out, 'w')
    lines = []
    for line in file_in:
        line = line.rstrip('\r\n')
        line = line.replace('<s> summary </s>','')
        line = line.replace('<s> title </s>','')
        line = line.replace('<s>','')
        line = line.replace('</s>','')
        line = line.replace('<sec>','\n')
        line = line.replace('<stop>','')
        line = line.replace('<pad>','')
        line = detokenize_line(line)
        file_out.write(line)
        lines.append(line)
    file_in.close()
    file_out.close()
    return lines

# adapted from:
# https://github.com/ufal/mtmonkey/blob/master/worker/src/util/detokenize.py
def detokenize_line(line):
    """\
    Detokenize the given text using current settings.
    """
    # split text
    words = line.split(' ')
    # paste text back, omitting spaces where needed 
    text = ''
    pre_spc = ' '
    quote_count = {'\'': 0, '"': 0, '`': 0}
    capitalize_next = True
    text_len_last_final_punct = 0
    for pos, word in enumerate(words):
        # no space after currency and initial punctuation
        if Regex(CURRENCY_OR_INIT_PUNCT).match(word):
            text += pre_spc + word
            pre_spc = ''
        # no space before commas etc. (exclude some punctuation for French)
        elif Regex(NOPRESPACE_PUNCT).match(word):
            text += word
            pre_spc = ' '
        # contractions with comma or hyphen 
        elif word in "'-–" and pos > 0 and pos < len(words) - 1 \
                and Regex(CONTRACTIONS).match(''.join(words[pos - 1:pos + 2])):
            text += word
            pre_spc = ''
        # handle quoting
        elif word in '\'"„“”‚‘’`':
            # detect opening and closing quotes by counting 
            # the appropriate quote types
            quote_type = word
            if quote_type in '„“”':
                quote_type = '"'
            elif quote_type in '‚‘’':
                quote_type = '\''
            # special case: possessives in English ("Jones'" etc.)                    
            if text.endswith('s'):
                text += word
                pre_spc = ' '
            # really a quotation mark
            else:
                # opening quote
                if quote_count[quote_type] % 2 == 0:
                    text += pre_spc + word
                    pre_spc = ''
                # closing quote
                else:
                    text += word
                    pre_spc = ' '
                quote_count[quote_type] += 1
        # contractions where comma or hyphen is already joined to following letters
        elif word[0] in "'-–" and pos > 0 and pos < len(words) - 1 \
                and Regex(CONTRACTIONS).match(''.join(words[pos - 1:pos + 1])):
            text += word
            pre_spc = ' '
        # keep spaces around normal words
        else:
            if capitalize_next:
                capitalize_next = False
                if len(word)==1:
                    word = word.upper()
                else:
                    word = word[0].upper() + word[1:]
            if word == 'i':
                word = word.upper()
            text += pre_spc + word
            pre_spc = ' '
        if Regex(FINAL_PUNCT).match(word):
            capitalize_next = True
            text_len_last_final_punct = len(text)
    # strip leading/trailing space
    text = text.strip()
    text = text[:text_len_last_final_punct]
    return text


def create_abstractive_summary_book(book_id):
    # create extractive summaries for chapters
    create_extractive_summary_book(book_id, 5)
    # process extractive summaries into test.txt for input to abstractive summarizer
    # (lower case, remove special characters, tokenize)
    tokenize_chapter_summaries(book_id)
    # run abstractive summarizer
    if not os.path.exists('../sum_data'):
        os.makedirs('../sum_data')
    shutil.copyfile(get_abstractive_summary_filename(book_id), '../sum_data/test.txt')
    parser = argparse.ArgumentParser()
    '''
    Use in the framework and cannot remove.
    '''
    parser.add_argument('--task', default='train',
                    help='train | validate | rouge | beam')

    parser.add_argument('--data_dir', default='../sum_data/',
                    help='directory that store the data.')
    parser.add_argument('--file_corpus', default='train.txt',
                    help='file store training documents.')
    parser.add_argument('--file_val', default='val.txt', help='val data')

    parser.add_argument('--n_epoch', type=int, default=35,
                    help='number of epochs.')
    parser.add_argument('--batch_size', type=int, default=16, help='batch size.')
    parser.add_argument('--checkpoint', type=int, default=100,
                    help='How often you want to save model?')
    parser.add_argument('--val_num_batch', type=int,
                    default=30, help='how many batches')
    parser.add_argument('--nbestmodel', type=int, default=10,
                    help='How many models you want to keep?')

    parser.add_argument('--continue_training', type=str2bool,
                    default=True, help='Do you want to continue?')
    parser.add_argument('--train_base_model', type=str2bool, default=False,
                    help='True: Use Pretrained Param | False: Transfer Learning')
    parser.add_argument('--use_move_avg', type=str2bool,
                    default=False, help='move average')
    parser.add_argument('--use_optimal_model', type=str2bool,
                    default=True, help='Do you want to use the best model?')
    parser.add_argument('--model_optimal_key', default='0,0', help='epoch,batch')
    parser.add_argument('--is_lower', type=str2bool, default=True,
                    help='convert all tokens to lower case?')
    '''
    User specified parameters.
    '''
    parser.add_argument('--device', default=torch.device("cuda:0"), help='device')
    parser.add_argument('--file_vocab', default='vocab',
                    help='file store training vocabulary.')

    parser.add_argument('--max_vocab_size', type=int, default=50000,
                    help='max number of words in the vocabulary.')
    parser.add_argument('--word_minfreq', type=int,
                    default=5, help='min word frequency')

    parser.add_argument('--emb_dim', type=int, default=128,
                    help='source embedding dimension')
    parser.add_argument('--src_hidden_dim', type=int,
                    default=256, help='encoder hidden dimension')
    parser.add_argument('--trg_hidden_dim', type=int,
                    default=256, help='decoder hidden dimension')
    parser.add_argument('--src_seq_lens', type=int, default=400,
                    help='length of source documents.')
    parser.add_argument('--trg_seq_lens', type=int, default=100,
                    help='length of target documents.')

    parser.add_argument('--rnn_network', default='lstm', help='gru | lstm')
    parser.add_argument('--attn_method', default='luong_concat',
                    help='luong_dot | luong_concat | luong_general')
    parser.add_argument('--repetition', default='vanilla',
                    help='vanilla | temporal | asee (coverage). Repetition Handling')
    parser.add_argument('--pointer_net', type=str2bool,
                    default=True, help='Use pointer network?')
    parser.add_argument('--oov_explicit', type=str2bool,
                    default=True, help='explicit OOV?')
    parser.add_argument('--attn_decoder', type=str2bool,
                    default=True, help='attention decoder?')
    parser.add_argument('--share_emb_weight', type=str2bool,
                    default=True, help='share_emb_weight')

    parser.add_argument('--learning_rate', type=float,
                    default=0.0001, help='learning rate.')
    parser.add_argument('--grad_clip', type=float, default=2.0,
                    help='clip the gradient norm.')

    parser.add_argument('--file_test', default='test.txt', help='test data')
    parser.add_argument('--file_output', default='summaries.txt',
                    help='test output file')
    parser.add_argument('--beam_size', type=int, default=5, help='beam size.')
    parser.add_argument('--test_batch_size', type=int, default=1,
                    help='batch size for beam search.')
    parser.add_argument('--copy_words', type=str2bool,
                    default=True, help='Do you want to copy words?')
    # for app
    parser.add_argument('--app_model_dir', default='../../pg_model/',
                    help='directory that stores models.')
    parser.add_argument('--app_data_dir', default='../../',
                    help='directory that stores data.')
    args = parser.parse_args([])
    model = modelPointerGenerator(args)
    model.test()
    # process abstractive summary summaries.txt into abstractive summary
    # (detokenize)
    return(detokenize_summary('../nats_results/summaries.txt',get_abstractive_summary_filename(book_id)))
