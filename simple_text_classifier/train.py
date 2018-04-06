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

from common.utils import remove_stop_words, remove_stop_chars
from common.models import train_classification_model, normalize_classification_model, save_classification_model
from common.models import dump_top, dump_bottom

#############################################    

def main(argv):
    parser = argparse.ArgumentParser(description="Train a classification model from one or more text files")
    parser.add_argument('-o', '--outputfile', default="trained.model", help="name of the classification model file")
    parser.add_argument('-c', '--clean', action="store_true", help="remove special characters before classifying?")
    parser.add_argument('-s', '--stopwords', action="store_true", help="remove stopwords before classifying?")
    parser.add_argument('-r', '--recurse', action="store_true", help="recursively train on files in subdirectories")
    parser.add_argument('-t', '--top', action="store_true", help="show top model entries after classifying ")
    parser.add_argument('-g', '--grams', default="2", help="number of grams to store, defaults to 2")
    parser.add_argument('filespec', help="path to the text files to train a classification model with")
    args = parser.parse_args()
    
    # initialize
    lstFiles = []
    dictModel = {}
    nGrams = int(args.grams)
    
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
            # handle directory
            for sNewFile in glob.glob(sFile + '/*'):
                lstFiles.append(sNewFile)
            continue
        
        if not os.path.isfile(sFile):
            print "train.py: warning, unexpected object type:", sFile
            continue
            
        print "train.py: reading:", sFile
        
        try:
            f = open(sFile, 'r')
        except Exception, e:
            print "train.py: error:", e
            continue
        
        # read the file
        try:
            lstBody = f.readlines()
        except Exception, e:
            print "train.py: error:", e
            f.close()
            continue
        # don't need to keep this file open
        f.close()
        
        # convert lstBody to sBody
        # to do: move this to models...
        sBody = ' '.join(lstBody)
        sBody = sBody.replace("\n","")
        sBody = sBody.strip()
        sBody = sBody.lower()

        # to do: remove email address lines
        # detect them? add a switch?

        # remove stop chars, if requested
        if args.clean:
            sBody = remove_stop_chars(sBody)
                    
        # remove stopwords, if requested
        if args.stopwords:
            sBody = remove_stop_words(sBody)
        
        # build model
        dictModel = train_classification_model(dictModel, sBody, nGrams)
        if not dictModel:
            print "train.py: error, failed to build model!"
            sys.exit(0)
    
            # to do: remove low value items from the model, i.e. anything lower than the threshold in classify.py
    
    # end for
    
    # finalize the model
    dictModel = normalize_classification_model(dictModel)
    if not dictModel:
        print "train.py: error, failed to normalize model!"
        sys.exit(0)
    
    # write out the model
    if not save_classification_model(dictModel, args.outputfile):
        print
        sys.exit(0)
    
    # report on top items
    if args.top:
        print "train.py: top 20 model entries..."
        print "--------------------------------------------------------------------------------"
        dump_top(dictModel, 20)
        print "--------------------------------------------------------------------------------"
        print "train.py: bottom 20 model entries..."
        print "--------------------------------------------------------------------------------"
        dump_bottom(dictModel, 20)
        print "--------------------------------------------------------------------------------"
    
    # delete, since these can be large    
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end