#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

import argparse
import sys
import glob
import os

from common.utils import *
from common.models import *

#############################################    

def main(argv):

    script_name = "classify.py"
    
    parser = argparse.ArgumentParser(description="Classify text files using a trained classification model")
    parser.add_argument('filespec', help="path to one or more text files to classify optionally including wildcards, example folder-name/*.txt")
    parser.add_argument('-c', '--clean', action="store_true", help="remove special characters when classifying")
    parser.add_argument('-d', '--debug', action="store_true", help="provide debugging information")
    parser.add_argument('-e', '--explain', action="store_true", help="show explanation after classifying")    
    parser.add_argument('-g', '--grams', default="2", help="maximum number of grams to use, defaults to 2")
    parser.add_argument('-i', '--idf', help="path to the idf reference model")
    parser.add_argument('-m', '--model', default="input.model", help="path to the classification model(s) to classify against, optionaly including wildcards")
    parser.add_argument('-r', '--recurse', action="store_true", help="recurse into sub-directories when classifying")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stop words in stopwords.txt when classifying")    
    parser.add_argument('-t', '--top', action="store_true", help="input classification model contains only top terms, was built with train -t")    
    parser.add_argument('-x', '--email', action="store_true", help="remove email addresses when classifying")    
    args = parser.parse_args()
    
    #########################################   
    # initialize
    n_grams = int(args.grams)
    list_stopwords = []
    dict_models = {}
        
    if args.stopwords:
        print script_name, "reading: stopwords.txt:", 
        list_stopwords = load_stopword_list('stopwords.txt')
        if not list_stopwords:
            print "error: failed to load stopwords.txt"
            sys.exit(1)
        print "ok,", str(len(list_stopwords)), "terms loaded"

    print script_name, "reading: input model(s):", args.model,
    list_model_files = glob.glob(args.model)
    grams_loaded = 0
    for item in list_model_files:
        if os.path.isfile(item):
            dict_models[item] = load_classification_model(item)
            grams_loaded = grams_loaded + len(dict_models[item])
            if args.debug:
                print
                dump_top(dict_models[item], 10, n_grams)
            continue
        if os.path.isdir(item):
            print "warning: ignoring directory:", item,
        #end if
    # end for
    if len(dict_models) == 0:
        print "error: failed to load:", args.model
        sys.exit(1)
    print "ok,", grams_loaded, "grams loaded from", len(dict_models), "model files"
        
    if args.idf and args.top:
        print script_name, "warning: --top specified, ignoring specified --idf."
    else:    
        if args.idf:
            print script_name, "reading: idf model:", args.idf,
            dict_IDF = load_classification_model(args.idf)    
            if not dict_IDF:
                print "error: failed to load idf model"
                del dict_IDF # can be large
                sys.exit(1)
            print "ok,", len(dict_IDF), "grams loaded"
    
    if not args.top and not args.idf:
        print script_name, "error: --idf required but not specified."
        sys.exit(1)
            
    if args.filespec:
        list_files = glob.glob(args.filespec)
    else:
        print script_name, "no input file(s) specified:", args.filespec
        sys.exit(1)
    
    if list_files == []:
        print script_name, "no files found:", args.filespec
        if args.idf:
            del dict_IDF
        del dict_models
        sys.exit(1)
           
    #########################################
    # read each file and prepare it
            
    for s_file in list_files:
        if os.path.isdir(s_file):
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(s_file + '/*'):
                    list_files.append(sNewFile)
            continue
        
        print script_name, "classifying:", s_file, "->",
        try:
            f = open(s_file, 'r')
        except Exception, e:
            print "error opening:", e
            continue
        
        # read the file
        try:
            list_body = f.readlines()
        except Exception, e:
            print "error reading:", e
            continue
        f.close()
 
        # clean email       
        if args.email:
            list_body = remove_email_addresses(list_body)
    
        # convert list_body to s_body
        s_body = lst_to_string(list_body)
    
        # remove stop chars, if requested
        if args.clean:
            s_body = remove_stop_chars(s_body)
                    
        dict_input = {}
        dict_input = train_classification_model(dict_input, s_body, n_grams, list_stopwords)
        # don't ever use -top for normalization when classifying (only training)
        dict_input = normalize_classification_model(dict_input, False)
        
        if args.debug:
            print
            dump_top(dict_input, 10, n_grams)
        
        #########################################
        # classify against each model

        b_matched = False
        dict_misses = {}
        
        for model in dict_models:
            dict_model = dict_models[model]
            if args.top:
                list_classify = classify_top(dict_input, dict_model, n_grams)
            else:
                list_classify = classify(dict_input, dict_model, dict_IDF, n_grams)
            f_score = list_classify[0]
            if f_score > .667:
                # match!
                b_matched = True
                mark = "*"
                if f_score > .79:
                    mark = "**"
                if f_score > .89:
                    mark = "***"
                print model, "%1.2f" % f_score, mark,
                if args.explain:
                    dict_explain = list_classify[1]
                    print "[",
                    list_explain = sorted(dict_explain.iteritems(), key=operator.itemgetter(1), reverse=True)
                    for (term, count) in list_explain:
                        print term, "(" + str(count) + ")",
                    print "]",
                # end if
            else:
                dict_misses[model] = f_score
                if args.debug:
                    print "%1.2f" % f_score,
            # end if
        # end for
        if not b_matched:
            if args.explain:
                print "?", dict_misses
            else:
               print "?"
        else:
            print

        # delete since these can be large
        del dict_input
        
    # end for  

    # clean up
    if not args.top:
        del dict_IDF
    del dict_models
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end