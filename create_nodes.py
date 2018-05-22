import os
import sys
import csv
import time
# import socket
import random
# from chord import *
import matplotlib.pyplot as plt
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-n", "--nodes", dest="nodes", help="number of nodes created within the system", default=10)
(options, args) = parser.parse_args()
nnodes = int(options.nodes)

data = []

#settings:
SIZE = nnodes #note not all nodes will be created because of repeated values due to psuedorandom random function
DATASIZE = data

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


# creates folders to hold all nodes
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# retrieve file data into global object
def retrieveData(data_csv):
    global data     
    inputFile = open(data_csv,'r')
    reader = csv.reader(inputFile)
    print 'making data object'    
    data = [r for r in reader]
    print 'made data object'
    return 

# retrieve specific row of data set
def retrieveRow(row):
    return data[row]


def addFile(row,hash_list):
    number_of_keywords = len(row)
    print 'number_of_keywords: '+ str(number_of_keywords)

    fileName = row[0]

    for keywords in row[1:]:
        print 'put '+fileName+' with '+str(keywords)
        print 'keyword hash: '+ str(abs(hash(keywords))) + ', ' + str(abs(hash(keywords))% SIZE) + ' ownerHash: '+str(findOwner(keywords,hash_list))

        x = int(findOwner(keywords,hash_list))
        print fileName + ' belongs at ' + str(hash_list[x][1])
        # keyword_hash = hash(keywords)
        # print keyword_hash % SIZE
        # print 'dude we found it?'
        # print findOwner(keywords,hash_list)

        #given list of nodes
        #find the one node that it is greater than but go to next greatest

    #find the node that should hold the key?


#find the immediate successor to a file/keyword given a list of nodes
def findOwner(file,hash_list):
    file_hash = abs(hash(file))% SIZE
    for i in range(len(hash_list)):
        print 'i: ' + str(i) + ' file_hash: ' + str(file_hash) + ' hash_list[i][0]: ' + str(hash_list[i][0])
        if(file_hash < hash_list[i][0]):
            return str(hash_list[(i)%len(hash_list)][0])
    return hash_list[0][0]
    #check for null then set to first indicie


def node2folder(node):
    return node.replace(':', '/')


# create a list of node addresses with corresponding hashes
def makeHashList(address_list):
    hash_list = []
    for x in range(len(address_list)):
        addressHash = (address_list[x].hash)
        address = (address_list[x].id)
        single = [addressHash,address]
        hash_list.append(single)

    return sorted(hash_list)

def makeNodes():
    print "Creating chord network with : %s nodes" % nnodes

    # create ip, port lists
    port_list = []
    ip_list = []
    for x in range(nnodes):
        ip_list.append(str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)))
        port_list.append(random.randrange(1, 65535))


    address_list = map(lambda (ip, port): Address(ip, port), zip(ip_list, port_list))
    # hash_list      = map(lambda addr: addr.__hash__(), address_list.id)

    # keep unique ones
    address_list = sorted(set(address_list))
    return address_list    


def main():

    address_list = makeNodes()

    hash_list = makeHashList(address_list)
    print 'hash_list'
    print hash_list


    createFolder('nodes/')
    for x in range(len(address_list)):
        createFolder('nodes/'+(address_list[x].id+'/'))

    # add keys into files?
    #retrieve data from file csv
    retrieveData('data.csv')
    print retrieveRow(3)

    addFile(retrieveRow(3),hash_list)


    # for i in range(len(data)):
    #     add_file()        


    # get a single row
    # add file for all keywords





    # plotlist = []
    # for x in range(len(address_list)):
    #   plotlist.append(address_list[x].hash)

    # print address_list[0]
    # print address_list[0].hash

    # plt.plot(plotlist, 'ro')
    # plt.ylabel('some numbers')
    # plt.show()



    # print hash_list[0]
  
if __name__== "__main__":
  main()


