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
    parser = argparse.ArgumentParser(description="Classify text file(s) using a trained model")
    parser.add_argument('-m', '--model', default="input.model", help="path to the input classification model file")
    parser.add_argument('-i', '--idf', help="path to the idf reference model file")
    parser.add_argument('-c', '--clean', action="store_true", help="remove special characters before classifying?")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stopwords before classifying?")    
    parser.add_argument('-g', '--grams', default="2", help="number of grams to store, defaults to 2")
    parser.add_argument('-r', '--recurse', action="store_true", help="recursively train on files in sub-directories")
    parser.add_argument('-t', '--top', action="store_true", help="use top-model for classification")    
    parser.add_argument('-x', '--explain', action="store_true", help="show explanation when classifying")    
    parser.add_argument('filespec', help="path to one or more text files to classify against the specified model")
    args = parser.parse_args()
       
    # initialize
    nGrams = int(args.grams)
    list_stopwords = []
        
    ########################################
    # read the classification model

    print "classify.py: reading input model:", args.model,
    dictModel = load_classification_model(args.model)
    if not dictModel:
        print "error: couldn't load:", args.model
        sys.exit(0)
    print "ok", len(dictModel), "grams loaded"
        
    ########################################
    # read the idf model

    print args.idf
    if args.idf:
        print "classify.py: reading idf model:", args.idf,
        dictIDF = load_classification_model(args.idf)    
        if not dictIDF:
            print "error: couldn't load:", args.idf
            del dictIDF # can be large
            sys.exit(0)
        print "ok", len(dictIDF), "grams loaded"
    ########################################
    # read the files to classify
    
    if args.filespec:
        lstFiles = glob.glob(args.filespec)
    else:
        print "classify.py: filespec missing!"
        sys.exit(0)
    
    if lstFiles == []:
        print "classify.py: can't open:", args.filespec
        if args.idf:
            del dictIDF
        del dictModel
        sys.exit(0)

    if args.stopwords:
        print "classify.py: loading stopwords:", 
        list_stopwords = load_stopword_list('stopwords.txt')
        if not list_stopwords:
            print "error"
            del dictIDF
            del dictModel
            sys.exit(0)
        print "ok"

    ########################################
    # iterate through filespec, processing each file
            
    for sFile in lstFiles:
                
        # process the files
        if os.path.isdir(sFile):
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(sFile + '/*'):
                    lstFiles.append(sNewFile)
            continue
        
        print "classify.py: reading:", sFile, 
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
            f.close()
            continue
        f.close()
    
        # convert lstBody to sBody
        sBody = ""
        sBody = ' '.join(lstBody)
        sBody = sBody.replace("\n","")
        sBody = sBody.strip()
        sBody = sBody.lower()
    
        # remove stop chars, if requested
        if args.clean:
            sBody = remove_stop_chars(sBody)
        
        # remove stopwords, if requested
        if args.stopwords:
            sBody = remove_stop_words(sBody, list_stopwords)
            
        dictInput = {}
        dictInput = train_classification_model(dictInput, sBody, nGrams)
        if dictInput:
            dictInput = normalize_classification_model(dictInput)
        else:
            print "warning: input model is empty"
            continue
        
        if args.top:
            list_classify = classify(dictInput, dictModel, None, nGrams, True)
        else:
            list_classify = classify(dictInput, dictModel, dictIDF, nGrams, False)
        fScore = list_classify[0]
        dictExplain = list_classify[1]
        print "ok, matches model:", 
        print "%1.2f" % fScore,
        if fScore > .667:
            print "*", 
 
        if args.explain:
            lstExplain = sorted(dictExplain.iteritems(), key=operator.itemgetter(1), reverse=True)
            for (term, count) in lstExplain:
                print term, "(" + str(count) + ")",
            
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