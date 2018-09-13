from flask import Flask, request, make_response, jsonify

import requests
import os
import sys
import operator
import hashlib

app = Flask(__name__)

# ----------------------------- SETUP ENVIRONMENTAL VARIABLES -------------------------------------
IP_ENV = os.environ.get('ip')      #.get() is a safe way to get values from a dictionary if their key might not exist
VIEW = os.environ.get('VIEW')
ip_port = os.environ.get('ip_port')
num_keywords = os.environ.get('num_keywords')


MAXSIZE = 3000 #note not all nodes will be created because of repeated values due to psuedorandom random function



# ----------------------------- HELPER FUNCTIONS --------------------------------------------------
def hashIt(input1):
    # return abs(hash(str(input1))%MAXSIZE)
    return(abs(int(hashlib.sha224(input1).hexdigest(),16))%MAXSIZE)
    # return abs(hash(str(hash(str(input)))))


# ----------------------------- DIRECTORY FOR ROUTING ---------------------------------------------

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


# '''builds ip:hash(ip) dictionary'''
# def make_ip_hash(hostlist):
#     for host in hostlist:
#         hostDictionary.update({str(host):hashIt(str(host))})        


'''returns sorted list of tuples by hash(ip) values from host dictionary'''
# def sortedDict():
#     global hostDictionary
#     sortedDictionary=sorted(hostDictionary.items(), key=operator.itemgetter(1))
#     print 'hostDictionary sorted is :' + str(sortedDictionary)
#     return sortedDictionary

# '''returns desired host of given key'''
# def findSuccessor(key, dictionaryThing):
#     sortedDictionary=sortedDict()
#     for ip, hashedIP in sortedDictionary: #want to go through dictionary values
#         print 'loop iteration ' 
#         if hashIt(str(key)) < hashedIP:   #comparing hash of the key's string to hashedIP
#             print 'returned ip: '+ str(ip) + ", whose hash is " + str(hashedIP)
#             return str(ip)
#     print 'defaulted: '+str(sortedDictionary[0])
#     return str(sortedDictionary[0][0]) #return the key of the first element in the sorted dictionary

# '''test function: prints key and hash(key) and successor'''
# def testValue(testKey):
#     print "___________________________________________________________________________"
#     hashedKey=hashIt(str(testKey)) #hashes the STRING of the key    
#     print "Our key is " + str(testKey) + ", whose hash is " + str(hashedKey)
#     print "The successor of this key is " + str(findSuccessor(testKey,hostDictionary))


@app.route('/')
def hello_world():
    return 'here is the hashlist' + str(hash_list)

'''key-value GET, PUT, and DELETE Requests'''
@app.route('/data', methods=['GET', 'PUT','DELETE'])
def stuff():
    global lookup
    global hostDictionary
    global hostList
    global hash_list

    if request.method == 'GET':
        return 'this get works'

    # print 'requests text'
    # print request.text
    # print 'json'
    # print request.json()


    if request.method == 'PUT':
        jsonObj = request.get_json(silent=True)
        fileName= jsonObj.get('fileName', None)
        keywords = jsonObj.get('keywords', None)

        if fileName == None or keywords == None:
            j = jsonify(replaced=0, msg='fail', test="key or value undefined", file=keywords)
            return (make_response(j,200,{'Content-Type':'application/json'}))
        # update hash list!
        # print 'valid put request'
        # print hostlist
        # print 'fileName keywords: '
        # print fileName
        # print keywords

        # hash_list = makeHashList(hostlist)
        return addFile(fileName,keywords,hash_list)

    # if request.method == 'GET':
    #     key = request.form.get('key') 
    #     keyOwner = findSuccessor(key, hostDictionary)

    #     if keyOwner == ip_port:
    #         if(key):
    #             if( key in lookup):
    #                 j = jsonify(msg= 'success', value= value, owner= keyOwner)
    #                 return (make_response(j,200,{'Content-Type':'application/json'}))
    #             else:
    #                 j = jsonify(msg='error',error='key does not exist')
    #                 return make_response(j,404,{'Content-Type':'application/json'})
    #         else:
    #             j = jsonify(msg='error',error='key does not exist')
    #             return make_response(j,404,{'Content-Type':'application/json'})
    #     else:
    #         if request.method == 'GET':
    #             key = request.args.get('key')
    #             r = requests.get('http://'+str(keyOwner)+'/kvs?key='+str(key))
    #             return r.text,r.status_code

# '''Returns number of kvs in node'''
# @app.route('/kvs/get_number_of_keys', methods=['GET'])
# def numKeys():
#     return jsonify(count=len(lookup)), 200

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
@app.route('/throwup', methods=['GET'])
def throwup():
    if request.method == 'GET': 
        return jsonify(count=len(lookup),lookup= lookup)# hostlist=hostlist, successor= findSuccessor(ip_port, hostDictionary), lookup=lookup, hash=hashIt(ip_port), ip_port=str(ip_port), hostDictionary=hostDictionary)
#----------------------------------------------------


if __name__ == "__main__":
    #app.run(host=IP_ENV, port=PORT_ENV)
    app.run("0.0.0.0", port=8080)
    # print 'started node'
    # print 'hostlist: ' +str(hostlist)
    # print 'hostDictionary: ' + str(hostDictionary)
    # testValue('10.0.0.4:8080') 


   