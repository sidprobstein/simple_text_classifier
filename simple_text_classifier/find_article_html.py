#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sidprobstein@gmail.com
'''

import os
import sys
import argparse
import operator

from bs4 import BeautifulSoup
# from __builtin__ import False

#############################################    

def bool(b):
    if b:
        return "T"
    else:
        return "F"
        
#############################################    

def main(argv):
    
    script_name = "find_article_html.py"

    parser = argparse.ArgumentParser(description="Find the content bearing portion of an HTML page")
    parser.add_argument('-d', '--debug', action="store_true", help="Show state machine for debugging")    
    parser.add_argument('filespec', help="path to the html file to extract")
    args = parser.parse_args()
        
    # initialize

    f = None
    
    try:
        f = open(args.filespec, 'r')
    except Exception, e:
        print script_name + ": error opening:", e
        
    try:
        html_list = f.readlines()
    except Exception, e:
        print script_name + ": error reading:", e
        
    html = ' '.join(html_list)
       
    # setup    
    section = 0
    dict_article = {}
    dict_article[section] = {}
    dict_article[section]['text'] = ""
    dict_article[section]['tag'] = ""
    dict_article[section]['len'] = 0
    dict_article[section]['links'] = 0
    dict_article[section]['density'] = 0.0
    dict_rank = {}
    dict_rank[section] = 0.0

    chunk_tags = [ 'div', 'title' ]
    remove_tags = [ 'script', 'style', 'link', 'noscript' ]
    ignore_chars = [ '\n', '\t', '\r' ]

    is_tag = False
    tag = ""
    is_close_tag = False
    is_link = False
    last = ""
    section_len = 0
    section_links = 0
    section_link_density = 0.0
    emit = True
    tag_done = False
    in_quote = False
    remove  = False

    # state machine:
    #################################
    
    for ch in html:   

        if args.debug:
            print "is_tag:", bool(is_tag), "close:", bool(is_close_tag), "done:", bool(tag_done), "link:", bool(is_link), "quote:", \
                bool(in_quote), "emit:", bool(emit), "last:", last, "tag:", ("%10s" % tag), "\t:", 
 
        # ignore new lines     
        if ch in ignore_chars:
            if args.debug:
                print "?", "\tignored"
            continue
        
        if args.debug:
            print ch, "\t",
        
        # ignore spaces at beginning of section (when not in_tag)
#         if not is_tag:
#             if ch == ' ':
#                 if dict_article[section]['text'] == "":
#                     continue
        # end if
        # ignore more than 1 space
        if ch == ' ':
            if last == ' ':
                if args.debug:
                    print "ignored0"
                continue
        # end if
        
        # important for script handling    
        if ch in [ '"', "'" ]:
            if not last == '\\':
                in_quote = not in_quote
                last = ch
                if args.debug:
                    if in_quote:
                        print "start-quote"
                    else:
                        print "end-quote"
                continue
            
        if in_quote:
            # print "ignoring quoted", ch
            # last = ch
            last = ch
            if args.debug:
                print "quoted"
            continue

        ################################# START TAG <
        
        if ch == '<':
            # start tag
            # the problem is that emit is too strong, once set, we stop looking for the clue to end the ignore tag
            is_tag = True
            is_close_tag = False
            tag_done = False
            emit = False
            is_link = False
            tag = ""
            last = ch
            if args.debug:
                print "start-tag"
            continue
        # end if

        ################################# END TAG >

        if ch == '>':
            # if not last.isalnum():
            if not is_tag:
                # not in tag, ignore
                if args.debug:
                    print "not-tag0"
                continue
            if tag.strip() == "":
                # tag is blank, this is not a tag
                if args.debug:
                    print "not-tag1"
                continue
            is_tag = False
            tag_done = True
            if last == "/":
                is_close_tag = True
            if is_close_tag:
                # end of a close tag
                emit = True
                debug_token = "end-close-tag"
                if tag == 'a':
                    is_link = False
                    if args.debug:
                        debug_token = "end-link"
                for t in remove_tags:
                    if tag.startswith(t):
                        emit = True
                        if args.debug:
                            debug_token = "end-remove"
                if args.debug:
                    print debug_token
            else:
                # end of open tag
                emit = True
                debug_token = "end-open-tag"
                if tag == 'a':
                    is_link = True
                    if args.debug:
                        debug_token = "start-link"
                    continue
                for t in remove_tags:
                    if tag.startswith(t):
                        emit = False
                        if args.debug:
                            debug_token = "start-remove"                        
                # end for
                # open tag doesn't cause section so move on
                if args.debug:
                    print debug_token
                continue
            # end if is_close_tag
                
            for t in chunk_tags:
                if tag.startswith(t):
                    if args.debug:
                        print "SECTION!"
                    # calculate density for this section
                    dict_article[section]['tag'] = tag
                    dict_article[section]['len'] = section_len
                    dict_article[section]['links'] = section_links
                    if section_len > 0:
                        dict_article[section]['density'] = float( float(section_links) / float(section_len) )
                        if dict_article[section]['density'] < 0.1:
                            dict_rank[section] = float(dict_article[section]['len'])
                        else:
                            if dict_article[section]['density'] > .7:
                                dict_rank[section] = 1
                            else:
                                dict_rank[section] = float( float(dict_article[section]['density']) * float(dict_article[section]['len']))
                        if dict_article[section]['tag'] == 'title':
                            dict_rank[section] = dict_rank[section] * 1000
                   # initialize next section
                    section = section + 1
                    dict_article[section] = {}
                    dict_article[section]['text'] = ""
                    dict_article[section]['tag'] = tag
                    dict_article[section]['len'] = 0
                    dict_article[section]['links'] = 0
                    dict_article[section]['density'] = 0.0
                    dict_rank[section] = 0.0
                    section_len = 0
                    section_links = 0
                    section_link_density = 0.0
                # end if
            # end for
            if args.debug:
                print ""
            continue
            
        # end if ch == >

        ################################# IN TAG           
        
        if is_tag:
            last = ch
            # in tag
            if ch == '/':
                if tag == "":
                    is_close_tag = True
                    if args.debug:
                        print "close-tag"
                    continue
            if ch in [' ', '!']:
                tag_done = True
                if tag.strip() == "":
                    is_tag = False
                    if args.debug:
                        print "not-tag"
                else:
                    if args.debug:
                        print "tag-done"                    
                continue
            if tag_done:
                if args.debug:
                    print ""
                continue  
            debug_token = ""
            if ch.isalnum():
                tag = tag + ch
                if args.debug:
                    debug_token = "*"
            if ch == " ":
                tag = tag + ch
                if args.debug:
                    debug_token = "*"
            if args.debug:
                print debug_token

        ################################# OUTSIDE TAG         
        
        else:
            if emit:
                # accumulate in appropriate section
                if ch.isalnum():
                    section_len = section_len + 1
                    if is_link:
                        section_links = section_links + 1
                if dict_article[section]['text'].strip() == "":
                    # if the text is blank, don't start with a space
                    if ch == " ":
                        if args.debug:
                            print "ignored1"
                        last = ch
                        continue
                if ch == " ":
                    if last == " ":
                        # ignore two spaces in a row
                        if args.debug:
                            print "ignored2"
                        continue
                    if dict_article[section]['text'][-1:] == " ":
                        # if the last thing in the text is a space, don't store it
                        if args.debug:
                            print "ignored3"
                        last = ch
                        continue
                # end if
                debug_token = ""
                if ch.isalnum():
                    dict_article[section]['text'] = dict_article[section]['text'] + ch
                    if args.debug:
                        debug_token = "*"
                if ch == " ":
                    dict_article[section]['text'] = dict_article[section]['text'] + ch
                    if args.debug:
                        debug_token = "*"
                if args.debug:
                    print debug_token
                last = ch
            else:
                if args.debug:
                    print
                last = ch
            # end if
        # end for
    
    # state machine end
    #################################    
        
    # calculate density for last section if necessary
    dict_article[section]['tag'] = tag
    dict_article[section]['len'] = section_len
    dict_article[section]['links'] = section_links
    if section_len > 0:
        dict_article[section]['density'] = float( float(section_links) / float(section_len) )
        if dict_article[section]['density'] < 0.1:
            dict_rank[section] = float(dict_article[section]['len'])
        else:
            if dict_article[section]['density'] > .7:
                dict_rank[section] = 0
            else:
                dict_rank[section] = float( float(dict_article[section]['density']) * float(dict_article[section]['len']))
        if dict_article[section]['tag'] == 'title':
            dict_rank[section] = dict_rank[section] * 1000
                                            
    ranked_sections = sorted(dict_rank.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    type = ""
    for (k, r) in ranked_sections:
        if r > 0:
            if dict_article[k]['density'] < .1:
                type = "body\t"
            if dict_article[k]['density'] > .6:
                type = "related"
            if dict_article[k]['density'] > .8:
                type = "nav\t"
            if type == "body":
                if dict_article[k]['len'] < 40:
                    type = "frag\t"
            if dict_article[k]['tag'] == "title":
                type = "title\t"
            if not dict_article[k]['tag'] == "":
                print type, int(r), "\t", "%3.2f" % dict_article[k]['density'], "\t", dict_article[k]['tag'], "\t", dict_article[k]['text']
                        
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end