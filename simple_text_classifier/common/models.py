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

def train_classification_model(dictModel, sString, nGrams, list_stopwords = None):
    
    lstModel = []
    nWords = 0
    sGram = ""
    xMinToken = 2
    
    if dictModel == None:
        dictModel = {}
        
    for token in sString.split():
        if (token in list_stopwords) or (len(token) < xMinToken):
            # ignore
            continue
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
                        nWords = nWords + 1
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

    script_name = "models.normalize_classification_module"

    if not dictModel.has_key("_words"):
        print script_name, "warning, _words not found in classification model"
        return None
    
    if not dictModel.has_key("_files"):
        print script_name, "warning, _files not found in classification model"
        return None
    
    # to do: look at problem of xyz xy eg high ranking officials and ranking officials
    # to do: why is explciitly_said high value?
                        
    # file size
    dictNormalized = {}
    fAverage = float(dictModel["_words"]) / float(dictModel["_files"])
 
    for entry in dictModel.iterkeys():
        # just copy meta entries
        if entry[0:1] != "_":
            # normalize non-meta entries
            dictNormalized[entry] = float(dictModel[entry]) / fAverage        
            
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

def compute_average_frequency_by_length(dictModel):
    
    if dictModel == {}:
        return {}
    
    dictLengths = {}
    big = 0
    for k in dictModel.keys():
        l = len(k)
        if l > big:
            big = l
        kl = "_f" + str(l)
        kc = "_c" + str(l)
        if dictLengths.has_key(kl):
            dictLengths[kl] = dictLengths[kl] + dictModel[k]
            dictLengths[kc] = dictLengths[kc] + 1 
        else:
            dictLengths[kl] = dictModel[k]         
            dictLengths[kc] = 1 
            
    dictFreqs = {}
    for k1 in dictLengths.keys():
        if k1[1:2] == "f":
            k = k1[2:]
            kf = "_f" + k
            kc = "_c" + k
            dictFreqs[k] = float(dictLengths[kf]) / float(dictLengths[kc])
    
    return dictFreqs

#############################################    

def save_classification_model(dictModel, sFile):

    try:
        fo = open(sFile, 'w')
    except Exception, e:   
        print "error opening:", e             
        return None
    # to do: sort the model, descending
    
    try:
        json.dump(dictModel, fo, sort_keys=False, indent=4, separators=(',', ':'))
    except Exception, e:
        print "error writing:", e
        return None
    fo.close()

    return True
 
# end save_classification_model

#############################################    

def load_classification_model(sFile):

    try:
        fi = open(sFile, 'r')
    except Exception, e:   
        print "error opening:", e             
        return None
    dictModel = {}
    try:
        dictModel = json.load(fi)
    except Exception, e:
        print "error reading:", e
        fi.close()
        return None
    fi.close()

    return dictModel
 
# end save_classification_model

#############################################    

def classify(dictInput, dictModel, dictIDF, nGrams):
        
    script_name = "models.classify"
    
    if dictInput == {}:
        return None

    if dictModel == {}:
        return None
    
    if dictIDF == {}:
        return None

    if dictInput.has_key("_words"):
        print script_name, "error: input model is not normalized, _words key found"

    if dictModel.has_key("_words"):
       print script_name, "error: reference model is not normalized, _words key found"

    if dictIDF.has_key("_words"):
        print script_name, "error: idf model is not normalized, _words key found"
    
    fScore = 0.0
    dictExplain = {}
        
    size_adjust = 1.0    
    if len(dictInput) < 75:
        size_adjust = 2.0
    if len(dictInput) < 25:
        size_adjust = 4.5
    input_vs_model = (float(len(dictInput)) / float(len(dictModel))) # e.g. .004
    if input_vs_model > .002:
        size_adjust = 0.67
    # presumably, very large documents will need more adjustment
        
    # compute average frequencies for various lengths
    dict_freqs = compute_average_frequency_by_length(dictModel)
     
    for gram in dictInput.keys():
        if float(dictInput[gram]) > 1.0:
            continue
        gram_count = count_grams(gram)
        if gram_count > 1:
            gc = 0
            gl = 0
            for g in gram.split('_'):
                gc = gc + 1
                gl = gl + len(g)
            gram_average_length = float(gl) / float(gc)
        else:
            gram_average_length = len(gram)

        # is it in the classification model?
        if dictModel.has_key(gram):
            idf = dictModel[gram]
            if dictIDF.has_key(gram):
                if dictIDF[gram] > idf:
                    idf = dictIDF[gram]
        else:
            continue
                                
        # compute tf/idf
        fContrib = float( 
                         ( float(dictInput[gram]) / float(idf) ) * ( math.log1p(gram_average_length) * ( gram_average_length ** 2 ) )
                        ) 

        # aggregate                    
        if fContrib > 1.0:
            # accept notable contributions only
            fScore = fScore + fContrib
            # add to explain dictionary 
            if dictExplain.has_key(gram):
                dictExplain[gram] = dictExplain[gram] + fContrib
            else:
                dictExplain[gram] = fContrib
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
    
    # adjust small models
    fScore1 = fScore1 * size_adjust

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
        
    script_name = models.classify_top
    
    if dictInput == {}:
        return None
    
    if dictModel == {}:
        return None
    
    if dictInput.has_key("_words"):
        print script_name, "error: input model is not normalized, _words key found"

    if dictModel.has_key("_words"):
        print script_name, "error: reference model is not normalized, _words key found"
        
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

def dump_entries(dictModel, nNumber, grams, sFilter, bDescending):

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
        # filter grams
        if int(grams) > 0:
            if count_grams(term) == int(grams):
                print term, count
                continue
        else: 
            if sFilter:
                if sFilter in term:
                    print term, count
            continue
        print term,count
        # end if
        top = top - 1
        if top == 0:
            break
        
    return True

# end dump_bottom_n_model

#############################################    

def dump_top(dictModel, nNumber, grams=1, sFilter=None):

    return dump_entries(dictModel, nNumber, grams, sFilter, True)

# end dump_top_n_model

#############################################    

def dump_bottom(dictModel, nNumber, grams=1):

    return dump_entries(dictModel, nNumber, grams, False)

# end dump_bottom_n_model
    
