# -*- coding: utf-8 -*-

__version__   = '1.0.8'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2025-May-29'   
__url__       = 'https://engineering.purdue.edu/kak/distGPT/babyGPT-1.0.8.html'
__copyright__ = "(C) 2025 Avinash Kak. Python Software Foundation."


__doc__ = '''

babyGPT.py

Version: ''' + __version__ + '''
   
Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''



@title
CHANGE LOG:

Version 1.0.8:

    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Version 1.0.7:

    There was an error in the definition of BasicDecoderWithMasking that I have fixed
    in this version.  Despite the error, the module worked as intended but not as
    efficiently as one would have expected.

Version 1.0.6:

    I have fixed the error that caused the predicted tokens to be shifted by one
    position vis-a-vis the ground-truth tokens.

Version 1.0.5:
    
    Had a URL error in the setup.py of the previous version. The rest of the module
    remains unchanged.

Version 1.0.4:

    This is the first public release version of the module. This module was created
    for the Deep Learning class at Purdue University.


@title
INTRODUCTION:

    SPECIFIC GOALS FOR THIS MODULE:

    1) To introduce the students in Purdue's Deep Learning class to the foundational
       concepts in how to create a Base Language Model through self-supervised
       learning.  Large Language Models start out as Base Models that are
       subsequently fine-tuned with reinforcement learning.  The focus of this module
       is solely on Base Modeling.

    2) To demonstrate small-scale large-language modeling that, for educational
       purposes, can be run on a typical university lab GPU.

    3) To create a self-contained module that, given a set of media URLs, will
       download the articles from those websites (assuming they are not behind a
       paywall), train a BPE tokenizer from the corpus of the articles collected,
       create a Base Model from the corpus, and, subsequently, let you play with the
       model using the prompting script in the module.

    My main goal in babyGPT is to demonstrate that, for the purpose of teaching and
    learning, it is possible to create a small-scale end-to-end implementation that
    downloads a corpus of news media articles, trains a BPE tokenizer if you need a
    new one for the domain of the corpus you have collected, and, finally, uses the
    corpus for training an autoregressive model for the next token prediction based
    on unsupervised learning. After you have trained the model, you can test it with
    the prompting script that is included in the Examples directory. 


    LANGUAGE MODELING AND UNSUPERVISED LEARNING:

    There is no denying the fact that the recent advances in chatbots have set the
    world on fire. It's truly amazing to see a chatbot returning (most of the time) a
    smooth-reading and well-structured narrative in response to a prompt. As if that
    were not enough, it can also supply you with variants of the same narrative
    depending on how you prompt it and your randomization settings for the bot.

    One would think that this degree of competency shown by a chatbot would require a
    vast amount of human annotated data for training the neural networks used for the
    bot.

    The truth is exactly the opposite.  Most of the learning that takes place in
    order to train a chatbot is unsupervised --- that is, without any human
    supervision. The bot is given the simplest of the goals: To predict the next
    token given the tokens that have been seen so far.  To master this goal, the bot
    needs zero supervision.  All it needs to do is to use its neural network to make
    a prediction for the next token.  And, at training time, should this prediction
    be wrong, to estimate the error made, and then to backpropagate that error while
    adjusting the learnable weights in the network.  Until not too long ago most
    people would have thought that this type of learning would be much too weak to be
    of any practical use. But, as in all engineering, you cannot argue with something
    that actually works.  One great thing that has come out of AI research of the
    last two decades is that unsupervised learning not only works, it actually lends
    itself to designing powerful data driven frameworks without too much human
    intervention.


    TRANSFORMERS:

    The unsupervised learning of the sort described above is best implemented with
    Transformers. (See my material for the Week 13 lecture at Purdue's Deep Learning
    class for a detailed presentation on how can implement an English-to-Spanish
    translation framework using Transformers.)  And central to a Transformer-based
    architecture is the notion of Attention.  Attention means the extent to which
    each element at the input to a neural network attends to every other element in
    the same input.  For example, in a network for language translation, the network
    would use Attention to figure out the significance of each token in a
    source-language sentence to every other token in the same sentence.  If "car" was
    one of the tokens in a sentence at the input and a subsequent clause in the same
    sentence used the pronoun "it" that pointed to that car, the network would be
    able to figure out the connection between the "it" and the "car" tokens through
    Attention.  Along the same lines, the network would use Cross Attention to figure
    out the importance of each token in the source language to the different tokens
    in the target language.  As you can imagine, understanding such connections
    between the tokens would be critical to any network that is learning how to
    translate a source language sentence into a target language sentence.


@title
THE MAJOR COMPONENTS of babyGPT:

    babyGPT module contains the following Python classes:

             (1) ArticleGatherer 

             (2) ArticleDataset              [supplies the data downloader for training]

             (3) TrainTokenizer 

             (4) TransformerFG               [borrowed from Transformers in DLStudio]

             (5) MasterDecoderWithMasking;   [borrowed from Transformers in DLStudio]

             (6) PromptResponder

    In what follows, I'll introduce each of these components one by one.  Each
    component is a separate inner class of the main module class babyGPT.


    @tag1
    ArticleGatherer:

    About the ArticleGatherer, you supply it with a list of URLs to media news sites.
    It then uses the Newspaper module (which understands the structure of a typical
    news HTML file) to download the articles from each of those URLs.  It is
    important to keep in mind that ArticleGatherer skips over non-HTML article files
    at the media websites. Unfortunately, many popular news websites now hide their
    content behind paywalls implemented with JavaScript.  [Examples of such websites
    include www.nyt.com, www.wsj.com, www.bbc.com, etc.] For obvious reasons, if the
    list of the URLs you provide ArticleGatherer consists of mostly such websites, the
    size of the corpus you create for experimenting with babyGPT could be much to
    small to be any fun.


    @tag1
    ArticleDataset:

    After you have used ArticleGatherer to download the news articles for the
    training corpus, the next thing you are going to need is a dataloader. That's
    exactly what's provided by the ArticleDataset class.  It randomly shuffles all
    the articles gathered and creates a number of dataloading streams equal to the
    batch-size that you are using for training babyGPT. The data input for the i^th
    batch instance is provided by the i^th stream. Logically speaking, you can think
    of each stream as a concatenation of the news articles that were randomly chosen
    for that batch instance.


    @tag1
    TrainTokenizer:
    
    Tokenizers play a critical role in language modeling because they create a
    bounded vocabulary of the tokens that the language model must understand. This is
    done by using a split-and-merge approach in which you start by considering each
    different word in your corpus as a sequence of the most basic symbols, which can
    be ASCII characters as in the WordPiece tokenizer or the individual bytes, as in
    the BPE (Byte Pair Encoding) tokenizer.  Subsequently, you form subwords by,
    first, merging the most basic constituents like the bytes and, then, merging
    smaller subwords into longer subwords, on the basis of the frequencies of the
    merged subwords vis-a-vis the frequencies of the components that were merged. The
    merging process continues until you have reached the specified vocabulary size.
    What this logic implies is that if a long word in the corpus occurs sufficiently
    frequently, it will be represented by a single token.  On the other hand, a
    relatively short word that occurs rarely in the original corpus could be
    decomposed into shorter tokens.  It is in this manner that, with the WordPiece
    tokenizer, the BERT LLM has a vocabulary of around 30,000 tokens and, with the
    BPE tokenizer, the GPT-3 has a vocabulary of 50,000 tokens. Without such
    tokenization, the size of the vocabulary could grow continuously with the the
    size of the corpus.  As you can imagine, if a language modeler is ingesting
    terabytes of text, the vocabulary of the words it sees could run into millions.
    It is not possible to devise the probability-based logic for next-word prediction
    if your underlying vocabulary is unbounded.

    The module comes with a pre-trained tokenizer with a vocab size of around
    50,000 tokens.  I trained this tokenizer using the babyGPT module on the athlete
    news dataset created by Adrien Dubois. The name of the tokenizer JSON in the
    Examples directory is: 104_babygpt_tokenizer_49270.json 


    @tag1
    TransformerFG:

    About the TransformerFG component of babyGPT, as mentioned already, language
    modeling is best carried out with Transformer based implementations. To that
    end, I borrowed TransformerFG from DLStudio's Transformers module.
    TransformerFG is my implementation of the concept of the Transformer as
    proposed by Vaswani et al.  in their seminal paper "Attention is All You
    Need."  The suffix "FG" stands for "First Generation."


    @tag1
    MasterDecoderWithMasking:

    The MasterDecoderWithMasking part of babyGPT has also been borrowed from
    DLStudio's Transformers module.  To see the need for this component, note that
    unsupervised learning that is needed for autoregressive language modeling only
    uses the Decoder side of the Encode-Decoder paper that would otherwise be
    needed for a Transformer-based framework for translating one language into
    another. An example of such a framework is presented in the notes for my Week
    14 lecture at Purdue's Deep Learning class. That framework has two decoder
    implementations: MasterDecoder and MasterDecoderWithMasking.  If you are
    engaged in autoregressive modeling, you have no choice but to use the
    "WithMasking" version of the decoder.  As to the reason for the "Master"
    prefix in the name of the decoder, a language modeling code typically requires
    a number of Transformer layers, with each layer using multiple Attention Heads
    to calculate what's known as Self Attention. In my DLStudio code, I have
    refers to this layered organization of the Transformers as MasterEncoder and
    MasterDecoder, and to each Transformer layer as the BasicEncoder and the
    BasicDecoder.  Note that there's an interesting difference between the decoder
    logic as used in language translation and what you need for unsupervised
    learning in a GPT: When used for language translation, the decoder would also
    calculate Cross Attention, which is the attention between each element of the
    data coursing through the decoder and all the elements at the final output of
    the encoder.  The decoder as used for unsupervised learning in a GPT only
    needs to calculate Self Attention.


    @tag1
    PromptResponder:

    About the final component of babyGPT, PromptResponder, its purpose is to put the
    trained babyGPT model to use by having it respond appropriately to the prompts
    supplied by a user.  Given a prompt in the form of a sentence fragment, the
    PromptResponder uses its next-token prediction ability to keep on generating the
    tokens until it reaches the end-of-sentence token or until it has generated a
    specified number of sentences through this process.


@title
DEALING WITH THE PROBLEM OF CONTEXT DISRUPTION CAUSED BY THE "<SOS>" TOKEN:

    What comes in the way of training babyGPT are the textual discontinuities created
    by how a batch is constructed for each new iteration of training.  As explained
    elsewhere in this doc page, the list of all the documents in the training corpus
    is first randomized and then divided into a number of token streams, with one
    stream for each batch instance. (This randomization of the files and the
    division into token streams is carried out afresh at the beginning of each
    epoch.)  Subsequently, when a fresh batch is needed, for each batch instance you
    "draw" from its corresponding stream a max_seq_length number of tokens. The
    special <SOS> token is placed at the beginning of each such token stream segment
    and another special token <EOS> at the end.

    This insertion of the <SOS> and <EOS> tokens disrupts the continuity of the token
    streams as you imagine --- which runs contrary to the main point of the exercise
    which is to learn the continuity properties. Since the narrative continuity
    properties are context dependent, it would be fair to say that the <SOS> token
    causes a context disruption for the token that comes after <SOS> at the beginning
    of each batch instance.  Over the years, various strategies have been proposed to
    circumvent this problem, one of the most recent being the "sliding-window based
    Attention" as presented by Beltagy, Peters, and Cohan in their 2023 paper
    "Longformer: The Long-Document Transformer".  In this approach, a fixed-sized
    window is used to calculate the attention at the token that is at the center of
    the window.  In this manner, what is calculated for Self Attention is the extent
    to which each token attends to the W/2 tokens on each side of the token at the
    center.  As the authors say: "Using multiple stacked layers of such windowed
    attention results in a large receptive field, where top layers have access to all
    input locations and have the capacity to build representations that incorporate
    information across the entire input."

    In keeping with the spirit of babyGPT, I have used a much simpler approach to
    deal with the context-disruption problem created by the <SOS> token.  My
    solution is based on the idea I call "Context Buffer".  In the token input
    stream that corresponds to each batch instance, a context buffer is the last n
    tokens that are meant to serve as the context for the first real token in the
    same instance in the next batch.  

    To elaborate, let's assume that N is the size of the Context Window for your
    Transformer based processing of text.  N is the maximum length of the input token
    sequence for which you have designed your Transformer implementation.  [This also
    means that your Attention Map will be an array of size NxN.] And let n be the
    smallest number of previous tokens that you think will provide a reasonable
    context for predicting the current token.  So, during each training iteration,
    from each batch instance at the input, we want to save the last n tokens to serve
    as the context buffer for the new token sequence in the same batch instance.
    Therefore, at the next iteration you will feed n+N tokens into the transformer,
    but, as you can imagine, at the output of the transformer, you would only retain
    the N tokens that come after the context-buffer n tokens.

    It is this idea of context buffer that is invoked by the code in the second
    script mentioned at the beginning of this section.

    It is interesting to note that the above mentioned problem with context
    disruption does NOT arise with sentence-based language modeling (as in BERT)
    since <SOS> is what you would want to use for designating the start of the
    sentence.  (For such learning, you would also use another token, denoted <EOS>
    for "End of Sequence", to mark the end of a sentence.)


@title
INSTALLATION:

    The babyGPT class was packaged using setuptools.  For installation, execute
    the following command in the source directory (this is the directory that
    contains the setup.py file after you have downloaded and uncompressed the
    gzipped tar archive for the module):
 
            sudo python3 setup.py install

    On Linux distributions, this will install the module file at a location that
    looks like

             /usr/local/lib/python3.10/dist-packages/

    If you do not have root access, you have the option of working directly off
    the directory in which you downloaded the software by simply placing the
    following statements at the top of your scripts that use the
    babyGPT class:

            import sys
            sys.path.append( "pathname_to_babyGPT_directory" )

    To uninstall the module, simply delete the source directory, locate where the
    babyGPT module was installed with "locate
    babyGPT" and delete those files.  As mentioned above, the full
    pathname to the installed version is likely to look like
    /usr/local/lib/python2.7/dist-packages/babyGPT*

    If you want to carry out a non-standard install of the babyGPT
    module, look up the on-line information on Disutils by pointing your browser
    to

              http://docs.python.org/dist/dist.html

@title
USAGE:

    If you want to use babyGPT for unsupervised learning of a base model for a text
    corpus, you would need to construct an instance of the main babyGPT class and its
    supporting classes as follows:

    baby_gpt = babyGPT(
                        max_seq_length = max_seq_length,
                        batch_size = batch_size,
                        embedding_size = embedding_size,
                        num_basic_decoders = num_basic_decoders,
                        num_atten_heads = num_atten_heads,
                        optimizer_params = optimizer_params,
                        num_warmup_steps = num_warmup_steps,
                        masking = masking,
                        verify_text_corpus = False,
                        path_saved_model = {"decoder" : "./saved_decoder",                                                             
                                            "embedding_generator" : "./saved_embedding_generator",                             
                                           },
                      )
    
    xformer = baby_gpt.TransformerFG( 
                        max_seq_length = max_seq_length,
                        embedding_size = embedding_size,
                        tokenizer_json = tokenizer_json,
                        num_warmup_steps = num_warmup_steps,
                        optimizer_params = optimizer_params,
              )
    
    master_decoder = baby_gpt.MasterDecoderWithMasking(
                        xformer, 
                        num_basic_decoders = num_basic_decoders,
                        num_atten_heads = num_atten_heads,
                        masking = masking
                     )
    
    dataloader = baby_gpt.ArticleDatasetWithBufferedContext(
                        gpt = baby_gpt,
                        tokenizer_json = tokenizer_json,
                        context_window_size = context_window_size,
                        context_buffer_size = context_buffer_size,
                        articles_dir = articles_dir,
                 )

    

@title 
THE Examples DIRECTORY:

    This directory contains the following four scripts for working with babyGPT:

        1.  run_gatherer.py

            This script is for collecting a corpus for experimenting with babyGPT.
            The script requires a list of URLs as article sources as illustrated
            by the following example:

                urls = ['https://finance.yahoo.com','http://cnn.com',
                        'https://sports.yahoo.com',
                        'https://purdueexponent.org','https://slate.com',
                        'https://timesofindia.indiatimes.com',
                        'http://cnn.com',
                        'https://slate.com'
                       ]

        2.  train_tokenizer.py

            If the text corpus you have collected is for a specialized domain (such
            as movies, sports, healthcare, etc.), you are likely to get better
            results from babyGPT if you first train a new tokenizer for that domain.
            You train a new tokenizer merely by invoking this script after you have
            set its variable "articles_dir" so that it points to the corpus 
            directory.


        3.  create_base_model_with_buffered_context.py

            This is the script to run if you want to create a Base Model for your
            corpus.  By Base Model I mean a language model acquired through
            unsupervised learning from a training corpus.  Since this script calls on
            the core language modeling functionality of babyGPT, you have to set a
            relatively large number of parameters in the script.  These parameters
            are shown below:

                articles_dir
                tokenizer_json 
                max_seq_length 
                context_window_size
                context_buffer_size
                batch_size 
                embedding_size
                num_atten_heads 
                num_basic_decoders 
                optimizer_params
                num_warmup_steps


        4.  interact_with_prompts.py
 
            This is the script for interacting with a trained babyGPT model through
            prompts.  The idea is that you supply a small number of words (as, say,
            the beginning of a new thought) as a prompt and the model supplies the
            rest of the words to complete the thought.  At this time, the model
            extends your prompt until it reaches a period (or the end dictated by the
            size of the "max_seq_length" parameter.

@title
BUGS:

    Please notify the author if you encounter any bugs.  When sending email,
    please place the string 'babyGPT' in the subject line to get past the
    author's spam filter.


@title
ABOUT THE AUTHOR:

    The author, Avinash Kak, is a professor of Electrical and Computer Engineering
    at Purdue University.  For all issues related to this module, contact the
    author at kak@purdue.edu If you send email, please place the string
    "babyGPT" in your subject line to get past the author's spam
    filter.

@title
COPYRIGHT:

    Python Software Foundation License

    Copyright 2025 Avinash Kak

@endofdocs
'''

import sys,os,os.path
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as tvt
import numpy as np
import math
import random
import string
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import glob                                                                                                           
import json
import logging                        ## for suppressing matplotlib warning messages
import re
import itertools
import newspaper
from torch.utils.data import IterableDataset, DataLoader
from collections import Counter
from newspaper import Article
import blingfire as bling                     ## has the best sentence detector
from transformers import PreTrainedTokenizerFast
from tokenizers import Tokenizer                                                                                               
from tokenizers.pre_tokenizers import Whitespace 
import lightning as L


#############################################################################################################################
################################################  Top level utility functions  ##############################################

import signal

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def ctrl_c_handler( signum, frame ):             
    print("Killed by Ctrl C")                       
    os.kill( os.getpid(), signal.SIGKILL )       
signal.signal( signal.SIGINT, ctrl_c_handler )   


def dev():                                                                                                              
    pass
"""
    if torch.cuda.is_available():                                                                                       
#        return torch.device(f"cuda:0")                                                                                  
        return torch.device(f"cuda")                                                                                  
    return torch.device("cpu") 
"""

def gen(container):
    j = 0
    while j < len(container):
        yield container[j]
        j += 1


###%%%
#############################################################################################################################
#############################################   babyGPT Class Definition   ##################################################

class babyGPT(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''babyGPT constructor can only be called with keyword arguments for 
                      the following keywords: urls, max_seq_length, batch_size, embedding_size, num_atten_heads, beta1, beta2, epsilon,
                      num_warmup_steps, masking, use_gpu, verify_text_corpus, path_saved_model''')
        max_seq_length=batch_size=embedding_size=num_atten_heads=beta1=beta2=epsilon=num_warmup_steps=masking=use_gpu=verify_text_corpus=None
        urls=path_saved_model=None

        if 'urls' in kwargs                          :   urls = kwargs.pop('urls')
        if 'max_seq_length' in kwargs                :   max_seq_length = kwargs.pop('max_seq_length')
        if 'batch_size' in kwargs                    :   batch_size = kwargs.pop('batch_size')
        if 'embedding_size' in kwargs                :   embedding_size = kwargs.pop('embedding_size')
        if 'num_atten_heads' in kwargs               :   num_atten_heads = kwargs.pop('num_atten_heads')
        if 'beta1' in kwargs                         :   beta1 = kwargs.pop('beta1')
        if 'beta2' in kwargs                         :   beta2 = kwargs.pop('beta2')
        if 'epsilon' in kwargs                       :   epsilon = kwargs.pop('epsilon')
        if 'num_warmup_steps' in kwargs              :   num_warmup_steps = kwargs.pop('num_warmup_steps')
        if 'masking' in kwargs                       :   masking = kwargs.pop('masking')
        if 'use_gpu' in kwargs                       :   use_gpu = kwargs.pop('use_gpu')
        if 'verify_text_corpus' in kwargs            :   verify_text_corpus = kwargs.pop('verify_text_corpus')
        if 'path_saved_model' in kwargs              :   path_saved_model = kwargs.pop('path_saved_model')

        if urls:
            self.urls = urls
        else:
            self.urls = None 
        if max_seq_length:                         
            self.max_seq_length = max_seq_length    
        if batch_size:
            self.batch_size = batch_size
        if embedding_size:
            self.embedding_size = embedding_size
        if num_atten_heads:
            self.num_atten_heads = num_atten_heads
        if beta1:
            self.beta1 = beta1
        if beta2:
            self.beta2 = beta2
        if epsilon:
            self.epsilon = epsilon
        if num_warmup_steps:
            self.num_warmup_steps = num_warmup_steps
        if masking:
            self.masking = masking     
        if verify_text_corpus:
            self.verify_text_corpus = verify_text_corpus
        else:
            self.verify_text_corpus = False
        if path_saved_model:
            self.path_saved_model = path_saved_model


    ###%%%
    #############################################################################################################################
    ######################################  Start Definition of Inner Class ArticleGatherer  ###################################

    class ArticleGatherer:
        """
        This script is for collecting data for experimenting with the Transformer based
        unsupervised learning code in baby_gpt.py.  

        The articles are downloaded from the URLs that are specified by the argument 'urls' in the
        constructor shown below.  See the script "create_base_model.py" in the Examples directory
        for how to set the URL strings for this argument.  Here are some examples:

            urls = ['https://finance.yahoo.com','http://cnn.com',
                     'https://timesofindia.indiatimes.com',
                     'https://purdueexponent.org','https://slate.com', 
                     'https://sports.yahoo.com']
    
            urls = ['http://cnn.com']
    
            urls = ['https://slate.com']
    
            urls = ['https://timesofindia.indiatimes.com']
    
        """
        def __init__(self, gpt, urls, articles_dir = 'saved_articles_dir'):
            ##  'urls' is a local array in which we store all the article URLs from where we want to 
            ##   download the news articles:
            self.urls = gpt.urls
            self.articles_dir = articles_dir

        def download_articles(self):
            if os.path.exists(self.articles_dir): 
                articles = glob.glob(self.articles_dir + "/*") 
                for file in articles:        
                    if os.path.isfile(file):       
                        os.remove(file)      
                    else:       
                        files = glob.glob(file + "/*")         
                        list(map(lambda x: os.remove(x), files))
            else:       
                os.mkdir(self.articles_dir)      
            master_list_article_links =  []
            for url in self.urls:
                print("\n\nDownloading from URL: %s\n\n" % url)
                scraped = newspaper.build( url, memoize_articles=False )
                for article_link in scraped.articles:
                    master_list_article_links.append( article_link.url )
                    print(article_link.url)
                print("\n\nThe number of available articles: ", scraped.size())
            print("\n\n\nHere is a dump of the article url's from all the news websites: ", master_list_article_links)
            print("\n\n\nTotal number of articles in the dump: ", len(master_list_article_links) )

            article_index = 0
            for item_url in master_list_article_links:
                if not item_url.endswith(".html"):
                     continue
                article_file_name =  self.articles_dir + "/" +  "article_" + str(article_index) + ".txt"
                FILE = open(article_file_name, 'w')
                try:
                    article = Article(item_url)
                    article.download()
                    article.parse()
                except:
                    continue
                print("downloaded ", article_file_name)
                text = article.text
                FILE.write(text)
                FILE.flush()
                FILE.close()
                article_index += 1
    


    ###%%%
    #############################################################################################################################
    ######################################  Start Definition of Inner Class TrainTokenizer  #####################################

    class TrainTokenizer:
        """Tokenizers play a critical role in language modeling because they create a
        fixed-sized vocabulary for the corpus you are working with --- regardless of
        the size of the corpus itself.  Unless your text corpus is based on a set of
        documents frozen in time, ordinarily, as the size of a text corpus goes up,
        so does the size of the vocabulary --- despite the illusion to the contrary
        created by the fixed sizes of the language dictionaries you have seen all
        your life.  How we express ourselves is a living thing.  We are constantly
        inventing new words and new expressions; these form important components of
        what's referred to as the zeitgeist.

        Having a fixed-sized vocab is important because the loss functions used in
        deep-learning network used for language processing are based on
        maximum-likelihood prediction of the next token given the tokens seen
        previously.  That requires estimating the probabilities associated with all
        possible tokens at the next position.  As you can imagine, it would be
        impossible to engage in such probabilistic reasoning if you did not know in
        advance the size of the vocabulary.

        """
        def __init__(self, corpus_directory, target_vocab_size=50000):
            import babyGPT
            version_str =  babyGPT.__version__
            version_str = version_str.replace(".", "")
            self.tokenizer_json_stem   =   version_str + "_babygpt_tokenizer_"
            self.corpus_dir = corpus_directory
            self.unk_token = "[UNK]"                    # token for undecipherable bytes
            self.spl_tokens = ["<UNK>", "<SEP>", "<MASK>", "<CLS>"] 
            self.target_vocab_size = target_vocab_size

            ##  Since we are assuming utf-8 encoding of the text corpus, we already have
            ##  the mappings between the numbers 0 through 255 and their corresponding
            ##  tokens as would be yielded by calling the Python function chr() on the
            ##  integers between 0 and 255.  [For example, chr(255) returns the character
            ##  'ÿ'. What that means is that 255 is the Unicode code point for this symbol.]
            ##  So the first available index for a new token produced by the merge rule 
            ##  would be 256:
            self.next_index_available = 256
            ##  I use "testing_iter" for producing the intermediate results during training:
            self.testing_iter = 0                         

      
        def train_tokenizer(self):
            """
            Tokenization steps: 

            -- Start with a base vocabulary for the tokens that consists of all 256 integer
               values that can be taken by a byte.

            -- Search through consecutively occurring numeric codes for the Unicode bytes to 
               find the pair that is the most frequent

            -- Replace all such pairs of the more elementary tokens with the new token for all
               the words
           
            -- Apply the logic described above iteratively until the size of the tokenizer
               vocab has reached the prescribed value.

            Note that the size of the tokenizer vocabulary is sum of the size of the Base Vocab
            and the number of merges.  The Base Vocab consists of the unique individual
            characters in the training dataset
            """

            def word_as_num_seq(word):
                for char in list(word):
                    if char not in char_to_num_dict:
                        char_to_num_dict[char] = self.next_index_available
                        merge_rules_dict[ self.next_index_available ] = char
                        self.next_index_available += 1       
                return [char_to_num_dict[char] for char in list(word) ]
            
            def get_str_token( num ):
                """
                Note that merge_rules_dict is what becomes the vocab eventually.  We make the
                conversion by reversing the <key,num> pairs in merge_rules_dict.
                """
                if num in num_to_char_dict:
                    return num_to_char_dict[num]
                elif num in merge_rules_dict:
                    return merge_rules_dict[num]
                else:
                    sys.exit("\n\n[get_str_token]  merge_rules_dict has no merge rule for the int token %d\n\n" % num)
            
            def subword_for_num_seq( num_seq ):
                subword = ""
                for num in num_seq:
                    if num in num_to_char_dict:
                        subword += chr(num)
                    elif num in merge_rules_dict:
                        subword += merge_rules_dict[num]
                    else:
                        sys.exit("\n\n[subword_for_num_seq] merge_rules_dict has no merge rule for the int token %d\n\n" % num)
                return subword
            
            def update_tokenizer_dict( tokenizer_dict, most_frequent_pair, new_token_as_num ):
                new_tokenizer_dict = {word : [] for word in tokenizer_dict}
                for word in tokenizer_dict:
                    str_rep = ",".join(str(i) for i in tokenizer_dict[word])
                    to_be_replaced_pair =  r"\b" +  ",".join(str(i) for i in most_frequent_pair) + r"\b"
                    replacement = str(new_token_as_num) 
                    output_str= re.sub(to_be_replaced_pair, replacement, str_rep)
                    new_tokenizer_dict[word]  =  [int(i) for i in output_str.split(",")]
                return new_tokenizer_dict
            
            
            def find_best_ngram_and_update_word_tokens_dict(tokenizer_dict):
                all_consec_pairs_dict = { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:] ) ) for word in tokenizer_dict }
                all_consec_triples_dict =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:] ) ) 
                                                                                                                     for word in tokenizer_dict }
                all_consec_quads_dict   =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:], 
                                                                                        tokenizer_dict[word][3:] ) ) for word in tokenizer_dict }   
                all_consec_all_ngrams_dict = {}
                for word in all_consec_pairs_dict:
                    if word in all_consec_triples_dict and  word in all_consec_quads_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word] + all_consec_quads_dict[word]
                    elif word in all_consec_triples_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word]
                    else:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word]
                all_consec_all_ngrams_dict  =   {word : all_consec_all_ngrams_dict[word] for word in all_consec_all_ngrams_dict 
                                                                                                      if len(all_consec_all_ngrams_dict[word]) > 0}
                most_frequent_ngram = list(Counter( list( itertools.chain(*all_consec_all_ngrams_dict.values()) ) ).keys()) [0]
                string_for_merges_array = "%s %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]))
                merges.append( string_for_merges_array )
                subword_for_most_frequent_ngram  =  subword_for_num_seq( most_frequent_ngram )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] Will merge the following subwords for the new most frequently occurring subword:" % self.testing_iter)
                    if len(most_frequent_ngram) == 2:
                        print("%s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1])))
                    elif len(most_frequent_ngram) == 3:
                        print("%s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                                                         get_str_token(most_frequent_ngram[2] )))        
                    else:
                        print("%s    %s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                        get_str_token(most_frequent_ngram[2]), get_str_token(most_frequent_ngram[3]) ))
                    print("\n\nAdding to tokenizer vocab: ",  subword_for_most_frequent_ngram)
                merge_rules_dict[self.next_index_available] = subword_for_most_frequent_ngram
                new_tokenizer_dict = update_tokenizer_dict( tokenizer_dict, most_frequent_ngram, self.next_index_available )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] UPDATED tokenizer dict:\n" % self.testing_iter)
                    for word in new_tokenizer_dict:
                        print("%s  =>  %s" % (word, str( [get_str_token(i) for i in new_tokenizer_dict[word]] )))
                self.next_index_available += 1
                return new_tokenizer_dict
            seed_value = 0
            random.seed(seed_value)
            os.environ['PYTHONHASHSEED'] = str(seed_value)
            dir_textfiles =  self.corpus_dir
            ##  The dict defined in the next statement stores the mappings from the symbolic tokens to integers that represent 
            ##  them. For the number range 0 through 255, the mappings stored are those that are returned by calling chr() on 
            ##  the Unicode numbers between 0 and 255. Subsequently, as larger tokens are constructed by merging the "sub-word" 
            ##  tokens, we add those tokens and their associated numbers to this dict.   
            char_to_num_dict = { chr(num) :  num for num in range(256) }
            num_to_char_dict = { num : chr(num) for num in range(256) }
            merge_rules_dict = { i : "" for i in range(256, self.target_vocab_size) }
            ##  I store all pairwise merges in the following array.  Each element of this array is a string 
            ##  that looks like  "str1 str2" where str1 and str2 are the two subwords that are to be merged together.
            merges = []                            
            text = ""
            ##  Data text data from file. Note that using errors='ignore' may NOT be the right option for opening a file:  
            ##  https://stackoverflow.com/questions/45529507/unicodedecodeerror-utf-8-codec-cant-decode-byte-0x96-in-position-35-invalid
            if os.path.exists(dir_textfiles):
                    textfiles = glob.glob(dir_textfiles + "/*")
                    print("\n\nNumber of text files: ", len(textfiles))
                    for filedoc in textfiles:
                        if os.path.isfile(filedoc):
                            with open( filedoc, encoding='utf8', errors='ignore' ) as f:
                                text += f.read()
            print("\n\nlength of the text string: ", len(text))
            ##  We will store the merged char mappings for the new tokens in this dictionary
            merged_symbols_dict = {num : None for num in range(256, self.target_vocab_size) } 
            
            all_words = text.split()
            print("\n\nNumber of words in the list 'all_words': ", len(all_words))
            print("\n\nfirst 100 entries in all_words: ", all_words[:100])
            ##  We need the word frequencies BECAUSE we need to find the most frequently occurring token pair 
            ##  in the corpus.  That is, for a given token pair, we need to know the number of words in which 
            ##  that pair occurs.
            words_with_counts = Counter(all_words)
            unique_words = list(set( all_words ))
            print("\n\nnumber of UNIQUE words: ", len(unique_words))
            print("\nfirst 100 UNIQUE words: ", unique_words[:100])
            word_tokens_dict =  { word : word_as_num_seq(word) for word in unique_words }                     ##  Initialization of word_tokens_dict
            print("\n\nIterative learning of the merge rules:\n\n")
            for i in range(256): 
                merge_rules_dict[i] = chr(i)           ## the char returned by the function chr(i) is the char under utf-8 encoding
            while self.next_index_available <= self.target_vocab_size:
                self.testing_iter += 1
                new_word_tokens_dict = find_best_ngram_and_update_word_tokens_dict( word_tokens_dict )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter = %d] Size of the tokenizer vocab: " % self.testing_iter,  self.next_index_available-1) 
                word_tokens_dict = new_word_tokens_dict
#                if self.testing_iter % 10000 == 0:
                if self.testing_iter % 5000 == 0:
                    FILE = open("merge_rules_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
                    for i in merge_rules_dict: 
                        FILE.write("%d       =>       %s\n" % (i, merge_rules_dict[i]))
                    merge_rules_dict[self.target_vocab_size + 1] = "<UNK>"
                    vocab = {val : key for (key,val) in merge_rules_dict.items()}
                    print("\n\n[testing_iter: %d] vocab: " % self.testing_iter, vocab)
                    print("\n\n[testing_iter: %d] merges array:" % self.testing_iter, merges)
                    vocab_and_merges =  {"version" : "1.0", 
                                         "truncation" : None,
                                         "padding" : None,
                                         "added_tokens" : [
                                              {"id" : self.target_vocab_size+1, 
                                               "content" : "<UNK>",
                                               "single_word": False,  
                                               "lstrip": False,
                                               "rstrip": False, 
                                               "normalized": False, 
                                               "special": True,
                                              },
                                         ],
                                         "normalizer": None,
                                         "pre_tokenizer": {
                                             "type": "Whitespace"
                                         },  
                                         "model" :  {"type": "BPE", "dropout" : None, "vocab" :  vocab,  "merges" : merges } }
                    with open(self.tokenizer_json_stem + str(self.testing_iter) + ".json", "w") as outfile:
                        json.dump(vocab_and_merges, outfile, indent=4)
            FILE = open("merge_rules_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
            for i in merge_rules_dict: 
                FILE.write("%d       =>       %s\n" % (i, merge_rules_dict[i]))
            merge_rules_dict[self.target_vocab_size + 1] = "<UNK>"
            vocab = {val : key for (key,val) in merge_rules_dict.items()}
            print("\n\nvocab: ", vocab)
            print("\n\nmerges array:", merges)
            vocab_and_merges =  {"version" : "1.0", 
                                 "truncation" : None,
                                 "padding" : None,
                                 "added_tokens" : [
                                      {"id" : self.target_vocab_size+1, 
                                       "content" : "<UNK>",
                                       "single_word": False,  
                                       "lstrip": False,
                                       "rstrip": False, 
                                       "normalized": False, 
                                       "special": True,
                                      },
                                 ],
                                 "normalizer": None,
                                 "pre_tokenizer": {
                                     "type": "Whitespace"
                                 },  
                                 "model" :  {"type": "BPE", "dropout" : None, "vocab" :  vocab,  "merges" : merges } }
            with open(self.tokenizer_json_stem + str(self.testing_iter) + ".json", "w") as outfile:
                json.dump(vocab_and_merges, outfile, indent=4)
            


    ###%%%
    #############################################################################################################################
    #############################  Start Definition of Inner Class ArticleDatasetWithBufferedContext  ###########################

    class ArticleDatasetWithBufferedContext:    
        """
        The parameter 'context_window_size' is related to how many tokens you can feed into the
        transformer at one iteration as the training corpus is being scanned.  In my Week 14 lecture
        on Transformers, I used the notation 'max_seq_len' for this parameter.

        """
        def __init__(self, gpt, tokenizer_json, context_window_size, context_buffer_size=7, articles_dir='saved_articles_dir'):

            if os.path.exists(articles_dir): 
                num_articles = len(glob.glob(articles_dir + "/*")) 
                if gpt.verify_text_corpus:
                    if num_articles == 0:
                        sys.exit("\n\nAborting --- You have no articles in the articles directory.  You may need to first use the ArticleGatherer")
                    ans = input("\n\nYou have %d articles in the articles directory. Continue? Enter 'y' if yes: " % num_articles)
                    ans = ans.strip()
                    if ans != ('y' or 'yes'): 
                        print("\n\nPlease run the 'run_gatherer()' function to gather the news articles.\n\n")
            else:
                sys.exit("\n\nAborting --- Your articles directory %s does not exist." % articles_dir)
            print("\n\nThe Dataloader will be applied to the previously collected trove of articles in %s." % articles_dir)
            print()
            self.dir_collected_articles = articles_dir
            self.num_articles = num_articles
            self.context_buffer_size = context_buffer_size
            ## The file named below must be a json file created by a tokenizer training routine:
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.batch_size = gpt.batch_size
            self.context_window_size = context_window_size
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.articles = []
            self.articles_for_batch_instances = []
            self.encoded_streams = {}              ## A dict whose keys are batch instance indexes            
            self.all_encoded_streams  =   []       ## A list of the values in the above dict
            self.iteration_index = 0               ## This value is reset to 0 at the beginning of each new epoch
            self.epoch_index = 0
            self.datastreams_initialized = False

        def generate_article_streams(self):
            debug = False
            def gen(container):
                j = 0
                while j < len(container):
                    yield container[j]
                    j += 1
            random.shuffle(self.articles)
            self.articles_for_batch_instances = [self.articles[i:i+len(self.articles)//self.batch_size] for i in range(self.batch_size)]
            self.encoded_streams =  []
            ## Create a stream of encoding for each batch instance
            for i in  range(self.batch_size):
                article_gen = gen( self.articles_for_batch_instances[i] )
                encoded_stream = [] 
                for article in article_gen:
                    if article is None: break
                    FILE = open(article)
                    text = FILE.read()
                    if debug:
                        encoded = self.tokenizer.encode(text)
                        print("\n\n\ntext in article: ", text)
                        print("after tokenization and encoding: ", encoded)
                        the_tokens = [self.inverse_lookup[code] for code in encoded]
                        print("the individual tokens: ", the_tokens)
                    encoded_stream += self.tokenizer.encode(text)
                self.encoded_streams.append( encoded_stream )
    

        def generate_article_sequences_for_batch_instances(self):
            """
            "equalization" here means that we want all the streams AS EQUAL IN LENGTH AS POSSIBLE
            based on N different attempts at article randomization.  Highly unequal stream lengths 
            can make GPT learning inefficient --- and sometimes impossible.
            """
            debug = False
            ## We need to find the total number of tokens in all the articles in our corpus.  Subsequently,
            ## when we partition the corpus into sub-corpora, with one sub-corpus for each batch instance,
            ## we want to make sure that the total number of tokens available for the token-stream created
            ## for each batch instance is roughly the same.
            article_sizes = { article : None for article in self.articles }  ## size is measured in terms of the number of tokens
            master_article_gen = gen(self.articles)
            total_num_tokens = 0 
            for article in master_article_gen:
                FILE = open(article)
                text = FILE.read()
                article_tokens = self.tokenizer.encode( text )
                article_sizes[article] = len(article_tokens) 
                total_num_tokens += len(article_tokens)

            if debug:
                print("\n\narticle sizes: ", article_sizes)
                print("\n\ntotal_num_tokens: ", total_num_tokens)
                print("\n\n\n")

            ##  Now we want to assign articles to each batch instance in such a way that the total number
            ##  of tokens assigned to a batch instance is approximately the same for batch instances. I am
            ##  going to use the followings dicts for this logic:
            num_tokens_per_batch_instance = total_num_tokens // self.batch_size
            article_sequence_for_batch_instance = {i : [] for i in range(self.batch_size)}           ## The sub-corpora of articles
            char_stream_size_for_batch_instance = {i : 0 for i in range(self.batch_size)}          ## The token stream for each sub-corpus

            ##  Now we are ready to create a sub-corpus for each batch instance. Each sub-corpus will eventually 
            ##  be turned into a token stream.  The epoch-to-epoch randomization of the input data would consist
            ##  of randomizing the sequence of articles (meaning, the order in which the articles appear) in
            ##  each sub-corpus.
            for article in article_sizes:
                ##  This is a variant of the heuristic algorithms used commonly for solving the combinatorial NP-Hard BIN 
                ##  PACKING Optimization problem in which the object are placed in unit-sized bins so as to minimize the
                ##  bins used.  The heuristic I have used here is to assign an article to that sub-corpus that currently
                ##  has the least total number of tokens in it. REMEMBER we measure the size of an article in terms of the 
                ##  number of tokens needed for that article.
                smallest_idx =  (sorted(char_stream_size_for_batch_instance, key=char_stream_size_for_batch_instance.get ))[0]
                article_sequence_for_batch_instance[smallest_idx].append(article)
                char_stream_size_for_batch_instance[smallest_idx] += article_sizes[article]
            ##  Let's now check we did a good job of roughly equalizing the number of tokens for each sub-corpus:
            for i in  range(self.batch_size):
                total_num_tokens = 0 
                article_gen = gen(article_sequence_for_batch_instance[i])
                for article in article_gen:
                    FILE = open(article)
                    text = FILE.read()
                    article_tokens = self.tokenizer.encode( text )
                    article_sizes[article] = len(article_tokens) 
                    total_num_tokens += len(article_tokens)
         
            self.article_sequence_for_batch_instance = article_sequence_for_batch_instance

        def generate_token_streams_for_batch_instances(self):
            debug = False 
            article_sequence_for_batch_instance  = self.article_sequence_for_batch_instance
            for seq_idx in article_sequence_for_batch_instance:
                random.shuffle( article_sequence_for_batch_instance[seq_idx] )          ## randomization at the beginning of each epoch
            ## Create a stream of encoding for each batch instance
            self.encoded_streams =  {i : [] for i in range(self.batch_size)}
            for i in  range(self.batch_size):
                article_gen = gen(article_sequence_for_batch_instance[i])
                for article in article_gen:
                    FILE = open(article)
                    text = FILE.read()
                    ## Change made on Jan 29, 2025. Insert underscore between the words to help out with the detokenization step:
                    all_words = text.split()  
                    all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words] 
                    text = ' '.join(all_words)
                    article_tokens = self.tokenizer.encode( text )
                    self.encoded_streams[i] += article_tokens
            ## Now let's check the difference in length between the longest batch-instance stream
            ## and the shortest batch-instance stream:
            self.all_encoded_streams = list(self.encoded_streams.values())
            shortest_encoded_stream = min(self.all_encoded_streams, key=lambda x: len(x))
            longest_encoded_stream = max(self.all_encoded_streams, key=lambda x: len(x))
            stream_len_disparity =  len(longest_encoded_stream)  -  len(shortest_encoded_stream) 
            if debug:
                print("\n\nlength of the shortest stream: ", len(shortest_encoded_stream))
                print("length of the longest stream: ", len(longest_encoded_stream))
                print("value of stream_len_disparity: ", stream_len_disparity)


        def initialize_tokenized_data_streams(self):
            if self.datastreams_initialized == False:
                self.articles = glob.glob(self.dir_collected_articles + "/*")               
                self.generate_article_sequences_for_batch_instances()
                self.generate_token_streams_for_batch_instances()
                self.datastreams_initialized = True

        def dataloader_for_buffered_context(self, how_many):
            """
            The argument "how_many" means the size of the context_window_size that is specified in the call to the 
            constructor of ArticleDatasetWithBufferedContext. 

            This function returns a batch of token sequences on each call.  A batch is constructing by pulling the token sequences 
            for each batch instance from the 'batch_size' number of token streams created in the constructor of the 'Ddataloader'
            class. When that process gets too close the end of the shortest of the 'batch_size' number of streams, the articles 
            are randomized again for assignment to the individual batch-instance streams.

            The variable   self.iteration_index  keeps track of where the downloader is in each batch-instance stream as feed data
            one batch at a time into the Transformer.
            """
            debug = False
            batch_size = self.batch_size
            context_window_size = how_many
            cws_minus_one = context_window_size - 1
            codes_for_SOS = [89, 90, 91, 92, 93, 94, 96, 97, 98]

            if any( len( self.all_encoded_streams[i][self.iteration_index*cws_minus_one : ] )  < cws_minus_one for i in range(batch_size) ):
                self.epoch_index += 1
                print("\n\nStarting epoch: %d\n" % (self.epoch_index + 1))
                self.iteration_index = 0

            ## self.iteration_index == 0  means we are starting a new epoch
            if self.datastreams_initialized and self.iteration_index == 0:
                self.articles = glob.glob(self.dir_collected_articles + "/*")               
                self.generate_article_sequences_for_batch_instances()
                self.generate_token_streams_for_batch_instances()

            out = np.zeros(shape=(batch_size, context_window_size), dtype=int)

            for i in range(batch_size):
                out[i,1:] =  self.all_encoded_streams[i][self.iteration_index*cws_minus_one :  (self.iteration_index+1) * cws_minus_one]
                out[i,0] = 89
            self.iteration_index  += 1
            return out

        def test_dataloader(self, how_many):
            data = self.dataloader_for_buffered_context(how_many)
            print("\n\n\nshape of the data returned by the dataloader: ", data.shape)
            print("\n\ndata returned by the dataloader:")
            print(data)
            tokens = [[self.inverse_lookup[code] for code in data[i]] for i in range(self.batch_size)]
            print(tokens)
            
            data = self.dataloader_for_buffered_context(how_many)
            print("\n\n\nshape of the data returned by the dataloader: ", data.shape)
            print("\n\ndata returned by the dataloader:")
            print(data)
            tokens = [[self.inverse_lookup[code] for code in data[i]]  for i in range(self.batch_size)]
            print(tokens)
            

        def display_token_vocab(self):  
            for code in self.inverse_lookup:
                print("%d        =>       %s" % (code , str( self.inverse_lookup[code] ) ) )
            

    ###%%%
    #############################################################################################################################
    ########################################  Start Definition of Inner Class TransformerFG  ####################################

    class TransformerFG(nn.Module):             
        """
        I have borrowed from the DLStudio's Transformers module.  "FG" stands for "First Generation" --- which is the Transformer
        as originally proposed by Vaswani et al.
        """
        def __init__(self, max_seq_length, embedding_size, tokenizer_json, num_warmup_steps=None, optimizer_params=None):
            super(babyGPT.TransformerFG, self).__init__()
            self.max_seq_length = max_seq_length
            self.embedding_size = embedding_size
            self.num_warmup_steps = num_warmup_steps
            self.optimizer_params = optimizer_params
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.vocab_size = self.tokenizer.vocab_size
    
        def sentence_with_words_to_ints(self, sentences, lang):
            sentence_to_ints = torch.ones(len(sentences), self.max_seq_length, dtype=torch.long)
            for i in range(len(sentences)):
                words = sentences[i].split(' ')
                for j,word in enumerate(words):
                    sentence_to_ints[i,j] = self.en_vocab_dict[word] if lang=="en" else self.es_vocab_dict[word]
            return sentence_to_ints
    
    class EmbeddingGenerator(nn.Module):
        def __init__(self, xformer, embedding_size):
            super(babyGPT.EmbeddingGenerator, self).__init__()
            tokenizer = PreTrainedTokenizerFast(tokenizer_file=xformer.tokenizer_json)
            self.vocab_size =  xformer.vocab_size
            self.embedding_size = embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embed = nn.Embedding(self.vocab_size, embedding_size)

        def forward(self, sentence_tensor):                                                                 
            sentence_tensor = sentence_tensor
            ## Let's say your batch_size is 4 and that each sentence has a max_seq_length of 10.
            ## The sentence_tensor argument will now be of shape [4,10].  If the embedding size is
            ## is 512, the following call will return a tensor of shape [4,10,512)
            word_embeddings = self.embed(sentence_tensor)
            position_coded_word_embeddings = self.apply_positional_encoding( word_embeddings )
            return position_coded_word_embeddings

        def apply_positional_encoding(self, sentence_tensor):
            position_encodings = torch.zeros_like( sentence_tensor ).float()
            ## Calling unsqueeze() with arg 1 causes the "row tensor" to turn into a "column tensor"
            ##    which is needed in the products shown below. We create a 2D pattern by 
            ##    taking advantage of how PyTorch has overloaded the definition of the infix '*' 
            ##    tensor-tensor multiplication operator.  It in effect creates an output-product of
            ##    of what is essentially a column vector with what is essentially a row vector.
            word_positions = torch.arange(0, self.max_seq_length).unsqueeze(1)            
            div_term =  1.0 / (100.0 ** ( 2.0 * torch.arange(0, self.embedding_size, 2) / float(self.embedding_size) ))
            position_encodings[:, :, 0::2] =  torch.sin(word_positions * div_term)                             
            position_encodings[:, :, 1::2] =  torch.cos(word_positions * div_term)                             
            return sentence_tensor + position_encodings

    ###%%%
    #######################################################################################################################
    ###################################  Self Attention Code for TransformerFG  ###########################################

    class SelfAttention(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads):
            super(babyGPT.SelfAttention, self).__init__()
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embedding_size = xformer.embedding_size
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.attention_heads_arr = nn.ModuleList( [babyGPT.AttentionHead(self.max_seq_length, 
                                    self.qkv_size, num_atten_heads)  for _ in range(num_atten_heads)] )           

        def forward(self, sentence_tensor):                                                                       
            concat_out_from_atten_heads = torch.zeros( sentence_tensor.shape[0], self.max_seq_length, 
                                                                  self.num_atten_heads * self.qkv_size,
                                                                  device=sentence_tensor.device,
                                                                  dtype=sentence_tensor.dtype)#.float()
            for i in range(self.num_atten_heads):                                                                 
                sentence_embed_slice = sentence_tensor[:, :, i * self.qkv_size : (i+1) * self.qkv_size]
                concat_out_from_atten_heads[:, :, i * self.qkv_size : (i+1) * self.qkv_size] =          \
                                                               self.attention_heads_arr[i](sentence_embed_slice)   
            return concat_out_from_atten_heads


    class AttentionHead(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self,  max_seq_length, qkv_size, num_atten_heads):
            super(babyGPT.AttentionHead, self).__init__()
            self.qkv_size = qkv_size
            self.max_seq_length = max_seq_length
            self.WQ =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WK =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WV =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.softmax = nn.Softmax(dim=-1)                                                                          

        def forward(self, sent_embed_slice):           ## sent_embed_slice == sentence_embedding_slice                
            Q = self.WQ( sent_embed_slice )                                                                           
            K = self.WK( sent_embed_slice )                                                                           
            V = self.WV( sent_embed_slice )                                                                           
            A = K.transpose(2,1)                                                                                      
            QK_dot_prod = Q @ A                                                                                       
            rowwise_softmax_normalizations = self.softmax( QK_dot_prod )                                              
            Z = rowwise_softmax_normalizations @ V                                                                    
            # Z = Z
#            coeff = 1.0/torch.sqrt(torch.tensor([self.qkv_size]).float()).to(dev())                
            # coeff = 1.0/torch.sqrt(torch.tensor([self.qkv_size]).float())
            coeff = 1.0 / math.sqrt(self.qkv_size)  ## This is the same as the above line, but more efficient --> Aditya
            Z = coeff * Z                                                                          
            return Z


    ###%%%
    #######################################################################################################################
    #########################################  Basic Decoder Class for TransformerFG  #####################################

    class BasicDecoderWithMasking(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads, masking=True):
            super(babyGPT.BasicDecoderWithMasking, self).__init__()
            self.masking = masking
            self.embedding_size = xformer.embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.self_attention_layer = babyGPT.SelfAttention(xformer, num_atten_heads)
            self.norm1 = nn.LayerNorm(self.embedding_size)
            self.norm2 = nn.LayerNorm(self.embedding_size)
            ## What follows are the linear layers for the FFN (Feed Forward Network) part of a BasicDecoder
            self.W1 =  nn.Linear( self.embedding_size, 4 * self.embedding_size )
            self.W2 =  nn.Linear( 4 * self.embedding_size, self.embedding_size ) 
            self.norm3 = nn.LayerNorm(self.embedding_size)

        def forward(self, sentence_tensor, mask):   
            masked_sentence_tensor = self.apply_mask(sentence_tensor, mask)
            Z_concatenated = self.self_attention_layer(masked_sentence_tensor)
            Z_out = self.norm1(Z_concatenated + masked_sentence_tensor)
            ## for FFN:
            basic_decoder_out =  nn.ReLU()(self.W1( Z_out.view( sentence_tensor.shape[0], self.max_seq_length, -1) ))                  
            basic_decoder_out =  self.W2( basic_decoder_out )                                                    
            basic_decoder_out = basic_decoder_out.view(sentence_tensor.shape[0], self.max_seq_length, self.embedding_size )
            basic_decoder_out =  basic_decoder_out  + Z_out 
            basic_decoder_out = self.norm3( basic_decoder_out )
            return basic_decoder_out

        def apply_mask(self, sentence_tensor, mask):
            # out = torch.zeros_like(sentence_tensor).float().to(dev())  
            out = torch.zeros_like(sentence_tensor)#.float().to(dev()) --> Aditya
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    


    ###%%%
    #######################################################################################################################
    ######################################  MasterDecoder Class for TransformerFG #########################################

    class MasterDecoderWithMasking(L.LightningModule):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_basic_decoders, num_atten_heads, context_window_size, context_buffer_size, batch_size, masking=True):
            super(babyGPT.MasterDecoderWithMasking, self).__init__()
            self.automatic_optimization = False
            self.xformer = xformer
            self.masking = masking
            self.max_seq_length = xformer.max_seq_length
            self.embedding_size = xformer.embedding_size
            self.vocab_size = xformer.vocab_size                                             
            self.basic_decoder_arr = nn.ModuleList([babyGPT.BasicDecoderWithMasking( xformer,
                                                    num_atten_heads, masking) for _ in range(num_basic_decoders)])  
            ##  Need the following layer because we want the prediction of each target word to be a probability 
            ##  distribution over the target vocabulary. The conversion to probs would be done by the criterion 
            ##  nn.CrossEntropyLoss in the training loop:
            self.out = nn.Linear(self.embedding_size, self.vocab_size)                                          
            self.n_warmup_steps = 4000
            self.context_window_size = context_window_size
            self.context_buffer_size = context_buffer_size
            # self.prev_seq_logprobs = torch.ones(batch_size, xformer.vocab_size, dtype=torch.float)
            self.register_buffer("prev_seq_logprobs",torch.ones(batch_size, xformer.vocab_size, dtype=torch.float)) #--> Aditya
            self.accum_times = []
            self.start_time = time.perf_counter()
            self.training_loss_tally  = []
            self.running_loss = 0.0
            self.training_iter = 0
            self.epoch = 0
            self.loss_normed  =  self.predicted_indexes =  self.predicted_word_logprobs =  self.token_sequences_in_batch = self.save_checkpoint_decoder = self.save_checkpoint_embedding_generator = None
            self.FILE_for_training_results = open("saved_training_with_buffered_context_results.txt",'w')
            self.FILE_for_training_loss = open("training_loss_vs_iterations.txt",'w')


        def forward(self, sentence_tensor, mask):                                                   
            out_tensor = sentence_tensor
            for i in range(len(self.basic_decoder_arr)):                                                 
                out_tensor = self.basic_decoder_arr[i](out_tensor, mask)                              
            word_index = mask.shape[0]
            last_word_tensor = out_tensor[:,word_index]                                      
            last_word_onehot = self.out(last_word_tensor)        
            output_word_logprobs = nn.LogSoftmax(dim=1)(last_word_onehot)                                     
            _, idx_max = torch.max(output_word_logprobs, 1)                
            ## the logprobs are over the entire vocabulary of the tokenizer
            return output_word_logprobs, idx_max

#        def training_step(self, inputs, prev_seq_logprobs, mask):   
        def training_step(self, inputs):   
            """
            input_tensor is the output of the embedding generator for a given sentence tensor  
            """
            input_tensor = torch.squeeze(inputs[0])
            data = torch.squeeze(inputs[1])
            token_sequences_in_batch = inputs[2][0]
            master_decoder_optimizer = self.optimizers()
#            prev_seq_logprobs = torch.squeeze(prev_seq_logprobs)
            # mask = torch.ones(1, dtype=int)                         ## initialize the mask
            mask = torch.ones(1, device=input_tensor.device, dtype=torch.long)       ## --> Aditya               
            predicted_indexes = [[] for i in range(input_tensor.shape[0])]
            detokenized_predicted_word_sequence = [[] for i in range(input_tensor.shape[0])]
            predicted_word_logprobs = []
            LOSS = 0.0
            for word_index in range(1,input_tensor.shape[1]):
                masked_input_seq = self.apply_mask(input_tensor, mask)                                
                predicted_word_logprobs, predicted_word_index_values = self(input_tensor, mask)
                if word_index == 0:
#                    predicted_word_logprobs = predicted_word_logprobs * prev_seq_logprobs
                    predicted_word_logprobs = predicted_word_logprobs * self.prev_seq_logprobs
                for i in  range(input_tensor.shape[0]):
                    predicted_indexes[i].append(predicted_word_index_values.cpu().numpy()[i])
                loss = nn.NLLLoss()(predicted_word_logprobs, data[:, word_index])           
                LOSS += loss
                # mask = torch.cat( ( mask, torch.ones(1, dtype=int) ) )
                mask = torch.cat((mask,torch.ones(1, device=input_tensor.device, dtype=torch.long)))  #--> Aditya                                       

            predicted_indexes = np.array(predicted_indexes)
            ## The following accounts for the fact that the first token is the SOS token, followed by context-buffer tokens
            predicted_indexes = predicted_indexes[:, self.context_buffer_size:]              
#            prev_iteration_data = new_prev_iteration_data
#            prev_seq_logprobs  =  predicted_word_logprobs
            self.prev_seq_logprobs  =  predicted_word_logprobs
            master_decoder_optimizer.zero_grad()
            self.manual_backward(LOSS)
#            master_decoder_optimizer.step_and_update_lr()                                                       
            master_decoder_optimizer.step()                                                       
            loss_normed = LOSS.item() / input_tensor.shape[0]
            self.loss_normed = loss_normed
            self.predicted_indexes = predicted_indexes
            self.predicted_word_logprobs = predicted_word_logprobs
            self.token_sequences_in_batch = token_sequences_in_batch
#            return loss_normed, predicted_indexes, predicted_word_logprobs, token_sequences_in_batch

#            loss_normed  =  self.loss_normed
#            predicted_indexes =  self.predicted_indexes
#            predicted_word_logprobs =   self.predicted_word_logprobs
#            token_sequences_in_batch =   self.token_sequences_in_batch

            self.running_loss += loss_normed
#            prev_seq_logprobs  =  predicted_word_logprobs
            self.prev_seq_logprobs =  predicted_word_logprobs
#            if self.training_iter % 100 == 99:    
            if self.training_iter % 10 == 9:    
                self.avg_loss = self.running_loss / float(100)
                self.training_loss_tally.append(self.avg_loss)
                self.FILE_for_training_loss.write("%s\n" % str(self.avg_loss))
                self.running_loss = 0.0
                current_time = time.perf_counter()
                time_elapsed = current_time-self.start_time
                print("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs]     loss: %.4f\n\n" % (self.epoch_index + 1, self.training_iter+1,time_elapsed,self.avg_loss)) 
                self.FILE_for_training_results.write("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs]     loss: %.4f\n\n\n" % (self.epoch_index, self.training_iter+1,time_elapsed,self.avg_loss)) 
                for j in range(self.batch_size):
#>>>>                    predicted_tokens[j] = dataloader.tokenizer.decode( predicted_indexes[j], skip_special_tokens=True )
                    self.predicted_tokens[j] = self.tokenizer.decode( self.predicted_indexes[j], skip_special_tokens=True )
                for i in random.sample( range(self.batch_size), 4 ): 
#>>>>                    print("Ground-Truth: ", detokenizer( ' '.join(token_sequences_in_batch[i]) ))
                    print("Ground-Truth: ", self.detokenizer( ' '.join(token_sequences_in_batch[i]) ))
                    print("GT Token Seq: ", ' '.join(self.token_sequences_in_batch[i] ))
                    print("   Predicted: ", self.predicted_tokens[i])
                    print(" Detokenized: ", self.detokenizer( self.tokenizer.decode( self.predicted_indexes[i], skip_special_tokens=True ) ))
                    print()
                    self.FILE_for_training_results.write("ground-truth: %s\n" % str(self.detokenizer( ' '.join(self.token_sequences_in_batch[i]) )))
                    self.FILE_for_training_results.write("GT Token Seq: %s\n" % str(' '.join(self.token_sequences_in_batch[i]) ))
                    self.FILE_for_training_results.write("   predicted: %s\n" % str(self.predicted_tokens[i]))
                    self.FILE_for_training_results.write(" detokenized: %s\n" % str(self.detokenizer( self.tokenizer.decode(self.predicted_indexes[i],skip_special_tokens=True))))
                    self.FILE_for_training_results.write("\n")
                self.training_iter += 1
                self.accum_times.append(current_time-self.start_time)
                self.FILE_for_training_results.flush()
                self.FILE_for_training_loss.flush()

            # if self.training_iter % self.checkpoint_frequency == self.checkpoint_frequency-1:    
                # print("\n\nSaving checkpoint at iteration: %d\n\n"% (training_iter+1))
                # self.save_checkpoint_decoder(self, self.checkpoint_dir, self.training_iter+1)
                # self.save_checkpoint_embedding_generator(self.embedding_generator, self.checkpoint_dir, self.training_iter+1)


        def configure_optimizers(self):
            optimizer = optim.AdamW(
                self.parameters(),
                lr=1e-4,
                weight_decay=5e-5
            )
            # Linear warmup scheduler
            warmup_scheduler = optim.lr_scheduler.LambdaLR(
                optimizer,
                lr_lambda=lambda step: min((step + 1) / self.n_warmup_steps, 1.0)
            )
            total_steps = self.trainer.estimated_stepping_batches if hasattr(self.trainer, 'estimated_stepping_batches') \
                                                                                         else 100000 # Placeholder total steps
            main_scheduler = optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=total_steps - self.n_warmup_steps
            )
    
            # Combine schedulers using SequentialLR
            scheduler = optim.lr_scheduler.SequentialLR(
                optimizer,
                schedulers=[warmup_scheduler, main_scheduler],
                milestones=[self.n_warmup_steps]
            )
            return {"optimizer": optimizer, "lr_scheduler": scheduler}
    

        def apply_mask(self, sentence_tensor, mask):  
            out = torch.zeros_like(sentence_tensor)#.float().to(dev())
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    

    ###%%%
    #######################################################################################################################
    ############################################### Training babyGPT  #####################################################

    def save_decoder(self, decoder):
        "Save the trained decoder to a disk file"       
        torch.save(decoder.state_dict(), self.gpt.path_saved_model["saved_decoder"])

    def save_embedding_generator(self, embedding_generator):
        torch.save(embedding_generator.state_dict(), self.gpt.path_saved_model["saved_embeddings_generator"])

    def save_checkpoint_decoder(self, decoder, dir_name, iter_index):
        "Save the decoder checkpoint"       
        torch.save(decoder.state_dict(), dir_name + "/saved_decoder_" + str(iter_index))

    def save_checkpoint_embedding_generator(self, embedding_generator, dir_name, iter_index):
        "save checkpoint for the embedding_generator"
        torch.save(embedding_generator.state_dict(), dir_name + "/saved_embedding_generator_" + str(iter_index))        


    def run_code_with_buffered_context_for_training_TransformerFG(self, xformer, master_decoder, dataloader, 
                                                           checkpoint_frequency=1000, display_train_loss=False ):
        """
        Drawn from the training routines in the Transformer module of DLStudio
        """
        global training_iter

        def detokenizer( token_sequence_as_string ):
            regex = r'\s_\s'
            out_words = ""
            try:
                out_words = re.split(regex, token_sequence_as_string)
            except TypeError as e:
                print(e)
# >>>>                return [""] * len(token_sequence)
                return [""] * len(token_sequence_as_string)
            ## Join together the space-separated token fragments into complete words, but make sure 
            ## you do NOT cross punctuation marks:
            new_all_words = []
            for word in out_words:
                 frag = word
                 while re.search( r'\w+\s\w+', frag ):
                     frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                 new_all_words.append(frag)
            ## If a word obtained from the previous step include a fragment that terminates in a 
            ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
            cleaned_all_words = []
            for word in new_all_words:
                new_words = []   
                if any(char in string.punctuation for char in word):
                    parts = re.findall(r'[^.?,!]+.?', word)
                    cleaned_all_words += parts
                else:
                    cleaned_all_words.append(word)
            return ' '.join(cleaned_all_words)

        checkpoint_dir =  "checkpoint_dir"
        if os.path.exists(checkpoint_dir):  
            files = glob.glob(checkpoint_dir + "/*")
            for file in files: 
                if os.path.isfile(file): 
                    os.remove(file) 
                else: 
                    files = glob.glob(file + "/*") 
                    list(map(lambda x: os.remove(x), files)) 
        else: 
            os.mkdir(checkpoint_dir)   



        class StreamingLocalLoader(IterableDataset):
            """
            For an IterableDataset, you do not have to define __getitm__ and __len__. Instead, you now define __iter__
            """
            def __init__(self, data_source, batchsize, context_window_size, context_buffer_size, inv_lookup_fn):
                super(StreamingLocalLoader, self).__init__()
                self.data_source = data_source
                self.batchsize = batchsize
                self.context_window_size = context_window_size
                self.context_buffer_size = context_buffer_size
                self.inv_lookup_fn = inv_lookup_fn
                self.prev_iteration_data = np.zeros((batchsize, context_buffer_size), dtype=int)
                self.embedding_generator = embedding_generator
#                global training_iter 

            def __iter__(self):
                ## here we implement the logic the stream the data
#                prev_iteration_data = np.zeros((self.batchsize, self.context_buffer_size), dtype=int)
                new_data_for_new_iteration = self.data_source
                new_prev_iteration_data = new_data_for_new_iteration[:, -self.context_buffer_size:]
                token_sequences_in_batch = [[self.inv_lookup_fn[code] for code in new_data_for_new_iteration[i][1:]] 
                                                                                                  for i in range(self.batchsize)]
                first_tokens_in_batch  =  new_data_for_new_iteration[:,0]
                first_tokens_in_batch = first_tokens_in_batch[...,None]
                data = np.concatenate( (first_tokens_in_batch, self.prev_iteration_data, new_data_for_new_iteration[:,1:]), axis=1 )
                data = torch.from_numpy( data ).to(dev())
                input_tensor = self.embedding_generator( data )
                input_tensor = input_tensor.detach()  ## detach the input_tensor from the computation graph --> Aditya
                self.prev_iteration_data = new_prev_iteration_data                
                yield (input_tensor, data, token_sequences_in_batch)

        class StreamingDataModule(L.LightningDataModule):
            def __init__(self, data_source, context_window_size, batchsize, context_buffer_size, inv_lookup_fn, batch_size=None, num_workers=11):
                super(StreamingDataModule, self).__init__()
                self.context_window_size = context_window_size
                self.context_buffer_size = context_buffer_size
                self.inv_lookup_fn = inv_lookup_fn
                self.data_source = data_source
                ## EXPLAIN the distinction between batchsize and batch_size
                self.batchsize = batchsize
                self.batch_size = batch_size
                self.num_workers = num_workers

            def setup(self, stage=None):
                self.train_dataset = StreamingLocalLoader(self.data_source, self.batchsize, self.context_window_size, self.context_buffer_size, 
                                                                                                                               self.inv_lookup_fn)
            def train_dataloader(self):
                # return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=self.num_workers)
                return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=4) #--> Aditya : Total number of workers will be twice this number for two GPU case. And you need some allowance for addition threads.


#        master_decoder.to(dev())     
        master_decoder
        embedding_generator = self.EmbeddingGenerator(xformer, self.embedding_size)
        criterion = nn.NLLLoss()                                                                                            
        accum_times = []
        start_time = time.perf_counter()
        training_loss_tally = []
        running_loss = 0.0
        batch_size = self.batch_size
        print("")
        debug = False
        training_iter = 0
        predicted_tokens = [[] for i in range(dataloader.batch_size)]

#        prev_seq_logprobs = torch.ones(self.batch_size, xformer.vocab_size, dtype=torch.float).to(dev())
#        master_decoder.prev_seq_logprobs = torch.ones(self.batch_size, xformer.vocab_size, dtype=torch.float).cuda()

        dataloader.initialize_tokenized_data_streams()
        print("\n\nSetting up of the token streams for the batch instances is now complete.") 
        print("\nStarting training iterations. Loss will be shown every 100 iterations. Depending on your hardware, batch size, max sequence length, and transformer config parameters, it may take several minutes for each such display of loss to come through.\n\n") 

        torch.set_float32_matmul_precision('medium')         ## you can also try    torch.set_float32_matmul_precision('high')

        master_decoder.save_checkpoint_decoder = self.save_checkpoint_decoder
        master_decoder.save_checkpoint_embedding_generator = self.save_checkpoint_embedding_generator
        master_decoder.epoch_index = dataloader.epoch_index
        master_decoder.tokenizer = dataloader.tokenizer
        master_decoder.detokenizer = detokenizer

#                self.save_checkpoint_decoder(master_decoder, checkpoint_dir, training_iter+1)
#                self.save_checkpoint_embedding_generator(embedding_generator, checkpoint_dir, training_iter+1)

#        while True:

#            loss_normed = L.Trainer(devices=-1, accelerator="gpu", strategy="ddp", step=1).fit( model=master_decoder,  
#            loss_normed = L.Trainer(devices=-1, accelerator="gpu", strategy="ddp").fit( model=master_decoder,  
#            loss_normed, predicted_indexes, predicted_word_logprobs, token_sequences_in_batch = \
#            L.Trainer(devices=-1, accelerator="gpu", strategy="ddp", max_epochs=-1).fit( model=master_decoder,

        L.Trainer(devices=-1, accelerator="gpu", strategy='ddp_find_unused_parameters_true', max_epochs=-1).fit( model=master_decoder,
                               train_dataloaders=StreamingDataModule(dataloader.dataloader_for_buffered_context(dataloader.context_window_size), 
                                                                     dataloader.batch_size,
                                                                     dataloader.context_window_size, 
                                                                     dataloader.context_buffer_size,
                                                                     dataloader.inverse_lookup) )
#            loss_normed  =  master_decoder.loss_normed
#            predicted_indexes =  master_decoder.predicted_indexes
#            predicted_word_logprobs =   master_decoder.predicted_word_logprobs
#            token_sequences_in_batch =   master_decoder.token_sequences_in_batch
#
#            running_loss += loss_normed
##            prev_seq_logprobs  =  predicted_word_logprobs
#            master_decoder.prev_seq_logprobs =  predicted_word_logprobs
#            if training_iter % 100 == 99:    
#                avg_loss = running_loss / float(100)
#                training_loss_tally.append(avg_loss)
#                FILE_for_training_loss.write("%s\n" % str(avg_loss))
#                running_loss = 0.0
#                current_time = time.perf_counter()
#                time_elapsed = current_time-start_time
#                print("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs]     loss: %.4f\n\n" % (dataloader.epoch_index + 1, training_iter+1,time_elapsed,avg_loss)) 
#                FILE_for_training_results.write("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs]     loss: %.4f\n\n\n" % (dataloader.epoch_index, training_iter+1,time_elapsed,avg_loss)) 
#                for j in range(dataloader.batch_size):
##>>>>                    predicted_tokens[j] = dataloader.tokenizer.decode( predicted_indexes[j], skip_special_tokens=True )
#                    predicted_tokens[j] = dataloader.tokenizer.decode( predicted_indexes[j], skip_special_tokens=True )
#                for i in random.sample( range(dataloader.batch_size), 4 ): 
##>>>>                    print("Ground-Truth: ", detokenizer( ' '.join(token_sequences_in_batch[i]) ))
#                    print("Ground-Truth: ", detokenizer( ' '.join(token_sequences_in_batch[i]) ))
#                    print("GT Token Seq: ", ' '.join(token_sequences_in_batch[i] ))
#                    print("   Predicted: ", predicted_tokens[i])
#                    print(" Detokenized: ", detokenizer( dataloader.tokenizer.decode( predicted_indexes[i], skip_special_tokens=True ) ))
#                    print()
#                    FILE_for_training_results.write("ground-truth: %s\n" % str(detokenizer( ' '.join(token_sequences_in_batch[i]) )))
#                    FILE_for_training_results.write("GT Token Seq: %s\n" % str(' '.join(token_sequences_in_batch[i]) ))
#                    FILE_for_training_results.write("   predicted: %s\n" % str(predicted_tokens[i]))
#                    FILE_for_training_results.write(" detokenized: %s\n" % str(detokenizer( dataloader.tokenizer.decode(predicted_indexes[i],skip_special_tokens=True))))
#                    FILE_for_training_results.write("\n")
#                accum_times.append(current_time-start_time)
#                FILE_for_training_results.flush()
#                FILE_for_training_loss.flush()
#
#            if training_iter % checkpoint_frequency == checkpoint_frequency-1:    
#                print("\n\nSaving checkpoint at iteration: %d\n\n"% (training_iter+1))
#                self.save_checkpoint_decoder(master_decoder, checkpoint_dir, training_iter+1)
#                self.save_checkpoint_embedding_generator(embedding_generator, checkpoint_dir, training_iter+1)
#

    ###%%%
    #######################################################################################################################
    ###########################################  PromptResponder for babyGPT  #############################################

    class PromptResponder(nn.Module):
        """
        Prompting a trained babyGPT models means that you supply a small number of words (as, say, the 
        beginning of a new thought) as a prompt and the model supplies the rest of the words to complete 
        the thought.  The class comes with two methods, the first for extending your prompt until it 
        reaches a period, and the second for going beyond the first period encountered.
    
        Any interaction with a trained GPT model has to deal with the following issue:  What to do with
        the context buffer that is meant to be a continuation of the last part of the previous "sentence"
        fed into the transformer. 
    
        Ideally, we should be placing in the context buffer words that create a context for the prompt.
        But there is no easy way to that without a more elaborate model. An example of more elaborate
        modeling would be to have the input to the transformer consist of, say, an SOS token, a special
        context token consisting possibly of integer index values beyond the tokenizer vocab, followed
        by a context buffer that would be the last part of the previous sentence, followed, finally, 
        by the new input tokens.
    
        babyGPT gives you two options regarding what to do with the context buffer for your prompt:
    
                --  all_zeros
    
                --  get_from_prompt
    
        With the first option, all of the integer encoding values in the context buffer are set to
        the integer zero.  And, with the second option, at this time, the context buffer contains
        a portion or all of the prompt itself.  If the tokenized version of the prompt is shorter
        than the size of the context buffer, only the context_buffer_size number of elements of the
        prompt are retained for the context buffer.  In the opposite case, just the initial 
        context_buffer_size number of elements of the prompt are retained.
        """
        def __init__(self, gpt,  xformer, master_decoder, context_window_size, context_buffer_size, tokenizer_json, checkpoint_dir, checkpoint_index):
            super(babyGPT.PromptResponder, self).__init__()
            self.gpt  =  gpt
            self.xformer = xformer
            self.master_decoder = master_decoder
            self.context_window_size = context_window_size
            self.context_buffer_size = context_buffer_size
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.vocab_size = self.tokenizer.vocab_size
            self.checkpoint_dir = checkpoint_dir
            self.checkpoint_index = checkpoint_index


        def generate_response_to_prompt_up_to_period(self, context_buffer_option=None, result_file=None):
            """
            This version tries to construct a more elaborate response to a single prompt by going beyond the first period that 
            is encountered.  The first part of the if-else block shown below is for extending the prompt to the first period.
            On the other hand, the else clause is for generating additional sentences beyond the first period.  I have yet to
            clean up the logic for that.
            """

            def detokenizer( token_sequence_as_string ):
                regex = r'\s_\s'
                out_words = ""
                try:
                    out_words = re.split(regex, token_sequence_as_string)
                except TypeError as e:
                    print(e)
                    return [""] * len(token_sequence_as_string)
                ## Join together the space-separated token fragments into complete words, but make sure 
                ## you do NOT cross punctuation marks:
                new_all_words = []
                for word in out_words:
                     frag = word
                     while re.search( r'\w+\s\w+', frag ):
                         frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                     new_all_words.append(frag)
                ## If a word obtained from the previous step include a fragment that terminates in a 
                ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
                cleaned_all_words = []
                for word in new_all_words:
                    new_words = []   
                    if any(char in string.punctuation for char in word):
                        parts = re.findall(r'[^.?,!]+.?', word)
                        cleaned_all_words += parts
                    else:
                        cleaned_all_words.append(word)
                return ' '.join(cleaned_all_words)
    

            if result_file is not None:
                FILE = open(result_file, 'w')

            master_decoder = self.master_decoder
            master_decoder.load_state_dict(torch.load(self.checkpoint_dir + "/" + 
                                                        self.gpt.path_saved_model['decoder'] +  '_' + str(self.checkpoint_index) ))
            master_decoder.to( dev() )     
            embedding_generator = self.gpt.EmbeddingGenerator(self.xformer, self.gpt.embedding_size).to( dev() )
            embedding_generator.load_state_dict(torch.load(self.checkpoint_dir + "/" +
                                                   self.gpt.path_saved_model['embedding_generator'] + '_' + str(self.checkpoint_index)))
            embedding_generator.to( dev() )
            debug = False
            prompt = ""
            with torch.no_grad():
                while True:
                    context_buffer = np.zeros(shape=(self.context_buffer_size), dtype=int)
                    while True:
                        prompt = input("\nEnter your prompt: ")
                        if prompt == "": continue
                        else: break
                    ##  Strip any empty space before or after the prompt:
                    prompt = prompt.strip()
                    print("\nyour prompt: ", prompt)
                    all_words = prompt.split()
                    all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words]
                    prompt_text = ' '.join(all_words)
                    print("\nprompt_text_with_underscores: ", prompt_text)
                    ## consists of int tokens for the symbolic token in prompt:
                    encoded_prompt = self.tokenizer.encode( prompt_text )
                    token_sequence_in_prompt = [self.inverse_lookup[int_code] for int_code in encoded_prompt]
                    print("\ntoken_sequence_in_prompt: ", token_sequence_in_prompt)
                    print("\nencoded_prompt: ", encoded_prompt)
                    predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                    stopping_token_code = 46
                    while predicted_word_index_value.item() != stopping_token_code:
                        if len(encoded_prompt) >=  self.context_window_size: 
                            break
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,0] = 89         ##  The SOS token             
                        if context_buffer_option == "all_zeros":
#                            print("\n\n======================== Choosing all-zeros option for context initialization")
                            input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        elif context_buffer_option == "get_from_prompt": 
#                            print("\n\n======================== Choosing 'get from prompt' option for context initialization")
                            if len(encoded_prompt) > self.context_buffer_size:
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(encoded_prompt[:self.context_buffer_size])
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)    
                            else:
                                ## if prompt is too short:
                                padded_encoded_prompt =  encoded_prompt +  [0] * (self.context_buffer_size - len(encoded_prompt))
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(padded_encoded_prompt)
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        input_tensor = input_tensor.to( dev() )
                        input_tensor = embedding_generator( input_tensor )
                        mask = torch.ones( self.context_buffer_size + len(encoded_prompt), dtype=int)
                        predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                        predicted_word_logprobs, predicted_word_index_value = master_decoder(input_tensor, mask)                     
                        predicted_token =  self.xformer.inverse_lookup[predicted_word_index_value.cpu().numpy()[0]]
                        encoded_prompt.append(predicted_word_index_value.item())
                        if debug: 
                            print("\npredicted token: ", predicted_token)                
                            print("\nencoded_prompt: ", encoded_prompt)                
                    if debug:
                        print("\n\nprompt and its response: ", encoded_prompt)
                    output_string = ""
                    for code in encoded_prompt:
                        output_string += " " + self.xformer.inverse_lookup[code]
                    print("\nencoding of prompt and the response: ", encoded_prompt)
                    print("\nprompt and its response: ", output_string)
                    final_output = detokenizer(output_string) 
                    ## find() returns -1 when no char is "."
                    index_period  =  final_output.find(".")
                    if index_period >= 0 and index_period < len(final_output):
                        print("\ndetokenized sentence completion: ", final_output[:final_output.find(".")+1])
                    else:
                        print("\ndetokenized sentence completion: ", final_output)


        def generate_response_to_prompt_beyond_period(self, context_buffer_option=None, result_file=None):
            """
            This version tries to construct a more elaborate response to a single prompt by going beyond the first period that 
            is encountered.  The first part of the if-else block shown below is for extending the prompt to the first period.
            On the other hand, the else clause is for generating additional sentences beyond the first period.  I have yet to
            clean up the logic for that.xs
            """
            def detokenizer( token_sequence_as_string ):
                regex = r'\s_\s'
                out_words = ""
                try:
                    out_words = re.split(regex, token_sequence_as_string)
                except TypeError as e:
                    print(e)
                    return [""] * len(token_sequence_as_string)
                ## Join together the space-separated token fragments into complete words, but make sure 
                ## you do NOT cross punctuation marks:
                new_all_words = []
                for word in out_words:
                     frag = word
                     while re.search( r'\w+\s\w+', frag ):
                         frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                     new_all_words.append(frag)
                ## If a word obtained from the previous step include a fragment that terminates in a 
                ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
                cleaned_all_words = []
                for word in new_all_words:
                    new_words = []   
                    if any(char in string.punctuation for char in word):
                        parts = re.findall(r'[^.?,!]+.?', word)
                        cleaned_all_words += parts
                    else:
                        cleaned_all_words.append(word)
                return ' '.join(cleaned_all_words)

            if result_file is not None:
                FILE = open(result_file, 'w')
            master_decoder = self.master_decoder
            master_decoder.load_state_dict(torch.load(self.checkpoint_dir + "/" + 
                                                        self.gpt.path_saved_model['decoder'] +  '_' + str(self.checkpoint_index) ))
            master_decoder.to( dev() )     
            embedding_generator = self.gpt.EmbeddingGenerator(self.xformer, self.gpt.embedding_size).to( dev() )
            embedding_generator.load_state_dict(torch.load(self.checkpoint_dir + "/" +
                                                   self.gpt.path_saved_model['embedding_generator'] + '_' + str(self.checkpoint_index)))
            embedding_generator.to( dev() )
            debug = False
            with torch.no_grad():
                interaction_index = 0
                overall_response = ""
                while True:
                    if interaction_index == 0:                                                                              ## (A)

                        context_buffer = np.zeros(shape=(self.context_buffer_size), dtype=int)
                        prompt = input("\n\nEnter your prompt: ")
                        ##  Strip any empty space before or after the prompt:
                        prompt = prompt.strip()
                        print("\n\nyour prompt: ", prompt)
                        all_words = prompt.split()
                        all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words]
                        prompt_text = ' '.join(all_words)
                        print("\n\nprompt_text_with_underscores: ", prompt_text)
                        ## consists of int tokens for the symbolic token in prompt:
                        encoded_prompt = self.tokenizer.encode( prompt_text )
                        token_sequence_in_prompt = [self.inverse_lookup[int_code] for int_code in encoded_prompt]
                        print("\n\ntoken_sequence_in_prompt: ", token_sequence_in_prompt)
                        print("\n\nencoded_prompt: ", encoded_prompt)
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,0] = 89         ##  The SOS token             
                        if context_buffer_option == "all_zeros":
                            input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        elif context_buffer_option == "get_from_prompt": 
                            if len(encoded_prompt) > self.context_buffer_size:
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(encoded_prompt[:self.context_buffer_size])
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)    
                            else:
                                ## if prompt is too short:
                                padded_encoded_prompt =  encoded_prompt +  [0] * (self.context_buffer_size - len(encoded_prompt))
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(padded_encoded_prompt)
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)

                    else:                                                                                                   ## (B)
                        print("\n\n\n[Interaction no. %d]  encoded prompt from PREV ITER: " % (interaction_index+1), encoded_prompt) 
                        context_buffer =  encoded_prompt[-self.context_buffer_size - self.context_buffer_size:-self.context_buffer_size]
                        encoded_prompt = encoded_prompt[-self.context_buffer_size:]
                        print("[Interaction no. %d]  context_buffer: " % (interaction_index+1), context_buffer)
                        print("[Interaction no. %d]  encoded prompt: " % (interaction_index+1), encoded_prompt) 
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,:self.context_buffer_size] = torch.tensor( context_buffer )
                        input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                    interaction_index += 1               
                    if interaction_index >= 3: 
                        print("\n\nInteraction limit reached")
                        break
                    input_tensor = input_tensor.to( dev() )
                    input_tensor = embedding_generator( input_tensor )
                    mask = torch.ones( self.context_buffer_size + len(encoded_prompt), dtype=int)
                    stopping_token_code = 16
                    predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                    while predicted_word_index_value.item() != stopping_token_code:
                        if len(encoded_prompt) >=  self.context_window_size: 
                            break
                        predicted_word_logprobs, predicted_word_index_value = master_decoder(input_tensor, mask)                 
                        predicted_token =  self.xformer.inverse_lookup[predicted_word_index_value.cpu().numpy()[0]]
                        encoded_prompt.append(predicted_word_index_value.item())
                        if debug: 
                            print("\npredicted token: ", predicted_token)                
                            print("\nencoded_prompt: ", encoded_prompt)                
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        input_tensor = input_tensor.to( dev() )
                        input_tensor = embedding_generator( input_tensor )
                        mask = torch.cat( ( mask, torch.ones(1, dtype=int) ) )                                          
                    if debug:
                        print("\n\nprompt and its response: ", encoded_prompt)
                    output_string = ""
                    for code in encoded_prompt:
                        output_string += " " + self.xformer.inverse_lookup[code]
                    print("\n\nprompt and its response: ", output_string)
                    print("\n\ndetokenized sentence completion: ", detokenizer(output_string))

                    overall_response += output_string

            print("\n\nOverall response to your prompt: ", overall_response)
            print("\n\nOverall detokenized response: ", detokenizer(overall_response))


    ###%%%
    ###########################  ScheduledOptim Code for TransformerFG #############################

    class ScheduledOptimXXXXXXXXXXXXXXXXXXXXXXXXXXXXX():
        """
        As in the Transformers module of DLStudio, for the scheduling of the learning rate
        during the warm-up phase of training TransformerFG, I have borrowed the class shown below
        from the GitHub code made available by Yu-Hsiang Huang at:

                https://github.com/jadore801120/attention-is-all-you-need-pytorch
        """
        def __init__(self, optimizer, lr_mul, d_model, n_warmup_steps):
            self._optimizer = optimizer
            self.lr_mul = lr_mul
            self.d_model = d_model
            self.n_warmup_steps = n_warmup_steps
            self.n_steps = 0

        def step_and_update_lr(self):
            "Step with the inner optimizer"
            self._update_learning_rate()
            self._optimizer.step()
    
        def zero_grad(self):
            "Zero out the gradients with the inner optimizer"
            self._optimizer.zero_grad()
    
        def _get_lr_scale(self):
            d_model = self.d_model
            n_steps, n_warmup_steps = self.n_steps, self.n_warmup_steps
            return (d_model ** -0.5) * min(n_steps ** (-0.5), n_steps * n_warmup_steps ** (-1.5))
    
        def _update_learning_rate(self):
            ''' Learning rate scheduling per step '''
            self.n_steps += 1
            lr = self.lr_mul * self._get_lr_scale()
            for param_group in self._optimizer.param_groups:
                param_group['lr'] = lr

#############################################################################################################################
##############################################   End of babyGPT Class Definition#############################################

if __name__ == '__main__': 
    pass

