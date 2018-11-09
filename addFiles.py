# requests for the files
import requests
import random
from optparse import OptionParser
import json
#inputs: number of files, number of keywords, input file, output file
parser = OptionParser()
parser.add_option("-f", "--files", dest="files", help="number of files for the system", default=1000)
parser.add_option("-k", "--keywords", dest="keys", help="keywords per file", default=5)
parser.add_option("-i", "--input", dest="input", help="input file for a list of keyword options", default="google-10000-english-master/google-10000-english-usa-no-swears-medium.txt")
parser.add_option("-n", "--nodes", dest="nodes", help="number of nodes for the system", default=3)

(options, args) = parser.parse_args()

number_of_files = int(options.files)
number_of_nodes = int(options.nodes)

number_of_keywords = int(options.keys)
input_file = str(options.input)
global words

def getWordFile():
	global words
	inputFileObj = open(input_file,'r')
	words = inputFileObj.read().split('\n')
	inputFileObj.close()

def getKeywordArray(number_of_keywords):
	keywords = []
	for i in range(number_of_keywords):
		keywords.append(getRandomWord())
	return keywords

def getRandomWord():
	global words
	return random.choice(words)

def getRandomHostUrl():
	# hello = 8000+random.randint(2,number_of_nodes+2)
	# return "hi" + str(hello)
	return "http://localhost:" + str(8000+random.randint(2,number_of_nodes+1)) + "/data"

def postRandomFiles():
	for i in range(number_of_files):
		url = getRandomHostUrl()
		keys = getKeywordArray(number_of_keywords)
		file =  getRandomWord()
		payload = {"fileName":file,"keywords":keys}
		print('adding ' + file + ' with ' + str(keys) + 'to ' + url)
		# print url
		# print file
		# print payload
		headers = {'Content-Type': 'application/json'}
		r = requests.post(url, headers=headers,json = payload)
		print('response: ' + r.text)
		print(i)
def main():
	getWordFile()

	postRandomFiles()






if __name__== "__main__":
    main()


