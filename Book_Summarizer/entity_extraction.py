"""
This file has the functions for the entity extracter.
Create an entity summary from chapters of a large document.
"""

from spacy import load
from fuzzywuzzy import fuzz
import operator
import csv

from data import get_data_filename

entity_types = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT",
                "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"]


def consolidate_list(long_list):
    """
    Consolidate a long list by matching similar items.

    Parameters:
    long_list: a list of characters or key items

    Returns:
    list: a consolidated list where similar items are combined
    """
    sorted_long_list = sorted(
        long_list.items(), key=operator.itemgetter(1), reverse=True)
    matched_list = dict()
    matched_list[sorted_long_list[0][0]] = sorted_long_list[0][1]
    for new_item in sorted_long_list[1:]:
        match_found = find_matching_item(matched_list.keys(), new_item[0])
        if len(match_found) > 0:
            matched_list[match_found] = matched_list[match_found] + new_item[1]
        else:
            matched_list[new_item[0]] = new_item[1]
    return matched_list


def find_matching_item(item_list, new_item):
    """
    Find matching items according to similarity of the text string

    Parameters:
    item_list: a list of items
    new_item: a potential new item to add to the list

    Returns:
    int: the index when the new_item is a match to an item in the item_list
    """
    match_found = ''
    match = 0
    for existing_item in item_list:
        if (fuzz.partial_ratio(existing_item, new_item) > (max(80, match))):
            match_found = existing_item
    return match_found


def remove_characters_from_entities(characters, entities):
    """
    Consolidate character and entities found by removing characters from entities.

    Parameters:
    characters: list of the characters found
    entities: list of the entities found    

    Returns: 
    updated characters and entities lists
    """
    for character in characters:
        if character in entities:
            characters[character] = characters[character] + entities[character]
            entities.pop(character)
    return characters, entities


def find_entities_book(book_id):
    """
    Use spacy to find the entities in the book.

    Separates entities found by spacy into characters and key words.
    Performs some formatting on the entities found to remove returns and whitespace.
    Consolidates lists so that similar entities are joined into one entity.

    Parameters:
    book_id: (int) the book identifier

    Returns:
    list: characters
    list: key words
    """
    filename = get_data_filename(book_id, 'books')
    try:
        nlp = load('en_core_web_lg')
    except:
        nlp = load('en_core_web_sm')
    with open(filename, 'r') as book:
        book_text = ' '.join(book)
        if len(book_text) > 1000000:
            book_text = book_text[:1000000]
        doc = nlp(book_text)
    characters = dict()
    key_entities = dict()
    for ent in doc.ents:
        new_entity = ent.text.replace('\n', '')
        new_entity = new_entity.strip()
        if len(new_entity) > 0:
            if (ent.label_ in entity_types):
                if (new_entity in key_entities):
                    key_entities[new_entity] = key_entities[new_entity] + 1
                else:
                    key_entities[new_entity] = 1
            if (ent.label_ == "PERSON"):
                if new_entity in characters:
                    characters[new_entity] = characters[new_entity] + 1
                else:
                    characters[new_entity] = 1
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
    """
    Find the entities for a chapter, matching the entities to the book entities.

    Parameters:
    book_id: (int) the book identifier
    chapter: the chapter to find the entities in
    book_characters: the characters that were found in the whole book
    book_entities: the key words that were found in the whole book

    Returns:
    list: characters
    list: key words
    """
    filename = get_data_filename(book_id, 'book_chapters', chapter)
    try:
        nlp = load('en_core_web_lg')
    except:
        nlp = load('en_core_web_sm')
    with open(filename, 'r') as chapter:
        chapter_text = ' '.join(chapter)
        doc = nlp(chapter_text)
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
    """
    Create a sentence for the entity summary.

    Parameters:
    entities: the entities to list in the sentence
    about_book: if the sentence is about a book, include up to 10 entities, otherwise 5 entities
    about_characters: if the entities are characters, otherwise key terms

    Returns:
    str: the created sentences
    """
    sentence = ''
    if (len(entities) > 0):
        sentence = "Characters: " if about_characters else "Key terms: "
        sorted_entities = sorted(
            entities.items(), key=operator.itemgetter(1), reverse=True)
        num_to_print = (min(10, len(sorted_entities)-1)
                        if about_book else min(5, len(sorted_entities)-1))
        for entity in sorted_entities[:num_to_print-1]:
            sentence = sentence + entity[0] + ', '
        sentence = sentence + sorted_entities[num_to_print-1][0] + '.'
    return sentence


def save_sorted_entities_book(characters, entities, book_id):
    """
    Saves the book entities in a csv file, begins the file.

    Parameters:
    characters: list of the characters in the book
    entities: list of the key words in the book
    book_id: (int) the book identifier
    """
    sorted_characters = sorted(
        characters.items(), key=operator.itemgetter(1), reverse=True)
    sorted_entities = sorted(
        entities.items(), key=operator.itemgetter(1), reverse=True)
    with open('../results/summaries/' + str(book_id) + '.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(sorted_characters)
        writer.writerows(sorted_entities)


def save_sorted_entities_chapter(characters, entities, book_id, chapter):
    """
    Saves the chapter entities in a csv file, appends to the existing file.

    Parameters:
    characters: list of the characters in the chapter
    entities: list of the key words in the chapter
    book_id: (int) the book identifier
    chapter: (int) the chapter number
    """
    sorted_characters = sorted(
        characters.items(), key=operator.itemgetter(1), reverse=True)
    sorted_entities = sorted(
        entities.items(), key=operator.itemgetter(1), reverse=True)
    with open('../results/summaries/' + str(book_id) + '.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows([['Chapter ' + str(chapter)]])
        writer.writerows(sorted_characters)
        writer.writerows(sorted_entities)
