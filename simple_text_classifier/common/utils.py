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
            continue
        if token == "'":
            sCleaned = sCleaned + token
            continue
        if ord(token) < 65:
            sCleaned = sCleaned + ' '

    # remove 's
    if sCleaned.find("'s") > -1:
        sCleaned = sCleaned.replace("'s", "")
        
    # remove ' (e.g. don't, isn't)
    if sCleaned.find("'") > -1:
        sCleaned = sCleaned.replace("'", "")
                
    return sCleaned.strip()

#############################################    

def lst_to_string(lst_string):

    sBody = ""
    sBody = ' '.join(lst_string)
    sBody = sBody.replace("\n","")
    sBody = sBody.strip()
    sBody = sBody.lower()
    return sBody

#############################################    

def remove_email_addresses(lst_input):
    
    if lst_input == []:
        return []
           
    lst_new = []
    for line in lst_input:
        line_new = ""
        hit = False
        for token in line.split():
            if '@' in token:
                hit = True
                hitc = 0
            else:
                if hit:
                    hitc = hitc + 1
                    if hitc == 1:
                        if token.startswith('(') or token.startswith('<'):
                            # drop the token
                            pass
                        else:
                            line_new = line_new + token + " "
                            hit = False
                        # end if
                    if hitc == 2:
                        if token.endswith(')') or token.endswith('>'):
                            pass
                        else:
                            line_new = line_new + token + " "
                        hit = False
                    # end if
                else:
                    line_new = line_new + token + " "
                # end if
            # end if
        # end for
        lst_new.append(line_new.strip())
    # end for
    
    return lst_new                
             
#############################################    

def load_stopword_list(filename):
    
    script_name = "utils.load_stopword_list"
    
    if filename == None or filename == "":
        return []
    
    try:
        f = open(filename, 'r')
    except Exception, e:
        print script_name, "error opening:", e
        return []
      
    # read the file
    try:
        lstBody = f.readlines()
    except Exception, e:
        print script_name, "error reading:", e
        return []
        
    f.close()
    
    lst_stopwords = []
    for l in lstBody:
        lst_stopwords.append(l.strip())
        
    return lst_stopwords
    
#############################################    

def prepare_string(sString):
    
    sCleaned = remove_stop_chars(sString)
    sCleaned = remove_stop_words(sCleaned)
    return sCleaned
    
#############################################    

def count_grams(term):

    if not term:
        return 0
        
    grams = 1
    
    if term.find('_') > -1:
        for c in term:
          if c == '_':
              grams = grams + 1
              
    return int(grams)
    
#############################################    
    
