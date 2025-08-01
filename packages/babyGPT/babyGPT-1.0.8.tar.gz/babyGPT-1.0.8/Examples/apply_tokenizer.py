#!/usr/bin/env python

##   apply_tokenizer.py

"""
If you have created a new JSON file for the tokenizer, this script is just to test
the tokenizer on a small txt file

Call syntax:

     python3  apply_tokenizer.py   text_sample_for_testing.txt   104_babygpt_tokenizer_49270.json

"""

from transformers import PreTrainedTokenizerFast

#import itertools
import string
import re
import sys, os
import json
import random


seed_value = 0
random.seed(seed_value)
os.environ['PYTHONHASHSEED'] = str(seed_value)

debug = False

if len(sys.argv) != 3:   
    sys.stderr.write("Usage: %s <textfile name for tokenization>  <tokenizer_json>\n" % sys.argv[0])            
    sys.exit(1)

testing_iter = 0
textfile =  sys.argv[1]
tokenizer_json = sys.argv[2]

tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_json)

with open( textfile, encoding='utf8', errors='ignore' ) as f: 
    text = f.read()                                           
if debug:
    FILE = open("junk.txt", 'w')
    FILE.write(text)                                                             
    print("\n\nnumber of characters in the file: ", len(text))
    print("The size of the file in bytes: ", os.stat(textfile).st_size)
    FILE.chose()

print("\n\nTHE ORIGINAL TEXT: : ", text)

encoded = tokenizer.encode(text, add_special_tokens=False) 

print("\n\nENCODED INTO INTEGERS: ", encoded)

decoded = tokenizer.decode(encoded, skip_special_tokens=True)

print("\n\nDECODED SYMBOLIC TOKENS FROM THE INTEGERS: ", decoded)

