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
    parser.add_argument('-e', '--explain', action="store_true", help="show explanation after classifying")    
    parser.add_argument('-g', '--grams', default="2", help="maximum number of grams to use, defaults to 2")
    parser.add_argument('-i', '--idf', help="path to the idf reference model")
    parser.add_argument('-m', '--model', default="input.model", help="path to the classification model to classify against")
    parser.add_argument('-r', '--recurse', action="store_true", help="recurse into sub-directories when classifying")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stop words in stopwords.txt when classifying")    
    parser.add_argument('-t', '--top', action="store_true", help="input classification model contains only top terms, was built with train -t")    
    parser.add_argument('-x', '--email', action="store_true", help="remove email addresses when classifying")    
    args = parser.parse_args()
       
    # initialize
    nGrams = int(args.grams)
    list_stopwords = []
        
    if args.stopwords:
        print script_name, "reading: stopwords.txt:", 
        list_stopwords = load_stopword_list('stopwords.txt')
        if not list_stopwords:
            print "error: failed to load stopwords.txt"
            sys.exit(1)
        print "ok,", str(len(list_stopwords)), "terms loaded"

    print script_name, "reading: input model:", args.model,
    dictModel = load_classification_model(args.model)
    if not dictModel:
        print "error: couldn't load:", args.model
        sys.exit(1)
    print "ok,", len(dictModel), "grams loaded"
        
    if args.idf and args.top:
        print script_name, "warning: --top specified, ignoring specified --idf."
    else:    
        if args.idf:
            print script_name, "reading: idf model:", args.idf,
            dictIDF = load_classification_model(args.idf)    
            if not dictIDF:
                print "error: failed to load idf model"
                del dictIDF # can be large
                sys.exit(1)
            print "ok,", len(dictIDF), "grams loaded"
    
    if not args.top and not args.idf:
        print script_name, "error: --idf required but not specified."
        sys.exit(1)
        
    # read the files to classify
    
    if args.filespec:
        lstFiles = glob.glob(args.filespec)
    else:
        print script_name, "no input file(s) specified:", args.filespec
        sys.exit(1)
    
    if lstFiles == []:
        print script_name, "no files found:", args.filespec
        if args.idf:
            del dictIDF
        del dictModel
        sys.exit(1)
           
    # iterate through filespec, processing each file
            
    for sFile in lstFiles:
                
        # process the files
        if os.path.isdir(sFile):
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(sFile + '/*'):
                    lstFiles.append(sNewFile)
            continue
        
        print script_name, "classifying:", sFile, 
        try:
            f = open(sFile, 'r')
        except Exception, e:
            print "error opening:", e
            continue
        
        # read the file
        try:
            lstBody = f.readlines()
        except Exception, e:
            print "error reading:", e
            continue
        f.close()
 
        # clean email       
        if args.email:
            lstBody = remove_email_addresses(lstBody)
    
        # convert lstBody to sBody
        sBody = lst_to_string(lstBody)
    
        # remove stop chars, if requested
        if args.clean:
            sBody = remove_stop_chars(sBody)
                    
        dictInput = {}
        dictInput = train_classification_model(dictInput, sBody, nGrams, list_stopwords)
        # don't ever use -top for normalization when classifying (only training)
        dictInput = normalize_classification_model(dictInput, False)
        
#         print "(", str(len(dictInput)), ",",
#         print "%1.6f" % (float(len(dictInput)) / float(len(dictModel))),
#         print ")",

        top_boost = False
        
        if args.top:
            list_classify = classify_top(dictInput, dictModel, nGrams)
        else:
            list_classify = classify(dictInput, dictModel, dictIDF, nGrams)
        fScore = list_classify[0]
        dictExplain = list_classify[1]
        print "->", 
        print "%1.2f" % fScore,
        mark = "\t"
        if fScore > .667:
            mark = "*"
        if fScore > .79:
            mark = "**"
        if fScore > .89:
            mark = "***"
        if top_boost:
            mark = mark + "+"
        print mark,
        if args.explain:
            print "\t[",
            lstExplain = sorted(dictExplain.iteritems(), key=operator.itemgetter(1), reverse=True)
            for (term, count) in lstExplain:
                print term, "(" + str(count) + ")",
            print "]",
            
        print

        # delete since these can be large
        del dictInput
        
    # end for  

    # delete since these are large
    if not args.top:
        del dictIDF
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end