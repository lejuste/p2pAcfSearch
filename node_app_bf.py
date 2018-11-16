from flask import Flask, request, make_response, jsonify

import requests
import os
import sys
import operator
import hashlib
from bloom_modified import Bloomfilter
from bloom_modified import BitVector
from cuckoopy import CuckooFilter
import cuckoo
from types import MethodType
# Initialize a cuckoo filter with 10000 buckets with bucket size 4 and fingerprint size of 1 byte
# cf = CuckooFilter(capacity=10000, bucket_size=4, fingerprint_size=1)
# print ('cuckoo import successful, response: ', cf.insert('Hello!'))

import json

import time

app = Flask(__name__)
print ('starting node! blom style')



# cf.method4printing = MethodType(printIt, cf)
# cf.method4printing()
# readCF(cf)


# ----------------------------- SETUP ENVIRONMENTAL VARIABLES -------------------------------------
IP_ENV = os.environ.get('ip')      #.get() is a safe way to get values from a dictionary if their key might not exist
VIEW = os.environ.get('VIEW')
ip_port = os.environ.get('ip_port')
num_keywords = os.environ.get('num_keywords')
randomId = os.environ.get('randomId')


MAXSIZE = 3000 #note not all nodes will be created because of repeated values due to psuedorandom random function
bloomDict = dict()

lastBloomCheck = False

# ----------------------------- HELPER FUNCTIONS --------------------------------------------------
def hashIt(input1):
    # return abs(hash(str(input1))%MAXSIZE)
    # dont do an int to eliminate 
    # return(abs(int(hashlib.sha224(input1).hexdigest(),16)))
    # print 'hash it'
    # print hashlib.sha224(input1).hexdigest()
    # print abs(int(hashlib.sha224(input1).hexdigest(),16)%MAXSIZE)

    return(abs(int(hashlib.sha224(input1.encode('utf-8')).hexdigest(),16)%MAXSIZE))
    # return(abs(int(hashlib.sha224(input1).hexdigest(),16))%MAXSIZE)
    # return abs(hash(str(hash(str(input)))))

# INPUT: keyword - keyword for file
# OUTPUT: boolean whether to create a new file or not to

# Creates a list of node addresses with corresponding hashes
def bloomItemExists(keyword):
    global bloomDict
    for item in bloomDict:
        if item == keyword:
            return True
    return False

def bloomItemAdd(keyword,fileName):
    global bloomDict

    # if bloom item exists, print
    if(bloomItemExists(keyword)):
        keyBloom = bloomDict.get(keyword, [])
        keyBloom.addToFilter(fileName)
    else:
        new_keyword_filter = Bloomfilter(keyword)
        new_keyword_filter.addToFilter(fileName)
        bloomDict[keyword] = new_keyword_filter

def bloomItemCheck(keyword):
    if(bloomItemExists(keyword)):
        theFilter = bloomDict.get(keyword, [])
        # print 'results:'
        # print theFilter.checkFilter(keyword)
        # print 'end of results'
        return theFilter.checkFilter(keyword)
    else:
        return 0

def getKeywordFilter(keyword):
    return bloomDict.get(keyword, 0)

def bloomItemIntersection(filter1,filter2):
    return filter1 & filter2

def rebuildBloomFilter(keywords):
    # startTime = time.time()
    global lookup
    global bloomDict
    # print 'startTime: ' + str(startTime)
    bloomDict = {}

    for fileName in lookup:
        keywords = lookup.get(fileName,[])
        print(('keywords: ' + str(keywords) + ' for ' + fileName))
        for tag in keywords:
            print(('empty bloom dict' + str(bloomDict)))
            bloomItemAdd(tag,fileName)
    return
    # print 'total time ' + str(totalTime)
    # return totalTime


def readCF(obj):
    obj.method4printing = MethodType(cuckoo.printIt, obj)
    obj.method4printing()

def setCF(obj):
    obj.method4printing = MethodType(cuckoo.printIt, obj)
    obj.method4printing()

# ----------------------------- DIRECTORY FOR ROUTING ---------------------------------------------

# INPUT: view - list of strings ip:port
# OUTPUT: sorted tuple list of hash(ip:port),ip:port

# Creates a list of node addresses with corresponding hashes
def makeHashList(address_list):
    hash_list = []
    for x in range(len(address_list)):
        # addressHash = (address_list[x].hash) #hash the address
        # address = (address_list[x].id) # get the ip and port
        addressHash = hashIt(address_list[x])
        single = [addressHash,address_list[x]] # create a tuple with the hash and then the address
        hash_list.append(single)
    print([sorted(hash_list)])
    return sorted(hash_list)

# ----------------------------- SETUP HOST LIST / HOST DICT ---------------------------------------

hostlist = []
if VIEW is None:
    hostlist.append(ip_port)
else:
    hostlist = str(VIEW).split(',')
hostDictionary = dict((host,hashIt(host)) for host in hostlist)
hash_list = makeHashList(hostlist)

# ----------------------------- LOCAL VARIABLES ---------------------------------------------------

lookup = {}
local_host_hash = hashIt(str(IP_ENV))

#--------------------------------------------------------data setup---------------------------------------------------------------

# INPUT: keyword - tags for the given file
#        hashlist - tuple list of hash(ip:port),ip:port
# OUTPUT: node number in hashlist for 

# Find the immediate successor to a file/keyword given a list of nodes
def findOwner(file,hash_list):
    file_hash = hashIt(file)
    for i in range(len(hash_list)):
        # print 'i: ' + str(i) + ' file_hash: ' + str(file_hash) + ' hash_list[i][0]: ' + str(hash_list[i][0])
        if(file_hash < hash_list[i][0]):
            # print 'hashlist ' + str(hash_list)
            print(('file_hash ' + str(file_hash))) 
            return str(hash_list[i][1])
    # print 'hashlist ' + str(hash_list)
    print(('file_hash ' + str(file_hash)))                    
    return str(hash_list[0][1])
    #check for null then set to first indicie


# INPUT: keywords - tags for the given file
#        hashlist - tuple list of hash(ip:port),ip:port
#        fileName - file name / file data
# OUTPUT: node number in hashlist for 

# Find the immediate successor to a file/keyword given a list of nodes
def addFile(fileName,keywords,hash_list):
    global ip_port
    # print 'add file is called.'
    fileLocations = []
    perfectHit = True
    data = []
    for keyword in keywords:
 
        fileLocation = findOwner(keyword,hash_list)

        if fileLocation == ip_port:
            print(('SAVING ' + str(fileName) + ' to ' + fileLocation + ' for ' + keyword))
            data = lookup.get(fileName, [])
            data.append(keyword)
            lookup[fileName] = data
            bloomItemAdd(keyword,fileName)
        else:
            fileLocations.append(fileLocation)
            perfectHit = False

    for i in range(len(fileLocations)):
        payload = {'fileName': fileName, 'keywords':[keywords[i]]}
        print(('FORWARDING ' + str(payload) + ' to ' + 'http://'+fileLocations[i]+'/data'))
        r = requests.post('http://'+fileLocations[i]+'/data', json = payload)        

    if perfectHit:
        j = jsonify(msg='success', owner=fileLocation, file=fileName, keywords = keywords )
        return (make_response(j,200,{'Content-Type':'application/json'}))               
    else: 
        return (make_response(r.text,r.status_code,{'Content-Type':'application/json'}))  


def deleteFileFlood(fileName,hostlist):
    global ip_port
    print(hostlist)
    for host in hostlist:
        if host != ip_port:
            payload = {'fileName': fileName}
            print(('Deleting ' + str(fileName) + ' at ' + 'http://'+host+'/data'))
            r = requests.delete('http://'+host+'/dataDelete', json = payload)        
     
    j = jsonify(msg='done talking to other hosts', file=fileName, )
    return (make_response(j,200,{'Content-Type':'application/json'}))                         


def deleteFileLocally(fileName):
    global lookup
    keywordsForfile = lookup.get(fileName,[])
    if(len(keywordsForfile) > 0):
        del lookup[fileName]
        rebuildBloomFilter()
    


# INPUT: node,ip - node ip address and port
#        keyword - keyword to search for on the node
# OUTPUT: a list of the file names

# Find the immediate successor to a file/keyword given a list of nodes
def getFileNamesForKeyword(keyword):
    global lookup
    global ip_port
    print(('getFiles at Node ' + ip_port + '\nkeyword'))
    print(keyword)
    print('kvs')
    print(kvs)

    files = []

    for fileName in lookup:
        keywords = lookup.get(fileName, [])
        print(('keywords: ' + keywords + ' in ' + fileName))
        for tag in keywords:
            if(keyword == tag):
                files.append(fileName)
    return list(set(files))

'''builds ip:hash(ip) dictionary'''
def make_ip_hash(hostlist):
    for host in hostlist:
        hostDictionary.update({str(host):hashIt(str(host))})        

'''test function: prints key and hash(key) and successor'''
def testValue(testKey):
    print("___________________________________________________________________________")
    hashedKey=hashIt(str(testKey)) #hashes the STRING of the key    
    print(("Our key is " + str(testKey) + ", whose hash is " + str(hashedKey)))
    print(("The successor of this key is " + str(findSuccessor(testKey,hostDictionary))))

def search_keywords(keywords,hash_list,searchType):
    # print 'keywords'
    # print keywords
    # print 'hash_list'
    # print hash_list

    # if len(keywords) == 0:
    #     j = jsonify(msg='no keywords', files=[], keywords = keywords)
    #     return (make_response(j,200,{'Content-Type':'application/json'}))  

    # THROUGHPUT SEARCH NEEDS TO SEND THE NEWLY CREATED FILTERS
    # send filter filter filter filter then filenames once
    # must forward: startTime(),remaining keywords,currentFilter
    startTime = time.time()
    # print 'start time: ' + str(startTime)
    nodeFilter = BitVector()
    remainingKeywords = []

    for keyword in keywords:
 
        fileLocation = findOwner(keyword,hash_list)
        if fileLocation == ip_port:
            print(('found: ' + keyword))
            filterObject = getKeywordFilter(keyword)
            if(filterObject):
                keyVector = filterObject.getBitVector()
                nodeFilter.bitwiseOr(keyVector)
        else:
            remainingKeywords.append(keyword)

    print(remainingKeywords)
    if(len(remainingKeywords) > 0):
        print('finding next node')
        nextNode = findOwner(remainingKeywords[0],hash_list)
        print(nextNode)
        payload = {'startTime': startTime, 'keywords': remainingKeywords, 'currentFilter':nodeFilter.vector}
        print(('FORWARDING ' + str(payload) + ' to ' + 'http://'+nextNode+'/search'))
        r = requests.post('http://'+nextNode+'/search', json = payload)        

        print((getJsonAttribute(r.text,'final time')))
        return (make_response(r.text,r.status_code,{'Content-Type':'application/json'}))  
    # j = jsonify(msg='success', json=r.json())
    else:

        print('all files are local')
        # return the keywords and the current time!!!!!
        finalFilter = Bloomfilter()
        finalFilter.filterUpdate(nodeFilter.vector)
        results = []
        for file in lookup:
            if finalFilter.checkFilter(file):
                results.append(file)

        totalTime = time.time() - startTime
        j = jsonify(msg='success',finalTime = totalTime, results = results)
        return (make_response(j,200,{'Content-Type':'application/json'}))  

        # # jsonResponse = r.text
        # # d = json.loads(jsonResponse)
        # # print 'final time'
        # # print d.get('finalTime', 'lololol')
        # # # print '....'
        # # j = jsonify(msg='success',finalTime = ti, results = results)
        # # return (make_response(j,200,{'Content-Type':'application/json'}))  
        # for file in lookup:
        #     if finalFilter.checkFilter(file):
        #         results.append(file)

        # totalTime = time.time() - startTime

        # j = jsonify(msg='success', finalTime = totalTime, fileNames = 'nonern')
        # return (make_response(j,200,{'Content-Type':'application/json'})) 
        # return internal_search_keywords(startTime,keywords) 

def getJsonAttribute(text,field):
    d = json.loads(text)
    return d.get(field,None)



# @app.route('/internalSearch', methods=['GET','PUT','DELETE'])
def  internal_search_keywords(startTime,keywords,currentFilter = None):
    print('............................ in internal .................................')
    print(startTime)
    print(keywords)
    print(currentFilter)

    global hash_list
    global lookup
    # THROUGHPUT SEARCH NEEDS TO SEND THE NEWLY CREATED FILTERS
    # send filter filter filter filter then filenames once
    # must forward: startTime(),remaining keywords,currentFilter
    # startTime = time.time()
    # print 'start time: ' + str(startTime)
    nodeFilter = BitVector()
    if currentFilter != None:
        nodeFilter.rebuildVector(currentFilter)
    remainingKeywords = []
    print(nodeFilter)
    for keyword in keywords:
 
        fileLocation = findOwner(keyword,hash_list)
        if fileLocation == ip_port:
            print(('found: ' + keyword))
            filterObject = getKeywordFilter(keyword)
            if(filterObject):
                keyVector = filterObject.getBitVector()
                nodeFilter.bitwiseOr(keyVector)
        else:
            remainingKeywords.append(keyword)

    print(remainingKeywords)
    if(len(remainingKeywords) > 0):
        print('finding next node')
        nextNode = findOwner(remainingKeywords[0],hash_list)
        print(nextNode)
        payload = {'startTime': startTime, 'keywords': remainingKeywords, 'currentFilter':nodeFilter.vector}
        print(('FORWARDING ' + str(payload) + ' to ' + 'http://'+nextNode+'/search'))
        r = requests.post('http://'+nextNode+'/search', json = payload)       

        print((getJsonAttribute(r.text,'final time')))
        return (make_response(r.text,r.status_code,{'Content-Type':'application/json'}))  
    else:
        # return the keywords and the current time!!!!!
        finalFilter = Bloomfilter()
        finalFilter.filterUpdate(nodeFilter.vector)
        results = []
        for file in lookup:
            if finalFilter.checkFilter(file):
                results.append(file)

        totalTime = time.time() - startTime
        j = jsonify(msg='success',finalTime = totalTime, results = results)
        return (make_response(j,200,{'Content-Type':'application/json'}))  

@app.route('/')
def hello_world():
    return 'here is the hashlist' + str(hash_list)




@app.route('/search', methods=['GET','PUT','POST','DELETE'])
def searchMethod():
    global lookup
    global hostDictionary
    global hostlist
    global hash_list

    if request.method == 'POST':
        jsonObj = request.get_json(silent=True)
        keywords = jsonObj.get('keywords', None)
        startTime = jsonObj.get('startTime', None)

        if keywords == None: # return failed search
            j = jsonify(msg='fail', test="keys undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
        if startTime == None: # start a search
            print(('RECEIVED SEARCH for ' + str(keywords)))

            return search_keywords(keywords,hash_list,'explicit')
        else: # internal searches that are part of process
            currentFilter = jsonObj.get('currentFilter', None)
            print('in else')
            return internal_search_keywords(startTime,keywords,currentFilter)

    else:
        j = jsonify(msg='FAIL!!!')
        return (make_response(j,200,{'Content-Type':'application/json'}))  # '''RECEIVE HOST LIST UPDATE TO REMOVE OR ADD A NODE TO LOCAL 'VIEW'''

'''key-value GET, PUT, and DELETE Requests'''
@app.route('/data', methods=['POST','GET','PUT','DELETE'])
def stuff():
    global lookup
    global hostDictionary
    global hostList
    global hash_list
    # print 'got it'
    if request.method == 'POST':
        # print 'got put'
        # data = request.data
        # dataDict = json.loads(data)
        # print dataDict
        # print dataDict.get('fileName')
        # print dataDict.get('keywords')
        jsonObj = request.get_json(silent=True)
        # print 'get json obj'
        # print jsonObj
        fileName= jsonObj.get('fileName', None)
        keywords = jsonObj.get('keywords', None)

        if fileName == None or keywords == None:
            j = jsonify(replaced=0, msg='fail', test="filename or keywords undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
        # update hash list!
        print(('Adding fileName ' + str(fileName) +  ' keywords: ' + str(keywords)))
        return addFile(fileName,keywords,hash_list)

    if request.method == 'DELETE':
        startTime = time.time()
        jsonObj = request.get_json(silent=True)
        fileName= jsonObj.get('fileName', None)
        if fileName == None:
            j = jsonify(replaced=0, msg='fail', test="filename or keywords undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
        else:
            print(('Deleting file called  ' + str(fileName)))
            deleteFileLocally(fileName)
            deleteFileFlood(fileName,hostlist) 
            j = jsonify(msg='done talking to other hosts', file=fileName, totalTime=time.time()-startTime)
            return (make_response(j,200,{'Content-Type':'application/json'}))   

    else:
        j = jsonify(msg='FAIL!!!')
        return (make_response(j,200,{'Content-Type':'application/json'}))  # '''RECEIVE HOST LIST UPDATE TO REMOVE OR ADD A NODE TO LOCAL 'VIEW'''


@app.route('/dataDelete', methods=['POST','GET','PUT','DELETE'])
def delete():
    global lookup
    global hostDictionary
    global hash_list
    # print 'got it'
    if request.method == 'DELETE':
        jsonObj = request.get_json(silent=True)
        fileName= jsonObj.get('fileName', None)
        if fileName == None:
            j = jsonify(replaced=0, msg='fail', test="filename or keywords undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
        else:
            print(('Deleting file called ' + str(fileName)))
            deleteFileLocally(fileName)
            j = jsonify(msg='deleting locally!!!')
            return (make_response(j,200,{'Content-Type':'application/json'}))  # '''RECEIVE HOST LIST UPDATE TO REMOVE OR ADD A NODE TO LOCAL 'VIEW'''


            # return deleteFile(fileName,hash_list) 
    else:
        j = jsonify(msg='FAIL!!!')
        return (make_response(j,200,{'Content-Type':'application/json'}))  # '''RECEIVE HOST LIST UPDATE TO REMOVE OR ADD A NODE TO LOCAL 'VIEW'''
#debugging code --------------------------------------

def printBloomDicts(bloom_dict):
    dictString = ''
    for key in list(bloom_dict.keys()):
        dictString = dictString +  + key + "\n" + str(bloom_dict.get(key,'None'))
    return dictString


@app.route('/fileCount', methods=['GET'])
def count():
    if request.method == 'GET': 
        return jsonify(count=len(lookup))


@app.route('/throwup', methods=['GET'])
def throwup():
    if request.method == 'GET': 
        return jsonify(lookupCount=len(lookup),bloomCount=len(bloomDict),lookup=lookup,bloomDict=list(bloomDict.keys()))
        # return jsonify(count=len(lookup),lookup=lookup,bloomDict=bloomDict.keys(),bloomPrint=printBloomDicts(bloomDict))# hostlist=hostlist, successor= findSuccessor(ip_port, hostDictionary), lookup=lookup, hash=hashIt(ip_port), ip_port=str(ip_port), hostDictionary=hostDictionary)
#----------------------------------------------------





if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)


   