import string
import math
import operator

def getlang(sentence, data, allwords):
	wordsinsentence = sentence.count(" ") + 1
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

langabbreviations = ['ara','bul','bos','ces','dan','deu','ell','eng','spa','est','fin','fra','heb','hrv','hun','isl','ita','lit','lav','mkd','msa','nob','nld','pol','por','ron','rus','slk','slv','sqi','srp','swe','tur','ukr','zho']
codetolang = {'ara' : 'arabic','bul' : 'bulgarian','bos' : 'bosnian','ces' : 'czech','dan' : 'danish','deu' : 'german','ell' : 'greek','eng' : 'english','spa' : 'spanish','est' : 'estonian','fin' : 'finnish','fra' : 'french','heb' : 'hebrew','hrv' : 'croatian','hun' : 'hungarian','isl' : 'icelandic','ita' : 'italian','lit' : 'lithuanian','lav' : 'latvian','mkd' : 'macedonian','msa' : 'malay','nob' : 'norwegian','nld' : 'dutch','pol' : 'polish','por' : 'portuguese','ron' : 'romanian','rus' : 'russian','slk' : 'slovak','slv' : 'slovenian','sqi' : 'albanian','srp' : 'serbian','swe' : 'swedish','tur' : 'turkish','ukr' : 'ukrainian','zho' : 'chinese'}
data = {}
allwords = {}

totalnumwords = 0
MAX_WORDS_PER_LANGUAGE = 50000

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

# Turn the total word frequencies into a weighted frequency
for word in allwords:
	count = allwords[word]
	allwords[word] = float(count) / totalnumwords

badsentences = []
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

print str(numcorrect) + ' correct, ' + str(numincorrect) + ' incorrect, ' + str(numunknown) + ' unknown'
print ''
badsentences.sort(key=lambda tup: tup[1], reverse=True)
for b in badsentences:
	print b[0]
	print "\tCurrent Language: " + codetolang[b[2]]
	print "\tSuggested Language: " + codetolang[b[3]]
	print "\tURL: http://tatoeba.org/eng/sentences/show/" + b[5] + "\n"
exit()
