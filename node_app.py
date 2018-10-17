from flask import Flask, request, make_response, jsonify

import requests
import os
import sys
import operator
import hashlib
from bloom_modified import Bloomfilter
import time

app = Flask(__name__)

# ----------------------------- SETUP ENVIRONMENTAL VARIABLES -------------------------------------
IP_ENV = os.environ.get('ip')      #.get() is a safe way to get values from a dictionary if their key might not exist
VIEW = os.environ.get('VIEW')
ip_port = os.environ.get('ip_port')
num_keywords = os.environ.get('num_keywords')


MAXSIZE = 3000 #note not all nodes will be created because of repeated values due to psuedorandom random function
bloomDict = dict()

lastBloomCheck = False

# ----------------------------- HELPER FUNCTIONS --------------------------------------------------
def hashIt(input1):
    # return abs(hash(str(input1))%MAXSIZE)
    # dont do an int to eliminate 
    # return(abs(int(hashlib.sha224(input1).hexdigest(),16)))
    return(abs(int(hashlib.sha224(input1).hexdigest(),16))%MAXSIZE)
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
        print 'results:'
        print theFilter.checkFilter(keyword)
        print 'end of results'
        return theFilter.checkFilter(keyword)
    else:
        return 0

def getKeywordFilter(keyword):
    return bloomDict.get(keyword, 0)

def bloomItemIntersection(filter1,filter2):
    return filter1 & filter2


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
            print 'hashlist ' + str(hash_list)
            print 'file_hash ' + str(file_hash) 
            return str(hash_list[i][1])
    print 'hashlist ' + str(hash_list)
    print 'file_hash ' + str(file_hash)                    
    return str(hash_list[0][1])
    #check for null then set to first indicie


# INPUT: keywords - tags for the given file
#        hashlist - tuple list of hash(ip:port),ip:port
#        fileName - file name / file data
# OUTPUT: node number in hashlist for 

# Find the immediate successor to a file/keyword given a list of nodes
def addFile(fileName,keywords,hash_list):
    global ip_port
    print 'add file is called.'
    fileLocations = []
    perfectHit = True
    data = []
    for keyword in keywords:
 
        fileLocation = findOwner(keyword,hash_list)

        if fileLocation == ip_port:
            print 'SAVING ' + str(fileName) + ' to ' + fileLocation + ' for ' + keyword
            data = lookup.get(fileName, [])
            data.append(keyword)
            lookup[fileName] = data
            bloomItemAdd(keyword,fileName)
        else:
            fileLocations.append(fileLocation)
            perfectHit = False

    for i in range(len(fileLocations)):
        payload = {'fileName': fileName, 'keywords':[keywords[i]]}
        print 'FORWARDING ' + str(payload) + ' to ' + 'http://'+fileLocations[i]+'/data'
        r = requests.put('http://'+fileLocations[i]+'/data', json = payload)        

    if perfectHit:
        j = jsonify(msg='success', owner=fileLocation, file=fileName, keywords = keywords )
        return (make_response(j,200,{'Content-Type':'application/json'}))                
    else:
        return (make_response(r.text,r.status_code,{'Content-Type':'application/json'}))  


# INPUT: node,ip - node ip address and port
#        keyword - keyword to search for on the node
# OUTPUT: a list of the file names

# Find the immediate successor to a file/keyword given a list of nodes
def getFileNamesForKeyword(keyword):
    global lookup
    global ip_port
    print 'getFiles at Node ' + ip_port + '\nkeyword'
    print keyword
    print 'kvs'
    print kvs

    files = []

    for fileName in lookup:
        keywords = lookup.get(fileName, [])
        print 'keywords: ' + keywords + ' in ' + fileName
        for tag in keywords:
            if(keyword == tag):
                files.append(fileName)
    return list(set(files))


def search_keywords(keywords,hash_list,searchType):
    print 'keywords'
    print keywords
    print 'hash_list'
    print hash_list

    if len(keywords) == 0:
        j = jsonify(msg='no keywords', files=[], keywords = keywords)
        return (make_response(j,200,{'Content-Type':'application/json'}))  

    # THROUGHPUT SEARCH NEEDS TO SEND THE NEWLY CREATED FILTERS
    # send filter filter filter filter then filenames once

    # must forward: startTime(),remaining keywords,currentFilter

    startTime = time.time()
    print 'start time: ' + startTime
    nodeFilter = 0
    remainingKeywords = []


    for keyword in keywords:
 
        fileLocation = findOwner(keyword,hash_list)
        if fileLocation == ip_port:
            filterObject = getKeywordFilter(keyword)
            bitVector = filterObject.getBitVector()

            j = jsonify(msg='success', keywordFound = keyword, bitVector=bitVector)
            return (make_response(j,200,{'Content-Type':'application/json'}))    
            # get filter for the word and start building the filter
        else:
            remainingKeywords.append(keyword)

        j = jsonify(msg='success', keywordNotFound = str(remainingKeywords))
        return (make_response(j,200,{'Content-Type':'application/json'}))  

    # if(len(remainingKeywords) > 1):
    #     nextNode = findOwner(remainingKeywords[0],hash_list)
    #     # create filter
    #     #forward to a node

    #     # wait for response
    #     # return response!!!
    # else:
    #     totalTime = time.time() - startTime

    #     # get fileNames on local node that are associated with the filter fileNames[]


    #     j = jsonify(msg='success', totalTime = totalTime, files=fileNames,)
    #     return (make_response(j,200,{'Content-Type':'application/json'}))     


'''builds ip:hash(ip) dictionary'''
def make_ip_hash(hostlist):
    for host in hostlist:
        hostDictionary.update({str(host):hashIt(str(host))})        

'''test function: prints key and hash(key) and successor'''
def testValue(testKey):
    print "___________________________________________________________________________"
    hashedKey=hashIt(str(testKey)) #hashes the STRING of the key    
    print "Our key is " + str(testKey) + ", whose hash is " + str(hashedKey)
    print "The successor of this key is " + str(findSuccessor(testKey,hostDictionary))


# @app.route('/internalSearch', methods=['GET', 'PUT','DELETE'])
# def searchNoAPI():
#     if request.method == 'PUT':
#         jsonObj = request.get_json(silent=True)

#     return 'here is the hashlist' + str(hash_list)

@app.route('/')
def hello_world():
    return 'here is the hashlist' + str(hash_list)




@app.route('/search', methods=['GET', 'PUT','DELETE'])
def searchMethod():
    global lookup
    global hostDictionary
    global hostList
    global hash_list

    if request.method == 'PUT':
        jsonObj = request.get_json(silent=True)
        keywords = jsonObj.get('keywords', None)

        if keywords == None:
            j = jsonify(replaced=0, msg='fail', test="keys undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
    
        j = jsonify(replaced=0, msg='keywords valid', keywords=str(keywords))
        return (make_response(j,200,{'Content-Type':'application/json'}))


        return search_keywords(query,hash_list,'explicit')




'''key-value GET, PUT, and DELETE Requests'''
@app.route('/data', methods=['GET', 'PUT','POST','DELETE'])
def stuff():
    global lookup
    global hostDictionary
    global hostList
    global hash_list

    # if request.method == 'POST':
    #     jsonObj = request.get_json(silent=True)
    #     keywords = jsonObj.get('keywords', None)

    #     if keywords == None:
    #         j = jsonify(replaced=0, msg='fail', test="keys undefined")
    #         return (make_response(j,200,{'Content-Type':'application/json'}))
    
    #     j = jsonify(replaced=0, msg='keywords valid', keywords=str(keywords))
    #     return (make_response(j,200,{'Content-Type':'application/json'}))


    #     return search_keywords(query,hash_list,'explicit')


    # print 'requests text'
    # print request.text
    # print 'json'
    # print request.json()


    if request.method == 'PUT':
        jsonObj = request.get_json(silent=True)
        fileName= jsonObj.get('fileName', None)
        keywords = jsonObj.get('keywords', None)

        if fileName == None or keywords == None:
            j = jsonify(replaced=0, msg='fail', test="filename or keywords undefined")
            return (make_response(j,200,{'Content-Type':'application/json'}))
        # update hash list!
        # print 'valid put request'
        # print hostlist
        # print 'fileName keywords: '
        # print fileName
        # print keywords

        # hash_list = makeHashList(hostlist)
        return addFile(fileName,keywords,hash_list)


# '''RECEIVE HOST LIST UPDATE TO REMOVE OR ADD A NODE TO LOCAL 'VIEW'''
# @app.route('/kvs/update_hostlist', methods=['PUT'])
# def hostList_update():
#     if request.method == 'PUT':

#         request_ipPort = request.form.get('input_host')
#         request_type = request.form.get('request_type')
#         global hostDictionary

#         if(request_type == 'add'):
#             # add new host to local local directory
#             if (request_ipPort not in hostlist):
#                 hostlist.append(str(request_ipPort))
#                 hostDictionary = dict((host,abs(hash(host))) for host in hostlist)
#                 #hostDictionary = make_ip_hash(hostlist)
                
#         elif(request_type == 'remove'):
#             #removes new host from local directory
#             if(request_ipPort in hostlist):
#                 hostlist.remove(str(request_ipPort))
#                 hostDictionary = dict((host,abs(hash(host))) for host in hostlist)

#         j = jsonify(msg='success',hostDictionary=str(list(hostDictionary.keys())),hostList=str(hostlist),lastHost=request_ipPort,request_type=request_type)
#         return (make_response(j,200,{'Content-Type':'application/json'}))

# #adding/deleting nodes -------------------------------
# @app.route('/kvs/view_update', methods=['PUT'])
# def viewUpdate():
#     global hostDictionary
#     if request.method == 'PUT':   

#         # parse request form
#         request_ipPort = request.form.get('ip_port') 
#         request_type = request.form.get('type')
#         forwardedIP_port = request.form.get('forwardedIP_port')
        

#         if request_type == 'add':
#             # check if new ip is in hostDictionary   
            
#             #Determine who is the successor of the new node.
#             successor = findSuccessor(request_ipPort, hostDictionary)


#             if successor == ip_port: #We are the successor of the incoming node
#                 #add node to local hostDictionary
#                 hostlist.append(str(request_ipPort))
#                 hostDictionary[str(request_ipPort)] = hashIt(str(request_ipPort))

#                 #update the new node's hostlist with existing IP's
#                 for host in list(hostDictionary.keys()):
#                     #put request to new node
#                     if host == request_ipPort:
#                         continue
#                     r = requests.put('http://'+str(request_ipPort)+'/kvs/update_hostlist',data = {'input_host':str(host),'request_type':'add'})

#                 # send all keys that belong to the new node to the new node
#                 i = 0
#                 for key in lookup.keys():
#                     if (hashIt(str(key)) < hashIt(str(request_ipPort))): #does key belong at new node?
#                         i = i + 1
#                         #add key to new node, delete key from old node
#                         r = requests.put('http://'+str(request_ipPort)+'/kvs', data = {'key':str(key),'value':lookup[key]})
#                         lookup.pop(key, None) 
#                         if(i > 100):
#                             break

#                 #broadcast: send put request with new node info to all nodes EXCEPT new node, forwarding node, and successor
#                 for host in list(hostDictionary.keys()):            
#                     if ((host == request_ipPort) or (host == ip_port) or (host == forwardedIP_port)):      
#                         pass
#                     else:
#                         r = requests.put('http://'+str(host)+'/kvs/update_hostlist',data = {'input_host':str(request_ipPort),'request_type':'add'})

    
#                 ##########wait for confirmation###########

#                 j = jsonify(msg= 'success', text=str(r.text),statusCode=str(r.status_code))
#                 return (make_response(j,200,{'Content-Type':'application/json'}))

#             else:   #not successor node (forward request to successor)
#                 r = requests.put('http://'+str(successor)+'/kvs/view_update', data={'ip_port':str(request_ipPort), 'type':'add', 'forwardedIP_port':str(ip_port)})
            
#                 hostlist.append(str(request_ipPort))
#                 hostDictionary[str(request_ipPort)] = hashIt(str(request_ipPort))
#                 j = jsonify(msg='success', hostDict= str(hostDictionary.keys()))
#                 return (make_response(j,200,{'Content-Type':'application/json'}))

#         elif request_type == 'remove':
#             #check if we are the node to be deleted
#             if request_ipPort == ip_port:
#                 hostDictionary.pop(str(ip_port))
                
#                 # j = jsonify(msg="success", ip_port=ip_port)
#                 # return (make_response(j,200,{'Content-Type':'application/json'}))
                
#                 successor = findSuccessor(ip_port, hostDictionary)

#                 j = jsonify(msg="success", ip_port=ip_port)
#                 return (make_response(j,200,{'Content-Type':'application/json'}))

#                 for key in lookup.keys():
#                     r = requests.put('http://'+str(successor)+'/kvs', data ={'key':str(key), 'value':str(lookup[key])})

#                 j = jsonify(msg="success", ip_port=ip_port)
#                 return (make_response(j,200,{'Content-Type':'application/json'}))
#             else:
#                 #forward to node to be deleted
#                 r = requests.put('http://'+request_ipPort+'/kvs/view_update', data={'ip_port':str(request_ipPort), 'type':'remove', 'forwardedIP_port':str(ip_port)})
#                 hostDictionary.pop(str(request_ipPort),None)
#                 hostlist.remove(str(request_ipPort))

#                 #tell everyone to remove node from hostlist
#                 for host in list(hostDictionary.keys()):
#                     if (host==ip_port):
#                         continue
#                     r = requests.put('http://'+str(host)+'/kvs/update_hostlist',data = {'input_host':str(request_ipPort),'request_type':'remove'})

#                 j = jsonify(msg='success', json=r.json())
#                 return (make_response(j,200,{'Content-Type':'application/json'}))     

#debugging code --------------------------------------

def printBloomDicts(bloom_dict):
    dictString = ''
    for key in bloom_dict.keys():
        dictString = dictString +  + key + "\n" + str(bloom_dict.get(key,'None'))
    return dictString


@app.route('/throwup', methods=['GET'])
def throwup():
    if request.method == 'GET': 
        return jsonify(count=len(lookup),lookup=lookup,bloomDict=bloomDict.keys())
        return jsonify(count=len(lookup),lookup=lookup,bloomDict=bloomDict.keys(),bloomPrint=printBloomDicts(bloomDict))# hostlist=hostlist, successor= findSuccessor(ip_port, hostDictionary), lookup=lookup, hash=hashIt(ip_port), ip_port=str(ip_port), hostDictionary=hostDictionary)
#----------------------------------------------------





if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)


   