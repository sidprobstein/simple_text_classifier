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
       
#     soup = BeautifulSoup(f, 'html.parser')
#         
#     # kill all script and style elements
#     for script in soup(["script", "style"]):
#         script.decompose()    # rip it out
#     
#     divs = soup.find_all('div')
    
    # setup    
    chunk_tags = [ 'div' ]
    remove_tags = [ 'script', 'style' ]
    is_tag = False
    tag = ""
    is_close_tag = False
    is_link = False
    last = ""
    section_len = 0
    section_links = 0
    emit = True

    for ch in html:        
        # print ch, "\tis_tag:", is_tag, "\tis_close_tag:", is_close_tag, "\temit:", emit
        if ch == '<':
            # start tag
            is_tag = True
            is_close_tag = False
            tag = ""
            continue
        if ch == '>':
            # end tag
            is_tag = False
            # handle tag
            if not is_close_tag:
                if tag in remove_tags:
                    emit = False
            else:
                if tag in remove_tags:
                    emit = True
            continue
        if is_tag:
            # in tag
            if ch == '/':
                is_close_tag = True
            else:
                tag = tag + ch
        else:
            if emit:
                print ch,
                
                
                
                
                
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