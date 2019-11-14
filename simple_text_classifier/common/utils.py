#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

#############################################    

def remove_stop_chars(unclean_string):
        
    clean_string = ""            
    for ch in unclean_string:
        if ch.isalpha():
            clean_string = clean_string + ch
            continue
        if ch == "'":
            clean_string = clean_string + ch
            continue
        if ord(ch) < 65:
            clean_string = clean_string + " "

    # remove ALL 's
    if clean_string.find("'s") > -1:
        clean_string = clean_string.replace("'s", "")
        
    # remove ' (e.g. don't, isn't)
    if clean_string.find("'") > -1:
        clean_string = clean_string.replace("'", "")
        
    return clean_string
        
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
    
