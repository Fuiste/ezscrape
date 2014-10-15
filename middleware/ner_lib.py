# -*- coding: utf-8 -*-
import re
import os
from middleware.text_format import replace_special_chars_in_text
import urllib
import urllib2
import json


__author__ = "fuiste"

middleware_dir = os.path.dirname(__file__)
parse_url = "http://distill-server.herokuapp.com/parse"


# Old noun phrase extraction method.
def extract_noun_phrases(pos_str):
    new_noun_phrase_regex = r"\(NP\s(?P<noun_phrase>(\([A-Z\$]+\s\w{4,}\)(\s)?)+)\)"
    pos_regex = r"(((\s)?\([A-Z\$]+)|(\)(\s)?))"
    noun_phrases = []
    matches = list(re.findall(new_noun_phrase_regex, pos_str))
    for m in matches:
        noun_phrase = re.sub(pos_regex, "", m[0]).strip()
        if len(noun_phrase.split(" ")) > 1:
            noun_phrases.append(noun_phrase)
    return noun_phrases


def pos_tag_text_documents(text_documents):
    formatted_text = []#replace_special_chars_in_text(text_documents=text_documents, lowercase=False)
    for doc in text_documents:
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', doc["text"])
        formatted_text.append({"sentences": sentences, "id": doc["id"]})
    doc_copy = []
    # maps noun phrases to their documents
    noun_phrase_map = {}
    formatted_cuts = []
    for t in formatted_text:
        if len(formatted_cuts):
            found = False
            for c in formatted_cuts:
                if len(c) < 4:
                    c.append(t)
                    found = True
            if not found:
                formatted_cuts.append([t])
        else:
            formatted_cuts.append([t])
    noun_phrases = []
    total_c = len(formatted_text)
    cur_c = 0
    for cut in formatted_cuts:
        request_object = urllib2.Request(parse_url, json.dumps(cut), {"Content-Type": "application/json"})
        response = urllib2.urlopen(request_object)
        html_arr = json.loads(response.read())
        cur_c = cur_c + len(cut)
        print "{0} / {1} reviews tagged".format(cur_c, total_c)
        noun_phrases.extend(html_arr)
    print "Tagging done, mapping phrases to topics"
    if noun_phrases:
        for p in noun_phrases:
            phrases = extract_noun_phrases(p["phrase"])
            for ph in phrases:
                if ph not in noun_phrase_map:
                    noun_phrase_map[ph] = set()
                noun_phrase_map[ph].add(p["id"])
    noun_phrase_list =[]
    for noun_phrase, id_set in noun_phrase_map.iteritems():
        noun_phrase_list.append({"noun_phrase": noun_phrase, "ids": list(id_set)})
    noun_phrase_list = sorted(noun_phrase_list, key=lambda n: len(n["ids"]), reverse=True)
    print "\nTop 10 noun phrases for this group:"
    for n in noun_phrase_list[:20]:
        print "\t" + n["noun_phrase"] + " - {0}".format(n["ids"])
    return noun_phrase_list
