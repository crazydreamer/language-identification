language-identification
=======================

The Tatoeba corpus is a large, open source collection of short sentences and their translations in different languages. Due to the open source nature of the work, sentences are sometimes filed under the wrong language which is obviously undesirable. This project aims to present candidates of incorrect sentence translations of the corpus to the user. The most common form of language identification is the n-gram method which is not optimal for short sentences, such as the ones in the corpus, so this project will instead use an extended dictionary method as described by Řehůřek and Kolkus (2009).


Usage:

1. Download the latest copy of the Tatoeba corpus, found at http://downloads.tatoeba.org/exports/sentences.tar.bz2. Extract and save sentences.csv in the same folder as the language analyzer script.

2. Run the script. # python languageanalyzer.py. It may be worthwhile piping the output to a file



Understanding the output:

The output is written in order of most likely to least likely sentences to be translated incorrectly.