# entity extraction

import spacy
from fuzzywuzzy import fuzz
import operator

from data_download_and_stats import get_text_filename, get_chapter_filename, get_clean_book_filename

entity_types = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT",
                "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"]


def consolidate_list(long_list):
    sorted_long_list = sorted(
        long_list.items(), key=operator.itemgetter(1), reverse=True)
    matched_list = dict()
    matched_list[sorted_long_list[0][0]] = sorted_long_list[0][1]
    for new_item in sorted_long_list[1:]:
        match_found = find_matching_item(matched_list.keys(), new_item[0])
        if len(match_found) > 0:
            matched_list[match_found] = matched_list[match_found] + new_item[1]
        else:
            matched_list[new_item[0].replace('\n', '')] = new_item[1]
    return matched_list


def find_matching_item(item_list, new_item):
    match_found = ''
    match = 0
    for existing_item in item_list:
        if (fuzz.partial_ratio(existing_item, new_item) > (max(80, match))):
            match_found = existing_item
    return match_found


def remove_characters_from_entities(characters, entities):
    for character in characters:
        if character in entities:
            characters[character] = characters[character] + entities[character]
            entities.pop(character)
    return characters, entities


def find_entities_book(book_id):
    filename = get_clean_book_filename(book_id)
    nlp = spacy.load('en_core_web_sm')
    book = open(filename, 'r')
    book_text = ' '.join(book)
    if len(book_text) > 1000000:
        book_text = book_text[:1000000]
    doc = nlp(book_text)
    book.close()
    characters = dict()
    key_entities = dict()
    for ent in doc.ents:
        if (ent.label_ in entity_types):
            if (ent.text in key_entities):
                key_entities[ent.text] = key_entities[ent.text] + 1
            else:
                key_entities[ent.text] = 1
        if (ent.label_ == "PERSON"):
            if ent.text in characters:
                characters[ent.text] = characters[ent.text] + 1
            else:
                characters[ent.text] = 1
    matched_entities = consolidate_list(key_entities)
    matched_characters = dict()
    for character in characters.keys():
        matched_character = find_matching_item(
            matched_entities.keys(), character)
        if matched_character in matched_characters:
            matched_characters[matched_character] = matched_characters[matched_character] + \
                characters[character]
        elif len(matched_character) > 0:
            matched_characters[matched_character] = characters[character]
    matched_characters, matched_entities = remove_characters_from_entities(
        matched_characters, matched_entities)
    return matched_characters, matched_entities


def find_entities_chapter(book_id, chapter, book_characters, book_entities):
    filename = get_chapter_filename(book_id, chapter)
    nlp = spacy.load('en_core_web_sm')
    chapter = open(filename, 'r')
    chapter_text = ' '.join(chapter)
    doc = nlp(chapter_text)
    chapter.close()
    characters = dict()
    key_entities = dict()
    for ent in doc.ents:
        matched_entity = find_matching_item(book_entities.keys(), ent.text)
        matched_character = find_matching_item(
            book_characters.keys(), ent.text)
        if (len(matched_entity) > 0):
            if (matched_entity in key_entities):
                key_entities[matched_entity] = key_entities[matched_entity] + 1
            else:
                key_entities[matched_entity] = 1
        if (len(matched_character) > 0):
            if (matched_character in characters):
                characters[matched_character] = characters[matched_character] + 1
            else:
                characters[matched_character] = 1
    return characters, key_entities


def create_sentence(entities, about_book=True, about_characters=True):
    sentence = ''
    if (len(entities)>0):
        sentence = "The " + ("characters" if about_characters else "key terms") + " in this " + \
            ("book" if about_book else "chapter") + " are "
        sorted_entities = sorted(
            entities.items(), key=operator.itemgetter(1), reverse=True)
        num_to_print = (min(10, len(sorted_entities)-1)
                    if about_book else min(5, len(sorted_entities)-1))
        for entity in sorted_entities[:num_to_print-1]:
            sentence = sentence + entity[0] + ', '
        if (len(sorted_entities) > 1):
            sentence = sentence + "and "
        sentence = sentence + sorted_entities[num_to_print-1][0] + '.'
    return sentence


def test_entity_extraction_sentences():
    filename = '../data/books/11.txt'
    chapter_filename = '../data/book_chapters/11-1.txt'
    book_characters, book_key_entities = find_entities_book(filename)
    chapter_characters, chapter_key_entities = find_entities_chapter(chapter_filename,
                                                                     book_characters, book_key_entities)

    print(create_sentence(book_characters, about_book=True, about_characters=True))
    print(create_sentence(book_key_entities,
                          about_book=True, about_characters=False))
    print(create_sentence(chapter_characters,
                          about_book=False, about_characters=True))
    print(create_sentence(chapter_key_entities,
                          about_book=False, about_characters=False))
