#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

#############################################    

def remove_stop_chars(sString):
        
    sCleaned = ""
    for token in sString:
        if token.isalpha():
            sCleaned = sCleaned + token
        if ord(token) < 65:
            sCleaned = sCleaned + ' '
    return sCleaned.strip()

# end removeStopChars

#############################################    

def load_stopword_list(filename):
    
    if filename == None or filename == "":
        return []
    
    try:
        # must be in current dir
        f = open(filename, 'r')
    except Exception, e:
        print "error opening:", e
      
    # read the file
    try:
        lstBody = f.readlines()
    except Exception, e:
        print "error reading:", e
        f.close()
        
    f.close()
    
    lst_stopwords = []
    for l in lstBody:
        lst_stopwords.append(l.strip())
        
    return lst_stopwords
    
#############################################        

def remove_stop_words(sString, stopword_list = None):

    sCleaned = ""
    for token in sString.split():
        if stopword_list:
            if token not in stopword_list:
                # also filter anything with less than 3 tokens
                if len(token) > 1:
                    sCleaned = sCleaned + token + " "
                        
    return sCleaned.strip()

# end removeStopWords

#############################################    

def prepare_string(sString):
    
    sCleaned = remove_stop_chars(sString)
    sCleaned = remove_stop_words(sCleaned)
    return sCleaned
    
# end prepare_string

#############################################    

def count_grams(term):

    if not term:
        return 0
        
    grams = 1
    
    if term.find('_') > -1:
        for c in term:
          if c == '_':
              grams = grams + 1
              
    return grams
    
# end prepare_string
