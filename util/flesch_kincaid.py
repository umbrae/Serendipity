# Gratefully borrowed from @proj at http://www.slumberheart.com/things/flesch_kincaid.py

import nltk
from nltk.corpus import cmudict
from re import match

cmu = cmudict.dict()
def syllable_count(word):
	reduced = reduce(word)
	if (not len(reduced)) or (not reduced in cmu):
		return 0
	return len([x for x in list(''.join(list(cmu[reduced])[-1])) if match(r'\d', x)])

def reduce(word):
	return ''.join([x for x in word.lower() if match(r'\w', x)])

def grade_level(text):
	sentences = nltk.tokenize.sent_tokenize(text)
	totalwords = 0
	totalsyllables = 0
	totalsentences = len(sentences)
	for sentence in sentences:
		words = nltk.tokenize.word_tokenize(sentence)
		words = [reduce(word) for word in words]
		words = [word for word in words if word != '']
		totalwords += len(words)
		syllables = [syllable_count(word) for word in words]
		totalsyllables += sum(syllables)
	totalwords = float(totalwords)
	return ( # Flesh-Kincaid Grade Level formula. Thanks, Wikipedia!
			0.39 * (totalwords / totalsentences)
			+ 11.8 * (totalsyllables / totalwords)
			- 15.59 )
