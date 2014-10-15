# -*- coding: utf-8 -*-
import re
import string

__author__ = "MDee"

ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fify", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"])


def split_text_into_word_bags(text_documents, use_stop_words=True):
    """Takes a list of strings and splits each into a list of words used

    Arguments:
        text_documents: A list of strings to split
    Returns:
        A list of lists, each entry is a word in the original corresponding string (["My car is cool"] -> [["My", "car", "is", "cool"]]
    """
    # Break each document up into a list of words, and throw any away that are stop words. Strip whitespace
    if use_stop_words:
        texts = [[word.strip() for word in document.split() if word not in ENGLISH_STOP_WORDS] for document in text_documents]
    else:
        texts = [[word.strip() for word in document.split()] for document in text_documents]
    return texts


def replace_chars(regex, replacement, text):
    """Replaces characters in given string

    Args:
        regex: a raw string or compiled regex
        replacement: a raw string of what goes in where matches are found
        text: the string to be modified
    Returns:
        A new string with replacements
    """
    return re.sub(regex, replacement, text)


def replace_special_chars_in_text(text_documents, lowercase=True):
    """Replaces all special chars in supplied text

    Arguments:
        text_documents: A list of strings to scrub
    Returns:
        A list of strings with special chars replaced
    """
    quote_backslash_regex = r"[{0}]".format(r"'\/\"`")
    punct_regex = r"[{0}]".format(string.punctuation)
    texts = [replace_chars(regex=quote_backslash_regex, replacement=r"", text=d) for d in text_documents]
    # Replace all &nbsp; with " "
    texts = [replace_chars(regex=r"&nbsp;", replacement=r" ", text=d) for d in texts]
    # Replace all punctuation with a space
    texts = [replace_chars(regex=punct_regex, replacement=r" ", text=d) for d in texts]
    if lowercase:
        texts = [t.lower() for t in texts]
    return texts