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
#     python languageanalyzer.py sentences.csv output.txt
#
# Understanding the output:
#
# The output is written in order of most likely to least likely sentences to
# be translated incorrectly.

# Wordlists from http://invokeit.wordpress.com/frequency-word-lists/ under
# CC-BY-SA, adjusted to remove common names


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
import sys


QUIET = False
VERBOSE = False
MAX_WORDS_PER_LANGUAGE = 50000

LANGABBREVIATIONS = ['ara', 'bul', 'bos', 'ces', 'dan', 'deu', 'ell', 'eng',
                     'spa', 'est', 'fin', 'fra', 'heb', 'hrv', 'hun', 'isl',
                     'ita', 'lit', 'lav', 'msa', 'nob', 'nld', 'pol', 'por',
                     'ron', 'rus', 'slk', 'slv', 'sqi', 'swe', 'tur', 'ukr',
                     'zho']
CODETOLANG = {'ara' : 'arabic', 'bul' : 'bulgarian', 'bos' : 'bosnian',
              'ces' : 'czech', 'dan' : 'danish', 'deu' : 'german',
              'ell' : 'greek', 'eng' : 'english', 'spa' : 'spanish',
              'est' : 'estonian', 'fin' : 'finnish', 'fra' : 'french',
              'heb' : 'hebrew', 'hrv' : 'croatian', 'hun' : 'hungarian',
              'isl' : 'icelandic', 'ita' : 'italian', 'lit' : 'lithuanian',
              'lav' : 'latvian', 'mkd' : 'macedonian', 'msa' : 'malay',
              'nob' : 'norwegian', 'nld' : 'dutch', 'pol' : 'polish',
              'por' : 'portuguese', 'ron' : 'romanian', 'rus' : 'russian',
              'slk' : 'slovak', 'slv' : 'slovenian', 'sqi' : 'albanian',
              'srp' : 'serbian', 'swe' : 'swedish', 'tur' : 'turkish',
              'ukr' : 'ukrainian', 'zho' : 'chinese'}

def print_to_console(msg):
    """Wrapper for writing output to the screen."""

    if not QUIET:
        sys.stdout.write(msg)

def get_number_of_words(number_of_words):
    """Calculate the total number of words in each language's frequency list.
    We don't pre-calculate these, as we can change the number of words used
    from the dictionary to a number higher than some dictionaries have words."""

    total_num_words = 0
    num_files_done = 0
    print_to_console("Calculating dictionary sizes [%-20s] %d%%" % ('='*(0/5), 0))
    for abr in LANGABBREVIATIONS:
        number_of_words[abr] = 0
        filename = 'dict/' + abr + '.txt'
        dictfile = open(filename, 'r')
        num_words = 0
        for line in dictfile:
            number_of_words[abr] += int(line.split()[1])
            num_words += 1
            if num_words > MAX_WORDS_PER_LANGUAGE:
                break
        total_num_words += number_of_words[abr]
        dictfile.close()
        num_files_done += 1
        progress = float(num_files_done) / float(len(LANGABBREVIATIONS)) * 100.0
        progress = int(progress)
        print_to_console("\rCalculating dictionary sizes [%-20s] %d%%" % ('='*(progress/5), \
		progress))
    print_to_console('\n')
    return total_num_words

def getlang(sentence, word_frequency, allwords):
    """Get a list containing the languages and associated probabilities that the
    sentence is believed to be."""

    best_relevance = 0
    best_lang = 'unknown'
    relevance_collection = {}

    sentence = sentence.lower()
    sentence = sentence.translate(string.maketrans("", ""), string.punctuation)
    sentence_list = sentence.split()

    # Sentences with 1 or 2 words are too unwieldy and show too many false positives
    if len(sentence_list) < 3:
        return ['unknown', 0.0, 0.0, []]

    for abr in LANGABBREVIATIONS:
        # Formula (6) from Řehůřek and Kolkus (2009)
        # Word relevance = SUM(gL(wi) << glang(wi)) fi · rel(wi, lang)
        # Where rel(w, lang) = log(glang(w)) − log(g0(w))

        relevance = 0
        for word in sentence_list:
            word_in_lang_freq = float(0.000000000001)
            word_in_corpus_freq = float(0.000000000001)
            if word in word_frequency[abr]:
                word_in_lang_freq = float(word_frequency[abr][word])
            if word in allwords:
                word_in_corpus_freq = float(allwords[word])
            relevance += math.log(word_in_lang_freq) - math.log(word_in_corpus_freq)

        # Formula (7)
        # (SUM(gL(wi) << glang(wi)) fi · rel(wi, lang)) / SUM(fi)
        relevance = relevance / len(sentence_list)

        if best_relevance < relevance:
            best_relevance = relevance
            best_lang = abr

        relevance_collection[abr] = relevance
    relevance_collection = sorted(relevance_collection.items(), \
    key=operator.itemgetter(1), reverse=True)
    if best_relevance < 0.0 or (relevance_collection[0][1] - relevance_collection[1][1] <= 0.4):
        best_lang = 'unknown'

    return [best_lang, relevance_collection]

def get_word_frequency(word_frequency, number_of_words, all_words):
    """Calculate each word's uncorrected observed frequency
    Formula (1): g[lang](w) = TF(w, C[lang]) / #(C[lang])
    with #(C) being the total number of words in corpus C
    and TF the number of occurences of a word in a corpus
    and g[0](w) = TF(w, C[0]) / #(C[0])"""

    num_files_done = 0
    print_to_console("Calculating word frequencies [%-20s] %d%%" % ('='*(0/5), 0))
    for abr in LANGABBREVIATIONS:
        word_frequency[abr] = {}
        filename = 'dict/' + abr + '.txt'
        dict_file = open(filename, 'r')
        num_words = 0
        for line in dict_file:
            word = line.split()[0]
            word_frequency[abr][word] = float(line.split()[1]) / number_of_words[abr]
            if word in all_words:
                all_words[word] += int(line.split()[1])
            else:
                all_words[word] = int(line.split()[1])
            num_words += 1
            if num_words > MAX_WORDS_PER_LANGUAGE:
                break
        dict_file.close()
        num_files_done += 1
        progress = float(num_files_done) / float(len(LANGABBREVIATIONS)) * 100.0
        progress = int(progress)
        print_to_console("\rCalculating word frequencies [%-20s] %d%%" % ('='*(progress/5), \
		progress))
    print_to_console('\n')

def to_weighted_frequency(all_words, total_num_words):
    """Turn the total word frequencies into a weighted frequency."""

    for word in all_words:
        count = all_words[word]
        all_words[word] = float(count) / total_num_words

def process_database(input_file, bad_sentences, word_frequency, all_words):
    """Find the incorrect sentences and place them into a list for later reporting."""

    print_to_console("Checking sentences [%-20s] %d%%" % ('='*(0/5), 0))
    result = {'correct' : 0, 'incorrect' : 0, 'unknown' : 0}
    num_lines_done = 0
    num_lines = sum(1 for line in open(input_file))
    sentence_file = open(input_file, 'r', 1)
    for line in sentence_file:
        tatoeba_id = line.split("\t")[0]
        real_lang = line.split("\t")[1]
        sentence = line.split("\t")[2].rstrip()

        # Only check languages that we have a model for
        if real_lang not in LANGABBREVIATIONS:
            continue

        estimation = getlang(sentence, word_frequency, all_words)
        est_lang = estimation[0]
        if est_lang == 'unknown':
            result['unknown'] += 1
        elif real_lang == est_lang:
            result['correct'] += 1
        elif real_lang != est_lang:
            result['incorrect'] += 1
            bad_sentences.append([sentence, real_lang, est_lang, tatoeba_id, estimation[1], \
            estimation[1][0][1] - estimation[1][1][1]])

        num_lines_done += 1
        if num_lines_done % 1000 == 0:
            progress = float(num_lines_done) / float(num_lines) * 100.0
            progress = int(progress)
            print_to_console("\rChecking sentences [%-20s] %d%%" % ('='*(progress/5), progress))
    print_to_console("\rChecking sentences [%-20s] %d%%\n" % ('='*(100/5), 100))
    sentence_file.close()
    return result

def write_report(output_file, result, bad_sentences):
    """Place the results of the sentence analysis into a text file."""

    outf = open(output_file, 'w')
    outf.write(str(result['correct']) + ' correct, ' + str(result['incorrect']) + \
    ' incorrect, ' + str(result['unknown']) + ' unknown\n')
    outf.write('\n')
    bad_sentences.sort(key=lambda tup: tup[5], reverse=True)
    for bad_sentence in bad_sentences:
        outf.write(bad_sentence[0] + '\n')
        outf.write("\tCurrent Language: " + CODETOLANG[bad_sentence[1]] + '\n')
        outf.write("\tSuggested Language: " + CODETOLANG[bad_sentence[2]] + '\n')
        outf.write("\tURL: http://tatoeba.org/eng/sentences/show/" + bad_sentence[3] + '\n\n')
        if VERBOSE:
            for pair in bad_sentence[4]:
                outf.write("\t" + CODETOLANG[pair[0]].ljust(15) + " " + str(pair[1]) + '\n')
            outf.write("\n")

def main():
    """Entrance to our script."""

    all_words = {}
    number_of_words = {}
    word_frequency = {}

    global QUIET
    global VERBOSE

    arguments = docopt(__doc__)
    input_file = arguments['INPUTFILE']
    output_file = arguments['OUTPUTFILE']
    QUIET = arguments['-q']
    VERBOSE = arguments['-v']

    total_num_words = get_number_of_words(number_of_words)
    get_word_frequency(word_frequency, number_of_words, all_words)
    to_weighted_frequency(all_words, total_num_words)

    bad_sentences = []
    result = process_database(input_file, bad_sentences, word_frequency, all_words)

    write_report(output_file, result, bad_sentences)

if __name__ == "__main__":
    main()
