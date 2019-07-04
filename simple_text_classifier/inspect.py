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

    script_name = "inspect.py"
    
    parser = argparse.ArgumentParser(description="Inspect a classification model")
    parser.add_argument('filespec', help="path to one or more classification models")
    parser.add_argument('-f', '--filter', help="filters the model by string")
    parser.add_argument('-g', '--grams', default="0", help="maximum number of grams to use, defaults to all")
    parser.add_argument('-n', '--number', default="100", help="the number of model entries to show, defaults to 100")
    args = parser.parse_args()
    
    # initialize
    lstFiles = []
    nGrams = int(args.grams)
    
    if args.filespec:
        lstFiles = glob.glob(args.filespec)
    else:
        sys.exit(1)
        
    if lstFiles == []:
        print script_name, "no files found:", args.filespec
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
        
        dictModel = load_classification_model(sFile)
        if not dictModel:
            print script_name, "error: couldn't load:", sFile
            continue
        print "ok,", len(dictModel), "grams loaded"
        print script_name, "inspecting: top", args.number, str(args.grams) + "-grams", 
        if args.filter:
            print "filter:", args.filter
        else:
            print
        print "--------------------------------------------------------------------------------"
        dump_top(dictModel, args.number, args.grams, args.filter)
        print "--------------------------------------------------------------------------------"
    
    # delete, since these can be large    
    del dictModel
    
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end