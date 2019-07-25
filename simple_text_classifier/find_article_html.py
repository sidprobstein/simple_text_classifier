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

from bs4 import BeautifulSoup

#############################################    

def main(argv):
    
    script_name = "find_article_html.py"

    parser = argparse.ArgumentParser(description="Find the content bearing portion of an HTML page")
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
    section = 1
    dict_article = {}
    dict_article[section] = {}
    dict_article[section]['text'] = ""
    dict_article[section]['tag'] = ""
    dict_article[section]['len'] = 0
    dict_article[section]['links'] = 0
    dict_article[section]['density'] = 0.0

    chunk_tags = [ 'title', 'div' ]
    remove_tags = [ 'script', 'style', 'link', '!--' ]
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
    in_link = False

    # state machine:
    for ch in html:   
        # ignore new lines     
        if ch in ignore_chars:
            continue
        # ignore spaces at beginning of section
        if ch == ' ':
            if dict_article[section]['text'] == "":
                continue
        # end if
        # ignore more than 1 space
        if ch == ' ':
            if last == ' ':
                last = ch
                continue
        # end if
        # print ch, ord(ch), "\tis_tag:", is_tag, "\tis_close_tag:", is_close_tag, "\tlink:", is_link, "\temit:", emit
        if ch == '<':
            if last in ['"', "'"]:
                # quoted, ignore 
                continue
            # start tag
            is_tag = True
            is_close_tag = False
            tag = ""
            continue
        # end if
        if ch == '>':
            # end tag
            is_tag = False
            if is_close_tag:
                for t in remove_tags:
                    if tag.startswith(t):
                        # finished with a remove tag
                        emit = True
                if tag == 'a':
                    in_link = False
                for t in chunk_tags:
                    if tag.startswith(t):
                        # calculate density for this section
                        dict_article[section]['tag'] = tag
                        dict_article[section]['len'] = section_len
                        dict_article[section]['links'] = section_links
                        if section_len > 0:
                            dict_article[section]['density'] = float( float(section_links) / float(section_len) )
                        # initialize next section
                        section = section + 1
                        dict_article[section] = {}
                        dict_article[section]['text'] = ""
                        dict_article[section]['tag'] = tag
                        dict_article[section]['len'] = 0
                        dict_article[section]['links'] = 0
                        dict_article[section]['density'] = 0.0
                        section_len = 0
                        section_links = 0
                        section_link_density = 0.0
                    # end if
                # end for
            else:
                # note we don't store spaces in tags!!
                if tag.lower().startswith('ahref'):
                    in_link = True
                for t in remove_tags:
                    if tag.startswith(t):
                        # finished with a tag we want to remove
                        emit = False
                # end for
            continue
        # end if
        if is_tag:
            # in tag
            # note we will never get ignore chars or spaces!
            if ch == '/':
                # only honor at beginning of tag
                if tag == "":
                    is_close_tag = True
            else:
                tag = tag + ch
        else:
            if emit:
                # accumulate in appropriate section
                section_len = section_len + 1
                if in_link:
                    section_links = section_links + 1
                dict_article[section]['text'] = dict_article[section]['text'] + ch
            # end if
            last = ch
        # end if
    # end for
                
    # calculate density for last section if necessary
    if dict_article[section]['text'] == "":
        del dict_article[section]
    else:
        dict_article[section]['len'] = section_len
        dict_article[section]['links'] = section_links
        if section_len > 0:
            dict_article[section]['density'] = float( float(section_links) / float(section_len) )
        else:
            dict_article[section]['density'] = 0.0

    for key in dict_article:
        if len(dict_article[key]['text']) > 0:
            print key, 
            print dict_article[key]
                
                
                
#                     section_links = section_links + 1
#                 else:
#                     section_len = section_len + 1
#             last = i
#         if section_len > 0:
#             link_density = float( float(section_links) / float(section_len) )
# #            if link_density < 0.3:
#             print ( link_density, div.getText() )
            
            
# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end