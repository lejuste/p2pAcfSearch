# requests for the files
import requests
import random
from optparse import OptionParser
import json
import csv 
import time

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
global dataDict
dataDict = dict()

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

def getRandomHostUrlforData():
	return "http://localhost:" + str(8000+random.randint(2,number_of_nodes+1)) + "/data"

def getRandomHostUrlforSearch():
	return "http://localhost:" + str(8000+random.randint(2,number_of_nodes+1)) + "/search"

def postRandomFiles():
	# with open('names.csv', 'w') as csvfile:
	# 	fieldnames = ['fileName', 'Keywords']
	# 	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	# 	writer.writeheader()

	for i in range(number_of_files):
		print (i)
		url = getRandomHostUrlforData()
		keys = getKeywordArray(number_of_keywords)
		file =  getRandomWord()
		payload = {"fileName":file,"keywords":keys}
		print('adding ' + file + ' with ' + str(keys) + 'to ' + url)
		dataDict[file]=keys
		headers = {'Content-Type': 'application/json'}
		r = requests.post(url, headers=headers,json = payload)
		time.sleep(3)

		# print('response: ' + r.text)
			# writer.writerow({'fileName': file, 'Keywords': str(keys)})

def returnTime(response):

	data = json.loads(response)
	return str(data['finalTime'])
	
def searchForFiles():
	timeFileName = str("timeTrials/time_file_for_" + str(number_of_nodes)+"_nodes_.txt")
	fileOut = open(timeFileName,"w+") 
	j = 0
	for file in dataDict.keys():
		print(j)
		j+=1
		keys =  dataDict.get(file,0)

		url = getRandomHostUrlforSearch()
		payload = {"keywords":keys}
		print('searching with ' + str(keys) + 'to ' + url)
		headers = {'Content-Type': 'application/json'}
		r = requests.post(url, headers=headers,json = payload, timeout = 5)
		print(r.text)
		fileOut.write(str(returnTime(r.text) + "\n"))

	fileOut.close() 



def main():
	getWordFile()
	postRandomFiles()
	print('done post')
	searchForFiles()
	print('done search')


if __name__== "__main__":
	main()


