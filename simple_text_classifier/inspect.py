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
    parser = argparse.ArgumentParser(description="Inspect a classification model")
    parser.add_argument('-g', '--grams', default="0", help="number of grams to inspect, defaults to all")
    parser.add_argument('-n', '--number', default="100", help="number of top results to show, defaults to 100")
    parser.add_argument('filespec', help="path to the classification model(s)")
    args = parser.parse_args()
    
    # initialize
    lstFiles = []
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
            if args.recurse:
                # recurse into directory
                for sNewFile in glob.glob(sFile + '/*'):
                    lstFiles.append(sNewFile)
            continue
                    
        print "train.py: inspecting:", sFile,
        
        dictModel = load_classification_model(sFile)
        if not dictModel:
            print "error: couldn't load:", sFile
            sys.exit(0)
        print "ok", len(dictModel), "grams loaded, dumping top", args.number, str(args.grams) + "-grams"
        print "--------------------------------------------------------------------------------"
        dump_top(dictModel, args.number, args.grams)
        print "--------------------------------------------------------------------------------"
    
    # delete, since these can be large    
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end