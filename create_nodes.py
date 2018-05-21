import os
import sys
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

#settings:
SIZE = nnodes #note not all nodes will be created because of repeated values due to psuedorandom random function

class Address(object):
	def __init__(self, ip, port):
		self.ip = ip
		self.port = int(port)
		self.hash = 0
		self.id = "%s:%s" % (self.ip,self.port)

	def __hash__(self):
		self.hash = hash(self.id) % SIZE
		# return hash(("%s:%s" % (self.ip, self.port))) % SIZE
		return hash(self.id) % SIZE


	def __cmp__(self, other):
		return other.__hash__() < self.__hash__()

	def __eq__(self, other):
		return other.__hash__() == self.__hash__()

	def __str__(self):
		return "[\"%s\", \"%s\", %s, %s]" % (self.id, self.ip, self.port, self.hash)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def main():


	print "Creating chord network with : %s nodes" % nnodes

	# create ip, port lists
	port_list = []
	ip_list = []
	for x in range(nnodes):
		ip_list.append(str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)) + '.' + str(random.randrange(0,255)))
		port_list.append(random.randrange(1, 65535))


	address_list = map(lambda (ip, port): Address(ip, port), zip(ip_list, port_list))
	# hash_list 	 = map(lambda addr: addr.__hash__(), address_list.id)

	# keep unique ones
	address_list = sorted(set(address_list))
	print "final number of addresses : %s" % len(address_list)


	createFolder('nodes/')
	for x in range(len(address_list)):
		createFolder('nodes/'+(address_list[x].id+'/'))


	# add keys into files?
	# plotlist = []
	# for x in range(len(address_list)):
	# 	plotlist.append(address_list[x].hash)

	# print address_list[0]
	# print address_list[0].hash

	# plt.plot(plotlist, 'ro')
	# plt.ylabel('some numbers')
	# plt.show()



	# print hash_list[0]
  
if __name__== "__main__":
  main()


