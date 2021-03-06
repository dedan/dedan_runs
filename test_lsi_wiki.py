#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

import numpy as np
import logging

from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.models.log_entropy_model import LogEntropyModel
from gensim.parsing import preprocessing
from gensim import utils
from gensim import models
from gensim import similarities
from gensim import matutils
from gensim.corpora import MmCorpus

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level = logging.DEBUG)
logging.info("running %s" % ' '.join(sys.argv))

# configuration
num_topics         = 50
word_ids_extension = '_wordids.txt'
log_ent_extension  = '_log_ent.model'
lsi_extension      = '_lsi.model'

# paths
base_path       = '/mnt/Data/'
corpus_name     = 'stemmedAllCleaned-fq10-cd10.noblanks.cor'
# base_path       = '/Users/dedan/projects/mpi/data/'
corpus_path     = 'corpora/wiki/wiki-mar2008/'
# corpus_name     = 'head500.noblanks.cor'
working_corpus  = base_path + corpus_path + corpus_name
human_data_file = base_path + "corpora/lee/lee-doc2doc/similarities0-1.txt"
lee_corpus      = base_path + "corpora/lee/lee.cor"
result_path     = base_path + "results/"


logging.info('loading word mapping')
id2word, word2id = utils.loadDictionary(working_corpus + word_ids_extension)
dictionary = Dictionary(word2id=word2id, id2word=id2word)

logging.info('loading corpus')
corpus_bow = MmCorpus(working_corpus + '_bow.mm')

logging.info("create log_ent model and save it to disk")
tfidf = LogEntropyModel(corpus_bow, id2word=dictionary.id2token, normalize = True)
tfidf.save(result_path + corpus_name + log_ent_extension)

logging.info('load smal lee corpus and preprocess')
raw_lee_texts = utils.get_txt(lee_corpus)
preproc_lee_texts = preprocessing.preprocess_documents(raw_lee_texts)
bow_lee_texts = [dictionary.doc2bow(text,
                                    allowUpdate=False,
                                    returnMissingWords=False)
                for text in preproc_lee_texts]

logging.info('initialize LSI model')
lsi = models.LsiModel(tfidf[corpus_bow], id2word=id2word, numTopics=num_topics)
lsi.save((result_path + corpus_name + '_%i_ent'  + lsi_extension) % num_topics)
logging.info('transforming small lee corpus (LSI)')
corpus_lsi = lsi[tfidf[bow_lee_texts]]

# # compute pairwise similarity matrix of transformed corpus
sim_matrix = np.zeros((len(corpus_lsi), len(corpus_lsi)))
for i, par1 in enumerate(corpus_lsi):
    for j, par2 in enumerate(corpus_lsi):
        sim_matrix[i, j] = matutils.cossim(par1, par2)

# read the human similarity data and flatten upper triangular
human_sim_matrix = np.loadtxt(human_data_file)
human_sim_vector = utils.array2utrilst(human_sim_matrix)
sim_vector = utils.array2utrilst(sim_matrix)

# compute correlations
cor = np.corrcoef(sim_vector, human_sim_vector)
print cor[0, 1]
