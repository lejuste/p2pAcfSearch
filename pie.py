import csv 
import sys
import random
from random import choice
from string import ascii_uppercase
from optparse import OptionParser


#inputs: number of files, number of keywords, input file, output file
parser = OptionParser()
parser.add_option("-f", "--files", dest="files", help="number of files for the system", default=100)
parser.add_option("-k", "--keywords", dest="keys", help="keywords per file", default=5)
parser.add_option("-o", "--output", dest="output", help="output file to save data", default="data.csv")
parser.add_option("-i", "--input", dest="input", help="input file for a list of keyword options", default="google-10000-english-master/google-10000-english-usa-no-swears-medium.txt")

(options, args) = parser.parse_args()

number_of_files = int(options.files)
number_of_keywords = int(options.keys)
output_file = str(options.output)
input_file = str(options.input)

#output file creation and selecting which file is used for keyword selection
outputFile = open(output_file,'wb')
words = open(input_file,'r')
lines = words.read().split('\n')


#adding files to output file
with outputFile:
	writer = csv.writer(outputFile)

	#make title columns:
	titleRow = ['File Name']
	for i in range(number_of_keywords):
		titleRow.append('keyword '+str(i+1))
	writer.writerow(titleRow)

	# add files with keywords to output file
	for i in range(number_of_files):
		row = []

		#make file name
		fileName = (''.join(choice(ascii_uppercase) for i in range(12)))
		row.append(fileName)

		#add keywords associated with each file
		for i in range(number_of_keywords):		
			row.append(lines[random.randrange(0,5460)])

		#write new file to data csv
		writer.writerow(row)
		del row[:]

#close the files
words.close()
outputFile.close()

