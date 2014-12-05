language-identification
=======================

The Tatoeba corpus is a large, open source collection of short sentences and their translations in different languages. Due to the open source nature of the work, sentences are sometimes undesirably filed under the wrong language. This project aims to present candidates of incorrect sentence translations of the corpus to the user. The most common form of language identification, the n-gram method, is not optimal for short sentences such as the ones in the Tatoeba corpus, so this project instead uses an extended dictionary method as described by Řehůřek and Kolkus (2009).

Requirements:

	Python 2.7
	docopt plugin


Usage:

1. Download the latest copy of the Tatoeba corpus, found at http://downloads.tatoeba.org/exports/sentences.tar.bz2. Extract and save sentences.csv in the same folder as the language analyzer script.

2. Run the script.

	languageanalyzer.py [-vqh] INPUTFILE OUTPUTFILE

	Process FILE and optionally apply correction to either left-hand side or
	right-hand side.

	Arguments:
	  INPUTFILE     file containing tatoeba sentence list
	  OUTPUTFILE    name for the report file

	Options:
	  -h --help
	  -v       verbose mode
	  -q       quiet mode


Understanding the output:

	The output is written in order of most likely to least likely sentences to be translated incorrectly.