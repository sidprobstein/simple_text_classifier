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

def remove_stop_words(sString):

    sCleaned = ""
    for token in sString.split():
        if len(token) >= 4:
            sCleaned = sCleaned + token + " "
    
    return sCleaned.strip()

# end removeStopWords

#############################################    

def prepare_string(sString):
    
    sCleaned = remove_stop_chars(sString)
    sCleaned = remove_stop_words(sCleaned)
    return sCleaned
    
# end prepare_string
