#cuckoo
import math
import hashlib
import os.path
from bloom import BitVector

#bit vector object
class BitVector(object):
    def __str__(self):
        return "Size: %d\nVector: %s\nInt: %d" %(self.size, self.vector, self.int)
    def vectorUpdate(self):
    #add function
    def add(self,location):
    #check certain location in bit vector
    def check(self,location):
    #refiles bit vector object from input strine
    def rebuildVector(self,inputFilter):
    #returns filter intersection with input string
    def intersection(self,filter2):



    #default: k = 2
    #default: total _bits = 2500
    #hashes availible: md5,sha1,sha224,sha256,sha384,sha512
class Bloomfilter(object):
    #if file is defined make make the filter from the file!!!!
    #else create a new file
    def __init__(self,file,k=2):
        self.num_of_hash = 2    #k
        self.total_bits = 2500  #m
        self.expected_num_of_elements = 100 #n
        self.num_of_elements = 0
        # self.false_positive_rate = (1-math.exp(-self.num_of_hash*self.expected_num_of_elements/self.total_bits))*self.num_of_hash,
        self.filter = BitVector(self.total_bits)
        self.file = file

        if(os.path.exists(file)):
            self.extractFilterFromFile(file)
        else:
            self.updateFilterFile()

    def __str__(self):
        return "num_of_hash: %d\ntotal_bits: %d\nexpected_num_of_elements: %d\nfilter: %s\nfile: %s\n" %(self.num_of_hash, self.total_bits, self.expected_num_of_elements, self.filter, self.file)

    #adds new key to filter
    def addToFilter(self,key):
        #key is hashed twice and added to the filter object
        # firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        # secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        # self.filter.add(firstHash)
        # self.filter.add(secondHash)
        # #increment number of elements within the filter
        # self.num_of_elements = self.num_of_elements + 1
        # self.updateFilterFile()
        # print 'added %s to filter!!!' % key

    # hashes key and checks if key is within the file
    def checkFilter(self,key):
        # firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        # secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        # if(self.filter.check(firstHash) and self.filter.check(secondHash)):
        #     print 'key: %s is possibly here' % key
        #     return 1
        # else:
        #     print 'key: %s is definitely not here' % key
        #     return 0

    # update filter file with integer representation
    def updateFilterFile(self):
        #int files
        # bloomFile = open(self.file,'wb')
        # bloomFile.write(str(self.filter.int))
        # bloomFile.close()
        #bit files
        # bloomFile = open(self.file,'wb')
        # bloomFile.write(str(self.filter.vector))
        # print 'filter length: %d'%len(self.filter.vector)
        # bloomFile.close()

    # extract filter from file
    def extractFilterFromFile(self,file):
        # bloomFile = open(file,'r')
        # contents = bloomFile.read()
        # self.num_of_hash = 2    #k
        # self.total_bits = len(contents) #m
        # self.expected_num_of_elements = 100 #n
        # self.num_of_elements = 0
        # self.filter = BitVector(self.total_bits)
        # self.filter.rebuildVector(contents)
        # bloomFile.close()        


    # super class intersection on sub-objet for intersection   
    def intersection(self,filter2):
        # return self.filter.intersection(filter2)


def main():

    #tester code for bloom object
    # bloomObject = Bloomfilter('bloombaby.txt')
    # bloomObject2 = Bloomfilter('bf_keyword.txt')

    # # bloomObject.addToFilter('KKKKKKKK')
    # # bloomObject.addToFilter('abcd')

    # print 'Printing bloomObject:'
    # print bloomObject

    # print 'Printing bloomObject2:'
    # print bloomObject2

    # print bloomObject.intersection(bloomObject2.filter.vector)


if __name__== "__main__":
    main()
