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

            # makes file store file
            file_store = directory+'file_store.txt'
            f = open(file_store, "w+")
            f.write('Files on node:')
            f.close()
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

# # Retrieve specific row of data set
# def retrieveRow(row):
#     return data[row]

# Adds a given file, it is placed on nodes corresponding with file's keywords.
def addFile(row,hash_list):
    print 'Adding ' + row[0] + 'into p2p system with keywords ' + str(row[1:])
    fileName = row[0]


    for keywords in row[1:]:
        # Determines the successor to file's specific keyword
        x = int(findOwner(keywords,hash_list))

        print fileName + ' belongs at ' + str(hash_list[x][1]) +' for keyword: '+str(keywords)

        # Adds new file to node's datastore
        file_store = str(hash_list[x][1]) + '/file_store.txt'
        f = open('nodes/'+file_store, "a+")
        f.write('\nfile: ' + fileName + ' keywords: ' + keywords)
        f.close()


        #build blooom filters for the entire node!!!
        bloomObject = Bloomfilter('nodes/'+str(hash_list[x][1])+'/bloooom.txt')
        bloomObject.addToFilter(fileName)


#--------------------------------------------------------data setup---------------------------------------------------------------

def main():

#-------------------------------------------------------p2p datastore setup-------------------------------------------------------

    address_list = makeNodes(nnodes)
    hash_list = makeHashList(address_list)
    # print 'hash_list'
    # print hash_list
    makeNodeFolders(address_list)

#-------------------------------------------------------p2p datastore setup-------------------------------------------------------
    
    retrieveData(input_file)

    # Adds number of files from data[] 
    for x in range(number_of_files):
        addFile(data[x+1],hash_list) 


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


