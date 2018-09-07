import os
import sys
import csv
import time
import random
from optparse import OptionParser

from bloom import BitVector
from bloom import Bloomfilter

parser = OptionParser()
parser.add_option("-n", "--nodes", dest="nodes", help="number of nodes created within the system", default=10)
parser.add_option("-i", "--input", dest="input", help="data file for data store", default="data.csv")
parser.add_option("-f", "--files", dest="fileAmount", help="number of files to initially add to the network", default=5)


(options, args) = parser.parse_args()
nnodes = int(options.nodes)
input_file = str(options.input)
number_of_files = int(options.fileAmount)

data = []

#settings:
SIZE = nnodes #note not all nodes will be created because of repeated values due to psuedorandom random function
# DATASIZE = data

#-------------------------------------------------------p2p datastore setup-------------------------------------------------------

#address objects for each node within the data store system
class Address(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.hash = 0
        self.id = "%s:%s" % (self.ip,self.port)

    def __hash__(self):
        self.hash = hash(self.id) % SIZE
        return self.hash

    def __str__(self):
        return "[\"%s\", \"%s\", %s, %s]" % (self.id, self.ip, self.port, self.hash)

# Creates a list of node addresses with corresponding hashes
def makeHashList(address_list):
    hash_list = []
    for x in range(len(address_list)):
        addressHash = (address_list[x].hash)
        address = (address_list[x].id)
        single = [addressHash,address]
        hash_list.append(single)

    return sorted(hash_list)

# Randomly generates certain number of nodes 
def makeNodes(number_of_nodes):
    print "Creating chord network with : %s nodes" % number_of_nodes

    # generate random values for ports and ip addresses
    port_list = []
    ip_list = []
    for x in range(number_of_nodes):
        ip_list.append(str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)))
        port_list.append(random.randrange(1, 65535))

    #creates local address list that maps out corresponding ip:port values
    address_list = map(lambda (ip, port): Address(ip, port), zip(ip_list, port_list))

    # keep unique ones
    address_list = sorted(set(address_list))
    
    # returns list of strings containing ip:port values
    return address_list    

# Creates single folder represending a single node with a file_store.txt file 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

            file_store = directory+'file_store.csv'

            myFile = open(file_store, 'w')
            with myFile:
                writer = csv.writer(myFile)
                writer.writerow(['Files on node:','keywords'])

            myFile.close()

    except OSError:
        print ('Error: Creating directory. ' +  directory)

# Makes folders for each node 
def makeNodeFolders(address_list):
    createFolder('nodes/')
    for x in range(len(address_list)):
        createFolder('nodes/'+(address_list[x].id+'/'))

#-------------------------------------------------------p2p datastore setup-------------------------------------------------------

#--------------------------------------------------------data setup---------------------------------------------------------------

# Find the immediate successor to a file/keyword given a list of nodes
def findOwner(file,hash_list):
    file_hash = abs(hash(file))% SIZE
    for i in range(len(hash_list)):
        # print 'i: ' + str(i) + ' file_hash: ' + str(file_hash) + ' hash_list[i][0]: ' + str(hash_list[i][0])
        if(file_hash < hash_list[i][0]):
            return str(hash_list[(i)%len(hash_list)][0])
    return hash_list[0][0]
    #check for null then set to first indicie

# Fill global data[] object from the input file
def retrieveData(data_csv):
    global data     
    inputFile = open(data_csv,'r')
    reader = csv.reader(inputFile)
    print 'making data object'    
    data = [r for r in reader]
    print 'made data object'
    return 

# Adds a given file, it is placed on nodes corresponding with file's keywords.
def addFile(row,hash_list):
    print 'Adding ' + row[0] + 'into p2p system with keywords ' + str(row[1:])
    fileName = row[0]


    for keyword in row[1:]:
        # Determines the successor to file's specific keyword
        x = int(findOwner(keyword,hash_list))

        print fileName + ' belongs at ' + str(hash_list[x][1]) +' for keyword: '+str(keyword)

        # Adds new file to node's datastore
        file_store = str('nodes/'+ hash_list[x][1]) + '/file_store.csv'

        
        f = open(file_store, 'a')
        writer = csv.writer(f)
        writer.writerow([fileName,keyword])

        bloomObject = Bloomfilter('nodes/'+str(hash_list[x][1])+'/bloom_'+str(keyword)+'.txt')
        bloomObject.addToFilter(fileName)

def getFilesonNode(node):
    print 'Getting files at node %s' % (node)

    with open('nodes/'+node+ '/file_store.csv', 'r') as f:
        lines = list(csv.reader(f))
    fileNames =[]
    for line in lines[1:]:
        fileNames.append(line[0])

    return list(set(fileNames))

def getFilesForKeyword(node, keyword):
    print 'Getting files at node %s' % (node)

    with open('nodes/'+node+ '/file_store.csv', 'r') as f:
        lines = list(csv.reader(f))
    fileNames =[]
    for line in lines[1:]:
        if(keyword in line):
            print keyword + ' is in the following: ' + str(line) + ', logging file ' + line[0] 
            fileNames.append(line[0])
        # fileNames.append(line[0])

    return list(set(fileNames))

# def getFilesForKeywords(node, keywords):
#     print 'Getting files at node %s' % (node)

#     with open('nodes/'+node+ '/file_store.csv', 'r') as f:
#         lines = list(csv.reader(f))
#     fileNames =[]
#     for line in lines[1:]:


#         # per line check that all keywords are 
#         for keyword in keywords:
#             if(keyword in line):
#             print keyword + ' is in the following: ' + str(line) + ', logging file ' + line[0] 
#             fileNames.append(line[0])

#         # fileNames.append(line[0])

#     return fileNames
 
# def removeFilesonNode(node,fileName):

#     print 'Getting files at node %s' % (node)
#     lines = [line.rstrip('\n') for line in open('nodes/'+node+ '/file_store.txt')]
#     fileNames =[]
#     print lines[1:]
#     for line in lines[1:]:
#         # print line.split()[1]
#         fileNames.append(line.split()[1])

#     print list(set(fileNames))

def bloomObjANDFiles(bloomObj,fileNames):


 # bloomObject = Bloomfilter('nodes/'+search_nodes[0]+'/bloooom.txt')

    # # finds intersection of all filters
    # for node in search_nodes[1:]:
    #     print 'intersection for node %s' %(node)
    #     print getFilter(node)
    #     bloomObject.filter.rebuildVector(bloomObject.intersection(getFilter(node)))

    print 'fileNames before' + str(fileNames)

    intersection = []
    for curr_file in fileNames:
        print 'fileName: ' + curr_file
        if bloomObj.checkFilter(curr_file):
            intersection.append(curr_file)

    print 'fileNames after' + str(intersection)
    return intersection
    #NOTE: FAILS WHEN THE TWO NODES ARE HAPPEN TO HOLD 2 OF THE SAME FILES WITH DIFFERENT KEYWORDS

#--------------------------------------------------------data setup---------------------------------------------------------------

#--------------------------------------------------------bloom search---------------------------------------------------------------
def search_keywords(query,hash_list,searchType):
    keywords_list = query.strip(' ').split(" ")
    print keywords_list   

    #find a list of nodes with following keywords
    search_nodes = []
    for key in keywords_list:
        x = int(findOwner(key,hash_list))
        print 'node %s has files with keyword %s ' % (str(hash_list[x][1]), key)
        search_nodes.append(str(hash_list[x][1]))

    if len(keywords_list) == 1:
        return getFilesForKeyword(search_nodes[0], keywords_list[0])
    else:
        #     do something for first node
        #     do something different for all other nodes

        # given 2 keywords
        
        # figure out host 1 has keyword 1

        # search_nodes[0]
        # given this guy

        #works for 2 keywords:

        # firstFilterObject = Bloomfilter('nodes/'+search_nodes[0]+'/'+'bloom_'+keywords_list[0]+'.txt')
        # print 'intersection between filter of '+keywords_list[0]+' and files on node '+search_nodes[1] 
        # print bloomObjANDFiles(firstFilterObject,getFilesonNode(search_nodes[1]))

        filterObject = Bloomfilter('nodes/'+search_nodes[0]+'/'+'bloom_'+keywords_list[0]+'.txt')

        # EXPLICIT SEARCH NEEDS TO SEND THE ACTUAL FILE NAMES
        if searchType == 'explicit':
            for node in search_nodes[1:]:
                print 'intersection between filter of '+keywords_list[0]+' and files on node '+search_nodes[1] 
                file_list = bloomObjANDFiles(filterObject,getFilesonNode(node))
                print file_list
                # newFilter  = made from file_list

                # new filter AND node list

                filterObject = Bloomfilter('new_filter_temp.txt')
                for file in file_list:
                    filterObject.addToFilter(file)

                # make newnew filter

                # newnew filter AND node list

            return file_list
                # print 'intersection for node %s' %(node)
                # print getFilter(node)
                # bloomObject.filter.rebuildVector(bloomObject.intersection(getFilter(node)))



        # THROUGHPUT SEARCH NEEDS TO SEND THE NEWLY CREATED FILTERS
        elif searchType == 'throughput':
            print 'to be implemented: throughput'
        else:
            return 'ERROR: invalid search type.'

        # search host 2 given a bloom filter
        
        # send the filter of the first keyword to host 2

        # host 2 sends host 1 the files that are associated with the filter sent. 
        # host 1 will send only interection of all of the files that are interection with itself

        return 'too many keywords'


    # cases:

    # find first host

    # only one keyword
    #     use first host
    #     search for file with keyword
    #     return a list of files with those keywords

    # multiple keywords
    #     find hosts for every keyword
    #         get its bloom filter
    #             if bloom filter matches
    #                 find file name that matches
    #                 return fileName
    #             else 
    #                 do nothing

    # # double check file name in file intersetcion?

    # mulitple keywords:












    #     create a bloom filter for first node
    #     retrieve all bloom filters for the other hosts
    #     create an intersection

    # keyword1 = Bloomfilter('nodes/'+search_nodes[0]+'/bloooom.txt')

    # each host has a bloom filter for each of its keywords that it maintains




    # # search search_nodes[0]
    # # return list of files with the keyword
    # print 'length of search nodes: '+str(len(search_nodes))+ ', ' + str(len(keywords_list))
    # print str(search_nodes)
    # print str(keywords_list)


    # # Identifies first node in search
    # bloomObject = Bloomfilter('nodes/'+search_nodes[0]+'/bloooom.txt')

    # # finds intersection of all filters
    # for node in search_nodes[1:]:
    #     print 'intersection for node %s' %(node)
    #     print getFilter(node)
    #     bloomObject.filter.rebuildVector(bloomObject.intersection(getFilter(node)))

    # # Searches for intersections with filter and self nodes
    # # Currently implemented where all nodes only have a single bloom filter for their own files

    # good_files = []

    # filesForFirstNode = getFilesonNode(search_nodes[0])
    # for file in filesForFirstNode:
    #     if bloomObject.checkFilter(file):
    #         good_files.append(file)

    # return good_files

def getFilter(node_ip):

    f = open('nodes/'+node_ip+'/bloooom.txt', "r")
    contents = f.read()
    f.close()
    return contents   


#--------------------------------------------------------bloom search---------------------------------------------------------------

def main():

    # removeFilesonNode('194.245.61.39:6445',"VZURDTFKENEG")
#-------------------------------------------------------p2p datastore setup-------------------------------------------------------

    address_list = makeNodes(nnodes)
    hash_list = makeHashList(address_list)
    makeNodeFolders(address_list)

#-------------------------------------------------------p2p datastore setup-------------------------------------------------------
    
    retrieveData(input_file)

    # Adds number of files from data[] 
    for x in range(number_of_files):
        addFile(data[x+1],hash_list) 

    while(1):
        keywords = raw_input("Which keywords are you looking for associated with files?")
        
        queryResults = search_keywords(keywords,hash_list,'explicit')

        print '\n Here r ur files dood:\n'
        print queryResults
        # for file in queryResults:
        #     print file
        print 'have a nice day bud.\n'


    # bloomObject = Bloomfilter('bloombaby.txt')
    # print 'Printing bloomObject:'
    # print bloomObject


    # plotlist = []
    # for x in range(len(address_list)):
    #   plotlist.append(address_list[x].hash)

    # print address_list[0]
    # print address_list[0].hash

    # plt.plot(plotlist, 'ro')
    # plt.ylabel('some numbers')
    # plt.show()
  
if __name__== "__main__":
  main()


