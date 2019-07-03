#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

#############################################    

import json
import math
import operator

from utils import count_grams

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
                    
    # compute counts
    
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

def normalize_classification_model(dictModel, bTop = False, list_stopwords = None):

    if not dictModel.has_key("_words"):
        print "normalize_classification_model: warning, _words not found in classification model"
        return None
    
    if not dictModel.has_key("_files"):
        print "normalize_classification_model: warning, _files not found in classification model"
        return None

    # remove stopwords 
    k = 0
    for term in dictModel.keys():
        k = k + 1
        if not term[0] == "_":
            grams_term = count_grams(term)
            if grams_term == 1:
                if term in list_stopwords or len(term) == 1:
                    del dictModel[term]
                    dictModel['_words'] = dictModel['_words'] - 1
                # end if
            else:                    
                stopwords_in_gram = 0
                for g in term.split('_'):
                    # count combinations of stopwords and 1-letter characters
                    # this will have some error rate
                    if (g in list_stopwords) or (len(g) == 1):
                        stopwords_in_gram = stopwords_in_gram + 1
                if stopwords_in_gram == grams_term: 
                    # it's all stopwords
                    del dictModel[term]
                    dictModel['_words'] = dictModel['_words'] - 1
    
    # to do: look at problem of xyz xy eg high ranking officials and ranking officials
    # to do: is explciitly_said as important as
                        
    # file size
    dictNormalized = {}
    fAverage = float(dictModel["_words"]) / float(dictModel["_files"])
    for entry in dictModel.iterkeys():
        # just copy meta entries
        if entry[0:1] != "_":
            # normalize non-meta entries
            dictNormalized[entry] = float(dictModel[entry]) / fAverage
    
#     # handle gram dupes e.g. x (w1) xy (w2), w1 > w2, then give xy w1
#     k = 0
#     work = len(dictNormalized)
#     page = (work / 100) / 100 * 100
#     lstSorted = sorted(dictNormalized.iteritems(), key=operator.itemgetter(1), reverse=True)
#     for (t1, c1) in lstSorted:
#         if c1 < 0.2:
#             break
#         if not t1[0] == "_":
#             # not a control term like _word
#             grams_t1 = count_grams(t1)
#             for (t2, c2) in lstSorted:
#                 if c2 < 0.1:                    
#                     break
#                 if not t2[0] == "_":
#                     grams_t2 = count_grams(t2)
#                     if grams_t2 > grams_t1:
#                         if c1 > c2:
#                             # higher weighted, check for match
#                             if t2.startswith(t1 + "_") or t2.endswith("_" + t1):
#                                 # boost
#                                 dictModel[t2] = c1
#                             # end if
#                         # end if
#                     # end if
#                 # end if
#             # end for
#         # end if
#         k = k + 1
#         if k % page == 0:
#             print "%",
#     # end for
        
    if bTop:
        dictTop = {}
        gramCount = {}
        # process the normalized dictionary, reverse sorted by normalized frequencies
        for term in sorted(dictNormalized, key=dictNormalized.get, reverse=True):
            # print term, dictNormalized[term]   
            # take top 10 for each gram found in the model
            grams = count_grams(term)
            if gramCount.has_key(grams):
                if gramCount[grams] < 11:
                    # take this one
                    dictTop[term] = dictNormalized[term]
                    gramCount[grams] = gramCount[grams] + 1
                else:
                    # don't need more of this gram
                    # for now just continue
                    continue
            else:
                # start counting this n-gram
                gramCount[grams] = 1
        # return it     
        return dictTop
    else:
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

#############################################    

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
    
    # to do: how to handle serdar_argic, which is very present in talk.politics.mideast but not the idf model built from all???
     
    for gram in dictInput.iteritems():
        # if it is in the model...
        if dictModel.has_key(gram[0].strip()):
            gram_count = count_grams(gram[0])
            nLen = len(gram[0].strip())
            if float(dictInput[gram[0].strip()]) > 1.0:
                # if the gram is extremely common in the text, ignore it
                pass
            else:
                if dictIDF.has_key(gram[0].strip()):
                    # if the IDF model has a reference count, use it:
                    fContrib = float( 
                                     ( float(dictInput[gram[0].strip()]) / float(dictIDF[gram[0].strip()]) ) * ( float(nLen) / 2.0 )
                                    )
                else:
                    # assume it is rare, i.e. 0.5
                    # to do: evaluate other numbers for this
                    fContrib = float( 
                                     ( float(dictInput[gram[0].strip()]) / 0.5 ) * ( float(nLen) / 2.0 )
                                    )
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
        # end if
    # end for

    # aggregate the top 20 hits into the score
    # to do: rewrite so that we score as the model (dictInput) is built, and stop as soon as we have 10 hits
    fScore1 = 0.0
    fScoreFinal = 0.0
    xTop = 50
    top = xTop
    lstExplain = sorted(dictExplain.iteritems(), key=operator.itemgetter(1), reverse=True)
    for (term, count) in lstExplain:
        if count > 1.0:
            fScore1 = fScore1 + 1.0
        if count > 0.25 and count <= 1.0:
            fScore1 = fScore1 + 0.75
        if count > 0.1 and count <= 0.25:
            fScore1 = fScore1 + 0.5
        top = top - 1
        if top == 0:
            break
    # end for
    if len(dictInput) < 100:
        fScoreFinal = float( float(fScore1) / ( float(xTop) / 1.5 ) )
    else:
        fScoreFinal = float( float(fScore1) / float(xTop) )

    if fScoreFinal > 1.0:
        fScoreFinal = 1.0
        
    return [fScoreFinal, dictExplain]

#############################################    

def classify_top(dictInput, dictModel, nGrams):
        
    if dictInput == {}:
        return None
    
    if dictModel == {}:
        return None
    
    if dictInput.has_key("_words"):
        print "classify: error: input model is not normalized, _words key found"

    if dictModel.has_key("_words"):
        print "classify: error: reference model is not normalized, _words key found"
        
    dictExplain = {}
         
    # for each kt in the input file:
    for kt in dictInput.keys():
        # if it is in the model...
        if dictModel.has_key(kt):
            gram_count = count_grams(kt)
            fContrib = 0.015 * float(len(kt))
            # add to explain dictionary 
            if dictExplain.has_key(kt):
                dictExplain[kt] = float(dictExplain[kt]) + fContrib
            else:
                dictExplain[kt] = fContrib
        # end if
    # end for

    fScore = 0.0
    lstExplain = sorted(dictExplain.iteritems(), key=operator.itemgetter(1), reverse=True)
    for (term, count) in lstExplain:
        fScore = fScore + count
    fScore = fScore * len(lstExplain)

    if fScore > 1.0:
        fScore = 1.0

    return [fScore, dictExplain]

#############################################    

def dump_entries(dictModel, nNumber, grams, bDescending):

    if dictModel == None:
        return None
    
    if dictModel == {}:
        return None
    
    if nNumber == 0:
        return None
    
    top = int(nNumber)
    if bDescending:
        dictSorted = sorted(dictModel.iteritems(), key=operator.itemgetter(1), reverse=True)
    else:
        dictSorted = sorted(dictModel.iteritems(), key=operator.itemgetter(1), reverse=False)        
    for (term, count) in dictSorted:
        if int(grams) > 0:
            if count_grams(term) == int(grams):
                print term, count
        else:
            print term,count
        # end if
        top = top - 1
        if top == 0:
            break
        
    return True

# end dump_bottom_n_model

#############################################    

def dump_top(dictModel, nNumber, grams=1):

    return dump_entries(dictModel, nNumber, grams, True)

# end dump_top_n_model

#############################################    

def dump_bottom(dictModel, nNumber, grams=1):

    return dump_entries(dictModel, nNumber, grams, False)

# end dump_bottom_n_model
    
