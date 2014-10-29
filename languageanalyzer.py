# Todo: Fix punctuation in words (e.g I've), either by adding these to the word files (ive) or by adding extra code to translate from contraction to separate words

import string
import math
import operator

def getlang(sentence, data, allwords):
	wordsinsentence = sentence.count(" ") + 1
	bestrelevance = - 10000 # wordsinsentence * 5.0
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
			#print abr + ':' + word + ':' + str(wordinlangfreq) + ':' + str(wordincorpusfreq)
		#print abr + str(relevance)
		if bestrelevance < relevance:
			bestrelevance = relevance
			bestlang = abr
		relevanceCollection[abr] = relevance
	relevanceCollection = sorted(relevanceCollection.items(), key=operator.itemgetter(1), reverse=True)
	if (bestrelevance < 0.0 or (relevanceCollection[0][1] * 0.9) <= relevanceCollection[1][1]):
		bestlang = 'unknown'
	return [bestlang,bestrelevance,relevanceCollection]

langabbreviations = ['ara','bul','bos','ces','dan','deu','ell','eng','spa','est','fin','fra','heb','hrv','hun','isl','ita','lit','lav','mkd','msa','nob','nld','pol','por','ron','rus','slk','slv','sqi','srp','swe','tur','ukr','zho']
# langabbreviations = ['dan','deu','ell','eng','fra','ita','rus','spa']
data = {}
allwords = {}

totalnumwords = 0
MAX_WORDS_PER_LANGUAGE = 50000

# Calculate the total number of words in each language's frequency list
for abr in langabbreviations:
	data[abr] = {}
	data[abr]['numwords'] = 0
	filename = abr + '.txt'
	f = open(filename, 'r')
	numwords = 0
	for line in f:
		data[abr]['numwords'] += int(line.split()[1])
		numwords += 1
		if numwords > MAX_WORDS_PER_LANGUAGE: break
	totalnumwords += data[abr]['numwords']
print 'Loaded number of words'

# Calculate each word's uncorrected observed frequency
for abr in langabbreviations:
	data[abr]['words'] = {}
	filename = abr + '.txt'
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
		#print word + ':' + str(data[abr]['words'][word])
print 'Calculated all word\'s uncorrected observed frequency'

# Turn the total word frequencies into a weighted frequency
for word in allwords:
	count = allwords[word]
	allwords[word] = float(count) / totalnumwords
	#print word + ':' + str(data['total']['words'][word])

	
# sentence = 'Mi aerodeslizador esta lleno de anguilas.'
# sentence = 'Voy a mi casa.'
# sentence = 'How could you say such a thing to my teacher, who does not nothing of such matters'

numcorrect = 0
numincorrect = 0
numunknown = 0
f = open('sentences.csv', 'r', 1)
for line in f:
	id = line.split("\t")[0]
	reallang = line.split("\t")[1]
	
	# Only check languages that we have a model for
	if reallang not in langabbreviations:
		continue
	sentence = line.split("\t")[2]
	l = getlang(sentence, data, allwords)
	estlang = l[0]
	estrelevance = l[1]
	if estlang == 'unknown':
		numunknown += 1
		#print '*',
	elif reallang == estlang:
		numcorrect += 1
	elif reallang != estlang:
		numincorrect += 1
		print '***' + reallang + ':' + estlang + ':' + str(estrelevance) + ':' + sentence,
	#print reallang + ':' + estlang + ':' + str(estrelevance) + ':' + sentence,
	if (numcorrect + numincorrect + numunknown) % 10000 == 0:
		print str(numcorrect) + ' correct, ' + str(numincorrect) + ' incorrect, ' + str(numunknown) + ' unknown'

print str(numcorrect) + ' correct, ' + str(numincorrect) + ' incorrect, ' + str(numunknown) + ' unknown'
