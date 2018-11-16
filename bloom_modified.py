import math
import hashlib
import os.path
import os


#bit vector object
class BitVector(object):
    def __init__(self, size = 20000):
        self.int = 0
        self.size = size
        self.vector = format(self.int,'0'+str(size)+'b')

    def __str__(self):
        return "Size: %d\nVector: %s\nInt: %d" %(self.size, self.vector, self.int)

    def vectorUpdate(self):
        self.vector = format(self.int,'0'+str(self.size)+'b')

    #add function
    def add(self,location):
        if(location < self.size and location > -1):
            self.int |= 1<<location
            print('1 added at %d'%location)
            self.vectorUpdate()
            # print('Bit vector add at %d.'%location)
            return 1
        else:
            # print('Bit vector add failed at %d.'%location)
            return 0

    #check certain location in bit vector
    def check(self,location):
        print('checking at location: %d'%location)
        return (self.int >> location) & 1 # test bit 19

    #refiles bit vector object from input strine
    def rebuildVector(self,inputFilter):
        # print 'trying to build another filter from a file'
        self.vector = inputFilter
        self.size = len(inputFilter)
        self.int = int(inputFilter,2)

    #returns filter intersection with input string
    def intersection(self,filter2):
        if(len(self.vector) != len(filter2)):
            return 'error files are not of equal length'
        else:
            andFilter = ''
            for i in range(0,len(self.vector)):
                if(self.vector[i] == '1' and filter2[i] == '1'):
                    andFilter = andFilter + '1'
                else:
                    andFilter = andFilter + '0'
            return andFilter

    def bitwiseOr(self,filter2):
        if(len(self.vector) != len(filter2)):
            print('error files are not of equal length, vector len: ' + len(self.vector) + ' filter2 length: ' + len(filter2))
        else:
            orFilter = ''
            for i in range(0,len(self.vector)):
                if(self.vector[i] == '1' or filter2[i] == '1'):
                    orFilter = orFilter + '1'
                else:
                    orFilter = orFilter + '0'
            self.vector = orFilter
            self.int = int(orFilter,2)


    #default: k = 2
    #default: total _bits = 2500
    #hashes availible: md5,sha1,sha224,sha256,sha384,sha512

class Bloomfilter(object):
    def __init__(self,intRep = 0):
        self.num_of_hash = 2    #k
        self.total_bits = 20000  #m
        self.expected_num_of_elements = 100 #n
        self.num_of_elements = 0
        # self.false_positive_rate = (1-math.exp(-self.num_of_hash*self.expected_num_of_elements/self.total_bits))*self.num_of_hash,
        self.filter = BitVector(self.total_bits)


    def __str__(self):
        return "filter: %s\n" %(self.filter)

        # return "num_of_hash: %d\ntotal_bits: %d\nexpected_num_of_elements: %d\nfilter: %s\n" %(self.num_of_hash, self.total_bits, self.expected_num_of_elements, self.filter)

    def getBitVector(self):
        return self.filter.vector

    def filterUpdate(self,string_vector):
        self.filter.rebuildVector(string_vector)

    def addToFilter(self,key):
        #key is hashed twice and added to the filter object
        firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        self.filter.add(firstHash)

        self.filter.add(secondHash)

        #increment number of elements within the filter
        self.num_of_elements = self.num_of_elements + 1

        # self.updateFilterFile()
        print('added %s to filter!!!' % key)

    def checkFilter(self,key):
        firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits

        if(self.filter.check(firstHash) and self.filter.check(secondHash)):
            print('key: %s is possibly here' % key)
            return True
        else:
            print('key: %s is definitely not here' % key)
            return False

    # super class intersection on sub-objet for intersection   
    def intersection(self,filter2):
        return self.filter.intersection(filter2)

    def removeElementFromFilter(self):
        self.updateFilterFile()


def main():

    #tester code for bloom object
    bloomObject = Bloomfilter('bloombaby.txt')
    bloomObject2 = Bloomfilter('bf_keyword.txt')

    # bloomObject.addToFilter('KKKKKKKK')
    # bloomObject.addToFilter('abcd')

    print('Printing bloomObject:')
    print(bloomObject)

    print('Printing bloomObject2:')
    print(bloomObject2)

    print(bloomObject.intersection(bloomObject2.filter.vector))

    print('removing element from the filter')

    bloomObject.removeElementFromFilter()



if __name__== "__main__":
    main()



