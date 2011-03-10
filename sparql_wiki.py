#!/usr/bin/env python
# encoding: utf-8
"""
sparql_wiki.py

this script is used to crawl wikipedia articles according to keywords
which were collected from sparql queries

Created by Stephan Gabler on 2011-03-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from urllib import FancyURLopener
from BeautifulSoup import BeautifulStoneSoup as BSS
import glob
import codecs
import os
from gensim.corpora import wikicorpus
from gensim.parsing.preprocessing import preprocess_string
import pickle
import unicodedata


# init and config
base_path = '/Users/dedan/projects/mpi/data/'
results_path = base_path + 'results/'
folder_path = base_path + 'corpora/queries-16-better/'
articles = {}
all_missing = []

# query url to the wikipedia api
query_base = "http://en.wikipedia.org/w/api.php?action=query&titles=%s" \
                + "&format=xml"\
                + "&redirects"


# create a new URL opener class because websites like google or wikipedia
# reject queries from unknown user agents
# solution from here: http://wolfprojects.altervista.org/changeua.php
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0'
myopener = MyOpener()


# get all txt files in a folder and iterate over them
filelist = glob.glob(folder_path + "*.txt");
for f in filelist:

    # get the word we are working on
    f_name = os.path.basename(f)
    k_word = os.path.splitext(f_name)[0]
    print "working on file: %s" % f_name


    # try to convert the word into ascii for the http query
    file_obj = codecs.open(f, "r", "utf-16" )
    counter = 0
    words = []
    for w in file_obj.readlines():
        try:
            s = w.strip().decode('ascii')
            words.append(s)
        except Exception:
            counter += 1
    print "\t%d words contained non ascii characters and are ommited" % counter


    # the wikipedia api restricts queries to a length of 50
    print "\tfound %d words in file" % len(words)
    for i in range((len(words) / 50)+1):
                
        # create the query and parse it
        query   = query_base % "|".join(words[(i*50):(i*50)+50])
        
        text    = myopener.open(query).read()
        soup    = BSS(text, convertEntities=BSS.ALL_ENTITIES)
        cont    = soup.api.query
    
        # collect all missing words
        missing = cont.pages.findAll(missing=True)
        all_missing.append([m['title'] for m in missing])
    
        # create dict containing all data from the available articles
        for page in cont.pages.findAll(missing=None):
            print 'title: ' + page['title']
            title = page['title']
            data = {}
        
            # check whether article was found through redirect
            if cont.redirects:
                redir = cont.redirects.findAll(to=title)
                if redir:
                    print '\tredirect from: ' + redir[0]['from']
                    data['from'] = data.get('from', []) + [redir[0]['from']]
            
            # download the content of the article
            
            # some redirects introduce no ascii characters 
            # TODO introduce a proper conversion of this characters
            try:
                title = title.decode('ascii')
            except Exception:
                continue
                
            query = (query_base + "&export") % title
            text    = myopener.open(query).read()
            soup    = BSS(text, convertEntities=BSS.ALL_ENTITIES)
            export  = BSS(soup.api.query.export.prettify())
            text    = BSS(export.mediawiki.page.revision.prettify())
            if text.revision.minor:
                data['text'] = wikicorpus.filterWiki(text.revision.minor.text)
            else:
                data['text'] = wikicorpus.filterWiki(text.revision.text)
            in_ascii = unicodedata.normalize('NFKD', data['text']).encode('ascii', 'ignore')
            data['text'] = preprocess_string(in_ascii)
            articles[title] = data

f = open(results_path + "sparql_wiki.pickle", 'wb')
pickle.dump(articles, f)
f.close

print sum(all_missing, [])













