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
    
    script_name = "train.py"

    parser = argparse.ArgumentParser(description="Train a classification model from text files")
    parser.add_argument('filespec', help="path to the text files optionally including wildcards, example folder-name/*.txt")
    parser.add_argument('-c', '--clean', action="store_true", help="remove special characters when training")
    parser.add_argument('-g', '--grams', default="2", help="maximum number of grams to use in the model, defaults to 2")
    parser.add_argument('-o', '--outputfile', default="trained.model", help="name of the model to write, defaults to 'trained.model'")
    parser.add_argument('-r', '--recurse', action="store_true", help="recurse into sub-directories when training")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stop words in stopwords.txt when training")
    parser.add_argument('-t', '--top', action="store_true", help="save only the top terms for each gram, use for vectorization")
    parser.add_argument('-x', '--email', action="store_true", help="remove email addresses when training")
    args = parser.parse_args()
        
    # initialize
    lstFiles = []
    list_stopwords = []
    dictModel = {}
    nGrams = int(args.grams)

    if args.stopwords:
        print script_name, "reading: stopwords.txt:", 
        list_stopwords = load_stopword_list('stopwords.txt')
        if not list_stopwords:
            print "error: failed to load stopwords.txt"
            sys.exit(1)
        print "ok,", str(len(list_stopwords)), "terms loaded"
    
    if args.filespec:
        lstFiles = glob.glob(args.filespec)
    else:
        sys.exit(1)
        
    if lstFiles == []:
        print script_name, "file not found:", args.filespec
        sys.exit(1)
            
    for sFile in lstFiles:
        
        # process the files
        if os.path.isdir(sFile):
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(sFile + '/*'):
                    lstFiles.append(sNewFile)
            continue
                    
        print script_name, "reading:", sFile,
        
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
            continue
        
        f.close()

        print "ok,", len(lstBody), "lines loaded"
         
        # clean email       
        if args.email:
            lstBody = remove_email_addresses(lstBody)
        
        # convert lstBody to sBody
        sBody = lst_to_string(lstBody)

        # remove stop chars, if requested
        if args.clean:
            sBody = remove_stop_chars(sBody)
        
        # to do: redo this so it runs as a single pass
                            
        # build model
        dictModel = train_classification_model(dictModel, sBody, nGrams, list_stopwords)
        
    # end for
    
    # finalize the model
    print script_name, "finalizing model:",
    if args.top:
        print "top grams only:",
        dictModel = normalize_classification_model(dictModel, True)
    else:
        dictModel = normalize_classification_model(dictModel, False)
    if not dictModel:
        print script_name, "error: failed to normalize model"
        sys.exit(1)
    print "ok,", len(dictModel), "terms loaded"
    
    # print script_name, "consolidating grams:",
    # now consolidate the grams
    # dictModel = consolidate_grams(dictModel)
    # print "ok"

    # print script_name, "trimming model:",
    # now remove irrelevant? grams
    # dictModel = trim_classification_model(dictModel, .001)
    # print "ok"
    
    # write out the model
    print script_name, "writing:", args.outputfile, 
    if not save_classification_model(dictModel, args.outputfile):
        print
        sys.exit(1)
    print "ok,", str(len(dictModel)), "terms saved" 

    dictFreqs = compute_average_frequency_by_length(dictModel)
    
    # delete, since these can be large    
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end