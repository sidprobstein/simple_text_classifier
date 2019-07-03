#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

import argparse
import glob
import sys
import os

from common.utils import *
from common.models import *

#############################################    

def main(argv):
    parser = argparse.ArgumentParser(description="Train a classification model from one or more text files")
    parser.add_argument('-o', '--outputfile', default="trained.model", help="name of the classification model file")
    parser.add_argument('-c', '--clean', action="store_true", help="remove special characters before classifying?")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stop words before classifying?")
    parser.add_argument('-r', '--recurse', action="store_true", help="recursively train on files in sub-directories")
    parser.add_argument('-t', '--top', action="store_true", help="store top 10 for each gram only")
    parser.add_argument('-g', '--grams', default="2", help="number of grams to store, defaults to 2")
    parser.add_argument('filespec', help="path to the text files to train a classification model with")
    args = parser.parse_args()
    
    # initialize
    lstFiles = []
    list_stopwords = []
    dictModel = {}
    nGrams = int(args.grams)

    if args.stopwords:
        print "train.py: loading: stopwords.txt:", 
        list_stopwords = load_stopword_list('stopwords.txt')
        if not list_stopwords:
            print "error: failed to load stopwords.txt"
            sys.exit(0)
        print "ok", str(len(list_stopwords)), "terms loaded"
    
    if args.filespec:
        lstFiles = glob.glob(args.filespec)
    else:
        sys.exit(-1)
        
    if lstFiles == []:
        print "train.py: can't open:", args.filespec
        sys.exit(-1)
    
    for sFile in lstFiles:
        
        # process the files
        if os.path.isdir(sFile):
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(sFile + '/*'):
                    lstFiles.append(sNewFile)
            continue
                    
        print "train.py: reading:", sFile,
        
        try:
            f = open(sFile, 'r')
        except Exception, e:
            print "error:", e
            continue
        
        # read the file
        try:
            lstBody = f.readlines()
        except Exception, e:
            print "error:", e
            f.close()
            continue
        
        f.close()

        print "ok"
        
        # convert lstBody to sBody
        sBody = ' '.join(lstBody)
        sBody = sBody.replace("\n","")
        sBody = sBody.strip()
        sBody = sBody.lower()

        # to do: remove email address lines
        # detect them? add a switch?

        # remove stop chars, if requested
        if args.clean:
            sBody = remove_stop_chars(sBody)
                            
        # build model
        dictModel = train_classification_model(dictModel, sBody, nGrams)
        if not dictModel:
            print "classify.py: error: training failed"
            sys.exit(0)
        
    # end for
    
    # finalize the model
    print "train.py: finalizing:",
    if args.top:
        print "(top only)",
        dictModel = normalize_classification_model(dictModel, True, list_stopwords)
    else:
        dictModel = normalize_classification_model(dictModel, False, list_stopwords)
    if not dictModel:
        print "train.py: error, failed to normalize model!"
        sys.exit(0)
    print "ok"
    
    # write out the model
    print "train.py: saving:", args.outputfile, 
    if not save_classification_model(dictModel, args.outputfile):
        print
        sys.exit(0)
    print "ok", str(len(dictModel)), "terms written" 
    
    # delete, since these can be large    
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end