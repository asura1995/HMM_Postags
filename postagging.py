#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import codecs
from collections import defaultdict
from math import log


def read_from_train():
    with codecs.open('train.txt', 'r', 'gb18030') as fr:
        train_data = fr.read()
    words_list = re.findall(r'(\S+)/\S+', train_data)
    postags_list = re.findall(r'\S+/(\S+)', train_data)
    return words_list, postags_list


def calc_trans_prob(postags_list):
    unigram_dict = {}
    bigram_dict = {}
    for postag in postags_list:
        if postag not in unigram_dict.keys():
            unigram_dict[postag] = 0
        unigram_dict[postag] += 1

    for i in range(1, len(postags_list)):
        bigram = postags_list[i - 1] + "_" + postags_list[i]
        if bigram not in bigram_dict.keys():
            bigram_dict[bigram] = 0
        bigram_dict[bigram] += 1

    postags_trans_dict = {}
    postags_start_dict = {}

    total_unigram = sum(unigram_dict.values())
    for unigram, freq in unigram_dict.items():
        postags_start_dict[unigram] = log(
            (freq + 0.01) / (1.01 * total_unigram))
    postags_start_dict["^ZERO$"] = log(0.01 / (1.01 * total_unigram))

    total_bigram = sum(bigram_dict.values())
    for bigram, freq in bigram_dict.items():
        postags_trans_dict[bigram] = log((freq + 0.01) / (1.01 * total_bigram))
    postags_trans_dict["^ZERO$"] = log(0.01 / (1.01 * total_bigram))

    return postags_trans_dict, postags_start_dict


def calc_emit_prob(words_list, postags_list):
    pos_words_emit_dict = defaultdict(dict)
    for i in range(len(words_list)):
        postag = postags_list[i]
        word = words_list[i]
        if postag not in pos_words_emit_dict.keys():
            pos_words_emit_dict[postag] = {}
        if word not in pos_words_emit_dict[postag].keys():
            pos_words_emit_dict[postag][word] = 0
        pos_words_emit_dict[postag][word] += 1

    for p, w_f in pos_words_emit_dict.items():
        total_freq = sum(w_f.values())
        for w, f in pos_words_emit_dict[p].items():
            pos_words_emit_dict[p][w] = log((f + 0.01) / (1.01 * total_freq))
    pos_words_emit_dict["NAN"]["^ZERO$"] = log(0.01 / (1.01 * total_freq))

    word_postags_dict = defaultdict(list)
    for i in range(len(words_list)):
        if words_list[i] not in word_postags_dict.keys():
            word_postags_dict[words_list[i]] = []
        if postags_list[i] not in word_postags_dict[words_list[i]]:
            word_postags_dict[words_list[i]].append(postags_list[i])

    return pos_words_emit_dict, word_postags_dict


def write2file(content, filename):
    if isinstance(content, type([])):
        with codecs.open(filename, 'w', 'utf-8') as fw1:
            fw1.write(' '.join(content))

    if isinstance(content, type({})):
        new_json = json.dumps(content)
        with codecs.open(filename, 'w', 'utf-8') as fw2:
            fw2.write(new_json)


def train():
    words_list, postags_list = read_from_train()
    postags_trans_dict, postags_start_dict = calc_trans_prob(postags_list)
    pos_words_emit_dict, word_postags_dict = calc_emit_prob(
        words_list, postags_list)
    write2file(words_list, "words_list.txt")
    write2file(word_postags_dict, "word_postags_dict.txt")
    write2file(postags_trans_dict, "postags_trans_dict.txt")
    write2file(postags_start_dict, "postags_start_dict.txt")
    write2file(pos_words_emit_dict, "postags_emit_dict.txt")
    return words_list, word_postags_dict, postags_trans_dict, postags_start_dict, pos_words_emit_dict


def read_trained_data(filename):
    file_type = filename.split('_')[-1]
    if file_type == "list.txt":
        with codecs.open(filename, 'r', 'utf-8') as fr1:
            file_content = fr1.read()
        list_from_file = file_content.split(' ')
        return list_from_file

    if file_type == "dict.txt":
        with codecs.open(filename, 'r', 'utf-8') as fr2:
            file_content = fr2.read()
        dict_from_file = json.loads(file_content)
        return dict_from_file


def segment(line, words_set):
    word_in_line = []
    while len(line) > 0:
        a_border = 0
        b_border = len(line)
        for i in range(len(line[a_border:b_border])):
            tmp_word = line[a_border + i: b_border]
            if tmp_word in words_set or len(tmp_word) == 1:
                word_in_line.insert(0, tmp_word)
                split_num = a_border + i
                break
        line = line[:split_num]
    return word_in_line


def postagging(test_words_list, word_postags_dict, postags_trans_dict, postags_start_dict, postags_emit_dict):
    magnet_list = []
    postag_magnet = {}
    for word in test_words_list:
        postag_magnet = defaultdict(dict)
        postags = word_postags_dict[word] if word in word_postags_dict.keys() else ["DNF"]
        for postag in postags:
            postag_magnet[postag] = [0.0, ""]
        magnet_list.append(postag_magnet)

    for i in range(len(magnet_list)):
        if i == 0:
            for postag, pv in magnet_list[i].items():
                start_prob = postags_start_dict[postag] if postag in postags_start_dict.keys(
                ) else postags_start_dict["^ZERO$"]
                emit_prob = postags_emit_dict[postag][word]\
                if postag in postags_emit_dict.keys() and \
                word in postags_emit_dict[postag].keys() \
                else postags_emit_dict["NAN"]["^ZERO$"]
                value = start_prob + emit_prob
                magnet_list[i][postag][0] = value
        else:
            for postag, pv in magnet_list[i].items():
                tmp_value = -100000
                tmp_pointer = ""
                for pre_postag, pre_pv in magnet_list[i - 1].items():
                    bigram_postag = pre_postag + '_' + postag
                    trans_prob = postags_trans_dict[bigram_postag] \
                    if bigram_postag in postags_trans_dict.keys(
                    ) else postags_trans_dict["^ZERO$"]
                    emit_prob = postags_emit_dict[postag][word] \
                    if postag in postags_emit_dict.keys() and \
                    word in postags_emit_dict[postag].keys() \
                    else postags_emit_dict["NAN"]["^ZERO$"]
                    pre_value = magnet_list[i - 1][pre_postag][0]
                    value = pre_value + trans_prob + emit_prob
                    if value > tmp_value:
                        tmp_value = value
                        tmp_pointer = pre_postag
                magnet_list[i][postag][0] = tmp_value
                magnet_list[i][postag][1] = tmp_pointer

    postags_list = []
    last_postag = max(magnet_list[-1].keys(),
                      key=lambda x: magnet_list[-1][x][0])
    postags_list.append(last_postag)
    pre_postag = magnet_list[-1][last_postag][1]
    postags_list.insert(0, pre_postag)
    for i in range(1, len(magnet_list)):
        pre_postag = magnet_list[-1 - i][pre_postag][1]
        if pre_postag != "":
            postags_list.insert(0, pre_postag)
    if len(postags_list) != len(test_words_list):
        print(postags_list)
        print("Failed, postags_list nq test_words_list")
    test_postags_list = []
    for i in range(len(postags_list)):
        word_postag = test_words_list[i] + '/' + postags_list[i]
        test_postags_list.append(word_postag)
    return test_postags_list


def core(textfile):
    try:
        words_list = read_trained_data("words_list.txt")
        word_postags_dict = read_trained_data("word_postags_dict.txt")
        postags_trans_dict = read_trained_data("postags_trans_dict.txt")
        postags_start_dict = read_trained_data("postags_start_dict.txt")
        postags_emit_dict = read_trained_data("postags_emit_dict.txt")
    except:
        words_list, word_postags_dict, postags_trans_dict, postags_start_dict, pos_words_emit_dict = train()
    words_set = set(words_list)
    with open(textfile, 'r') as fr:
        postag_sentences = []
        for line in fr:
            sentence = line.strip()
            test_words_list = segment(sentence, words_set)
            test_postags_list = postagging(
                test_words_list, word_postags_dict, postags_trans_dict, postags_start_dict, postags_emit_dict)
            postag_sentences.append(test_postags_list)
    with open("result_" + textfile, 'w') as fw:
        for s in postag_sentences:
            fw.write(' '.join(s) + '\n')


if __name__ == "__main__":
    textfile = "test.txt"
    core(textfile)
