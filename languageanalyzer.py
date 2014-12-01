 #!/usr/bin/python
 # coding: latin-1

# The Tatoeba corpus is a large, open source collection of short sentences and 
# their translations in different languages. Due to the open source nature of 
# the work, sentences are sometimes filed under the wrong language which is 
# obviously undesirable. This project aims to present candidates of incorrect 
# sentence translations of the corpus to the user. The most common form of 
# language identification is the n-gram method which is not optimal for short
# sentences, such as the ones in the corpus, so this project will instead use
# an extended dictionary method as described by Řehůřek and Kolkus (2009).
# 
# Usage:
# 
# Download the latest copy of the Tatoeba corpus, found at 
# http://downloads.tatoeba.org/exports/sentences.tar.bz2. Extract and save 
# sentences.csv in the same folder as the language analyzer script.
# 
# Run the script. 
# 	python languageanalyzer.py sentences.csv output.txt
# 
# Understanding the output:
# 
# The output is written in order of most likely to least likely sentences to
# be translated incorrectly.
 
 # Wordlists from http://invokeit.wordpress.com/frequency-word-lists/

 
"""Usage: languageanalyzer.py [-vqh] INPUTFILE OUTPUTFILE

Process FILE and optionally apply correction to either left-hand side or
right-hand side.

Arguments:
  INPUTFILE     file containing tatoeba sentence list
  OUTPUTFILE    name for the report file

Options:
  -h --help
  -v       verbose mode
  -q       quiet mode

"""
from docopt import docopt

import string
import math
import operator
import getopt
import sys



quiet = False
verbose = False


# Wrapper for writing output to the screen
def printToConsole(string):
	if (quiet == False):
		sys.stdout.write(string)


# Get a list containing the languages and associated probabilities that the 
# sentence is believed to be
def getlang(sentence, data, allwords):
	bestrelevance = 0
	bestlang = 'unknown'
	relevanceCollection = {}
	
	sentence = sentence.lower()
	sentence = sentence.translate(string.maketrans("",""), string.punctuation)
	sentencelist = sentence.split()
	
	# Sentences with 1 or 2 words are too unwieldy and show too many false positives
	if (len(sentencelist) < 3):
		return ['unknown', 0.0, 0.0, []]
	
	for abr in langabbreviations:
		# Formula (6) from Řehůřek and Kolkus (2009)
		# Word relevance = SUM(gL(wi) << glang(wi)) fi · rel(wi, lang)
		# Where rel(w, lang) = log(glang(w)) − log(g0(w))
		
		relevance = 0
		for word in sentencelist:
			wordinlangfreq = float(0.000000000001)
			wordincorpusfreq = float(0.000000000001)
			if word in data[abr]['words']:
				wordinlangfreq = float(data[abr]['words'][word])
			if word in allwords:
				wordincorpusfreq = float(allwords[word])
			relevance += math.log(wordinlangfreq) - math.log(wordincorpusfreq)
		
		# Formula (7)
		# (SUM(gL(wi) << glang(wi)) fi · rel(wi, lang)) / SUM(fi)
		relevance = relevance / len(sentencelist)
		
		if bestrelevance < relevance:
			bestrelevance = relevance
			bestlang = abr
		
		relevanceCollection[abr] = relevance
	relevanceCollection = sorted(relevanceCollection.items(), key=operator.itemgetter(1), reverse=True)
	if (bestrelevance < 0.0 or (relevanceCollection[0][1] - relevanceCollection[1][1] <= 0.4)):
		bestlang = 'unknown'
	difference = relevanceCollection[0][1] - relevanceCollection[1][1]
	return [bestlang,bestrelevance,difference,relevanceCollection]

langabbreviations = ['ara','bul','bos','ces','dan','deu','ell','eng','spa',
					 'est','fin','fra','heb','hrv','hun','isl','ita','lit',
					 'lav','msa','nob','nld','pol','por','ron','rus','slk',
					 'slv','sqi','swe','tur','ukr','zho']
codetolang = {'ara' : 'arabic','bul' : 'bulgarian','bos' : 'bosnian',
			  'ces' : 'czech','dan' : 'danish','deu' : 'german',
			  'ell' : 'greek','eng' : 'english','spa' : 'spanish',
			  'est' : 'estonian','fin' : 'finnish','fra' : 'french',
			  'heb' : 'hebrew','hrv' : 'croatian','hun' : 'hungarian',
			  'isl' : 'icelandic','ita' : 'italian','lit' : 'lithuanian',
			  'lav' : 'latvian','mkd' : 'macedonian','msa' : 'malay',
			  'nob' : 'norwegian','nld' : 'dutch','pol' : 'polish',
			  'por' : 'portuguese','ron' : 'romanian','rus' : 'russian',
			  'slk' : 'slovak','slv' : 'slovenian','sqi' : 'albanian',
			  'srp' : 'serbian','swe' : 'swedish','tur' : 'turkish',
			  'ukr' : 'ukrainian','zho' : 'chinese'}
			  
			  
def main(argv):
	data = {}
	allwords = {}

	totalnumwords = 0
	MAX_WORDS_PER_LANGUAGE = 50000

	global quiet
	global verbose
	
	arguments = docopt(__doc__)
	inputfile = arguments['INPUTFILE']
	outputfile = arguments['OUTPUTFILE']
	quiet = arguments['-q']
	verbose = arguments['-v']
	
	# Calculate the total number of words in each language's frequency list
	# We don't pre-calculate these, as we can change the number of words used
	# from the dictionary to a number higher than some dictionaries have words
	numfilesdone = 0
	printToConsole("Calculating dictionary sizes [%-20s] %d%%" % ('='*(0/5), 0))
	for abr in langabbreviations:
		data[abr] = {}
		data[abr]['numwords'] = 0
		filename = 'dict/' + abr + '.txt'
		f = open(filename, 'r')
		numwords = 0
		for line in f:
			data[abr]['numwords'] += int(line.split()[1])
			numwords += 1
			if numwords > MAX_WORDS_PER_LANGUAGE: break
		totalnumwords += data[abr]['numwords']
		f.close()
		numfilesdone += 1
		progress = float(numfilesdone) / float(len(langabbreviations)) * 100.0
		progress = int(progress)
		printToConsole("\rCalculating dictionary sizes [%-20s] %d%%" % ('='*(progress/5), progress))
	printToConsole('\n')

	# Calculate each word's uncorrected observed frequency
	# Formula (1): g[lang](w) = TF(w, C[lang]) / #(C[lang])
	# with #(C) being the total number of words in corpus C
	# and TF the number of occurences of a word in a corpus
	# and g[0](w) = TF(w, C[0]) / #(C[0])
	numfilesdone = 0
	printToConsole("Calculating word frequencies [%-20s] %d%%" % ('='*(0/5), 0))
	for abr in langabbreviations:
		data[abr]['words'] = {}
		filename = 'dict/' + abr + '.txt'
		f = open(filename, 'r')
		numwords = 0
		for line in f:
			word = line.split()[0]
			data[abr]['words'][word] = float(line.split()[1]) / data[abr]['numwords']
			if word in allwords:
				allwords[word] += int(line.split()[1])
			else:
				allwords[word] = int(line.split()[1])
			numwords += 1
			if numwords > MAX_WORDS_PER_LANGUAGE: break
		f.close()
		numfilesdone += 1
		progress = float(numfilesdone) / float(len(langabbreviations)) * 100.0
		progress = int(progress)
		printToConsole("\rCalculating word frequencies [%-20s] %d%%" % ('='*(progress/5), progress))
	printToConsole('\n')

	# Turn the total word frequencies into a weighted frequency
	for word in allwords:
		count = allwords[word]
		allwords[word] = float(count) / totalnumwords

	numlinesdone = 0
	printToConsole("Checking sentences [%-20s] %d%%" % ('='*(0/5), 0))
	badsentences = []
	numcorrect = 0
	numincorrect = 0
	numunknown = 0
	num_lines = sum(1 for line in open(inputfile))
	f = open(inputfile, 'r', 1)
	for line in f:
		id = line.split("\t")[0]
		reallang = line.split("\t")[1]
		
		# Only check languages that we have a model for
		if reallang not in langabbreviations:
			continue
		sentence = line.split("\t")[2].rstrip()
		l = getlang(sentence, data, allwords)
		estlang = l[0]
		estrelevance = l[1]
		difference = l[2]
		if estlang == 'unknown':
			numunknown += 1
		elif reallang == estlang:
			numcorrect += 1
		elif reallang != estlang:
			numincorrect += 1
			badsentences.append([sentence, difference, reallang, estlang, estrelevance, id, l[3]])

		numlinesdone += 1
		if (numlinesdone % 1000 == 0):
			progress = float(numlinesdone) / float(num_lines) * 100.0
			progress = int(progress)
			printToConsole("\rChecking sentences [%-20s] %d%%" % ('='*(progress/5), progress))
	printToConsole("\rChecking sentences [%-20s] %d%%\n" % ('='*(100/5), 100))
	f.close()

	outf = open(outputfile, 'w')
	outf.write(str(numcorrect) + ' correct, ' + str(numincorrect) + ' incorrect, ' + str(numunknown) + ' unknown\n')
	outf.write('\n')
	badsentences.sort(key=lambda tup: tup[1], reverse=True)
	for b in badsentences:
		outf.write(b[0] + '\n')
		outf.write("\tCurrent Language: " + codetolang[b[2]] + '\n')
		outf.write("\tSuggested Language: " + codetolang[b[3]] + '\n')
		outf.write("\tURL: http://tatoeba.org/eng/sentences/show/" + b[5] + '\n\n')
		if (verbose):
			for pair in b[6]:
				outf.write("\t" + codetolang[pair[0]].ljust(15) + " " + str(pair[1]) + '\n')
			outf.write("\n")

if __name__ == "__main__":
    main(sys.argv)