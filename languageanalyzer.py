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


import string
import math
import operator
import getopt
import sys

# Get a list containing the languages and associated probabilities that the 
# sentence is believed to be
def getlang(sentence, data, allwords):
	bestrelevance = - 10000
	bestlang = 'unknown'
	relevanceCollection = {}
	for abr in langabbreviations:
		sentence = sentence.lower()
		sentence = sentence.translate(string.maketrans("",""), string.punctuation)
		sentencelist = sentence.split()
		relevance = 0
		for word in sentencelist:
			wordinlangfreq = float(0.000000000001)
			wordincorpusfreq = float(0.000000000001)
			if word in data[abr]['words']:
				wordinlangfreq = float(data[abr]['words'][word])
			if word in allwords:
				wordincorpusfreq = float(allwords[word])
			relevance += math.log(wordinlangfreq)
			relevance -= math.log(wordincorpusfreq)
		if bestrelevance < relevance:
			bestrelevance = relevance
			bestlang = abr
		relevanceCollection[abr] = relevance
	relevanceCollection = sorted(relevanceCollection.items(), key=operator.itemgetter(1), reverse=True)
	if (bestrelevance < 0.0 or (relevanceCollection[0][1] * 0.9) <= relevanceCollection[1][1]):
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

	# Check the input
	if (len(sys.argv) != 3):
		print "Usage: python languageanalyzer.py <inputfile> <outputfile>"
		exit(1)
	inputfile = sys.argv[1]
	outputfile = sys.argv[2]

	# Calculate the total number of words in each language's frequency list
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

	# Calculate each word's uncorrected observed frequency
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

	# Turn the total word frequencies into a weighted frequency
	for word in allwords:
		count = allwords[word]
		allwords[word] = float(count) / totalnumwords

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
			badsentences.append([sentence, difference, reallang, estlang, estrelevance, id])
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

if __name__ == "__main__":
    main(sys.argv)