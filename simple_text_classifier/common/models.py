#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

#############################################    

import json
import operator

#############################################    

def train_classification_model(dictModel, sString, nGrams):
    
    lstModel = []
    nWords = 0
    sGram = ""
    
    if dictModel == None:
        dictModel = {}
    
    for token in sString.split():
        # add to the gram list
        lstModel.append(token)
        nWords = nWords + 1
        # if the gram list is full, delete the left-most
        if len(lstModel) > nGrams:
            lstModel = lstModel[1:len(lstModel)]
        # now process all grams
        sLast = ""
        for n in range(1, nGrams + 1):
            sGram = '_'.join(lstModel[-1*n:])
            if sGram != sLast:
                if sGram != "":
                    if dictModel.has_key(sGram):
                        dictModel[sGram] += 1
                    else:
                        dictModel[sGram] = 1
            sLast = sGram
    # end for
    
    if dictModel.has_key('_words'):
        dictModel['_words'] = dictModel['_words'] + nWords
    else:
        dictModel['_words'] = int(nWords)
        
    if dictModel.has_key('_files'):
        dictModel['_files'] = dictModel['_files'] + 1
    else:
        dictModel['_files'] = int(1)

    return dictModel

# end build_model

#############################################    

def normalize_classification_model(dictModel):

    if not dictModel.has_key("_words"):
        print "normalize_classification_model: warning, _words not found in classification model"
        return None
    
    if not dictModel.has_key("_files"):
        print "normalize_classification_model: warning, _files not found in classification model"
        return None
    
    # file size
    dictNormalized = {}
    fAverage = float(dictModel["_words"]) / float(dictModel["_files"])
    for entry in dictModel.iterkeys():
        # just copy meta entries
        if entry[0:1] != "_":
            # normalize non-meta entries
            dictNormalized[entry] = float(dictModel[entry]) / fAverage
    
    return dictNormalized

# end normalize_classification_model

#############################################    

def save_classification_model(dictModel, sFile):

    try:
        fo = open(sFile, 'w')
    except Exception, e:   
        print "error:", e             
        fo.close()
        return None
    try:
        json.dump(dictModel, fo, sort_keys=False, indent=4, separators=(',', ':'))
    except Exception, e:
        print "error:", e
        fo.close()
        return None
    fo.close()

    return True
 
# end save_classification_model

#############################################    

def load_classification_model(sFile):

    try:
        fi = open(sFile, 'r')
    except Exception, e:   
        print "error:", e             
        return None
    dictModel = {}
    try:
        dictModel = json.load(fi)
    except Exception, e:
        print "error:", e
        fi.close()
        return None
    fi.close()

    return dictModel
 
# end save_classification_model


def classify(dictInput, dictModel, dictIDF, nGrams):
        
    if dictInput == {}:
        return None
    if dictModel == {}:
        return None
    if dictIDF == {}:
        return None

    if dictInput.has_key("_words"):
        print "classify: error: input model is not normalized, _words key found"

    if dictModel.has_key("_words"):
        print "classify: error: reference model is not normalized, _words key found"

    if dictIDF.has_key("_words"):
        print "classify: error: idf model is not normalized, _words key found"
        
    nHits = 0
    fScore = 0.0
    dictExplain = {}
    
    # for each gram in the input file:
    for gram in dictInput.iteritems():
        # if it is in the model...
        if dictModel.has_key(gram[0].strip()):
            nLen = len(gram[0].strip())
            if float(dictInput[gram[0].strip()]) > 1.0:
                # if the gram is extremely common in the text, ignore it
                fContrib = 0.0
            else:
                if dictIDF.has_key(gram[0].strip()):
                    # if the IDF model has a reference count, use it:
                    fContrib = float(( float(dictInput[gram[0].strip()]) / float(dictIDF[gram[0].strip()]) ) * ( float(nLen) / 2.0 ))
                else:
                    # assume it is rare, i.e. 0.5
                    # to do: evaluate other numbers for this
                    fContrib = float(( float(dictInput[gram[0].strip()]) / 0.5 ) * ( float(nLen) / 2.0 ))
            if fContrib > 1.0:
                # accept notable contributions only
                fScore = fScore + fContrib
                # count them as a hit
                nHits = nHits + 1
                # add to explain dictionary 
                if dictExplain.has_key(gram[0]):
                    dictExplain[gram[0]] = dictExplain[gram[0]] + fContrib
                else:
                    dictExplain[gram[0]] = fContrib
                                
    ########################################
    # aggregate the top 20 hits into the score
    
    # to do: rewrite so that we score as the model (dictInput) is built, and stop as soon as we have 10 hits
    
    fScore1 = 0.0
    xTop = 20
    top = xTop
    nTopHits = 0
    lstExplain = sorted(dictExplain.iteritems(), key=operator.itemgetter(1), reverse=True)
    for (term, count) in lstExplain:
        if count > 1.0:
            fScore1 = fScore1 + 1.0
        if count > 0.25 and count <= 1.0:
            fScore1 = fScore1 + 0.75
        if count > 0.1 and count <= 0.25:
            fScore1 = fScore1 + 0.5
        top = top - 1
        nTopHits = nTopHits + 1
        if top == 0:
            break
    if len(dictInput) < 100:
        fScoreFinal = float( float(fScore1) / ( float(xTop) / 1.5 ) )
        if fScoreFinal > 1.0:
            fScoreFinal = 1.0
    else:
        fScoreFinal = float( float(fScore1) / float(xTop) )

    return fScoreFinal
                    
#############################################    

def dump_entries(dictModel, nNumber, bDescending):

    if dictModel == None:
        return None
    
    if dictModel == {}:
        return None
    
    if nNumber == 0:
        return None
    
    top = nNumber
    if bDescending:
        dictSorted = sorted(dictModel.iteritems(), key=operator.itemgetter(1), reverse=True)
    else:
        dictSorted = sorted(dictModel.iteritems(), key=operator.itemgetter(1), reverse=False)        
    for (term, count) in dictSorted:
        print term, count
        top = top - 1
        if top == 0:
            break
        
    return True

# end dump_bottom_n_model

#############################################    

def dump_top(dictModel, nNumber):

    return dump_entries(dictModel, nNumber, True)

# end dump_top_n_model

#############################################    

def dump_bottom(dictModel, nNumber):

    return dump_entries(dictModel, nNumber, False)

# end dump_bottom_n_model
    
