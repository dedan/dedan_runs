#!/usr/bin/env python
# encoding: utf-8
"""
sparql_sim_matrix.py

compute similarity matrices for the terms I received from wikipedia from 
the sparqle queries. Created bz sparql_wiki.py

Created by Stephan Gabler on 2011-03-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import logging
import pickle
import numpy as np
from gensim.models.log_entropy_model import LogEntropyModel
from gensim import utils
from gensim.corpora.dictionary import Dictionary
from gensim import matutils

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level = logging.DEBUG)

word_ids_extension = '_wordids.txt'
base_path = '/Users/dedan/projects/mpi/data/'
results_path = base_path + 'results/'
corpus_path     = 'corpora/wiki/wiki-mar2008/'
corpus_name     = 'head500.noblanks.cor'
working_corpus  = base_path + corpus_path + corpus_name
model_name = 'head500.noblanks.cor_log_ent.model'

matrices = {}

logging.info('load the articles pickle')
with open(results_path + "sparql_wiki.pickle", 'r') as f:
    articles = pickle.load(f)

logging.info('load the dictionary')
id2word, word2id = utils.loadDictionary(working_corpus + word_ids_extension)
dictionary = Dictionary(word2id=word2id, id2word=id2word)

logging.info('load the log_ent model')
log_ent = LogEntropyModel.load(results_path + model_name)

for key in articles.iterkeys():

    logging.info('current term: %s' % key)

    term_list = articles[key].keys()
    text_list = [dictionary.doc2bow(article['text'], allowUpdate=False, returnMissingWords=False) 
            for article in articles[key].values()]
    sim_matrix = np.zeros((len(text_list), len(text_list)))

    logging.info('transform the textlist')
    text_list = log_ent[text_list]

    logging.info('compute similarity matrix')
    for i, par1 in enumerate(text_list):
        for j, par2 in enumerate(text_list):
            sim_matrix[i, j] = matutils.cossim(par1, par2)
    matrices[key] = {}
    matrices[key]['term_list'] = term_list
    matrices[key]['sim_matrix'] = sim_matrix
    assert np.shape(sim_matrix)[0] == len(term_list)
