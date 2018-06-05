import math
import hashlib
import os.path

#bit vector object
class BitVector(object):
    def __init__(self, size):
        self.int = 0
        self.size = size
        self.vector = format(self.int,'0'+str(size)+'b')

    def vectorUpdate(self):
        self.vector = format(self.int,'0'+str(self.size)+'b')

    #add function
    def add(self,location):
        if(location < self.size and location > -1):
            self.int |= 1<<location
            print '1 added at %d'%location
            self.vectorUpdate()
            # print('Bit vector add at %d.'%location)
            return 1
        else:
            # print('Bit vector add failed at %d.'%location)
            return 0

    #check certain location in bit vector
    def check(self,location):
        print 'checking at location: %d'%location
        return (self.int >> location) & 1 # test bit 19

    def rebuildVector(self,inputFilter):
        print 'trying to build another filter from a file'
        self.vector = inputFilter
        self.size = len(inputFilter)
        self.int = int(inputFilter,2)

    def __str__(self):
        return "Size: %d\nVector: %s\nInt: %d" %(self.size, self.vector, self.int)

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


    def addToFilter(self,key):
        #key is hashed twice and added to the filter object
        firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        self.filter.add(firstHash)

        self.filter.add(secondHash)

        #increment number of elements within the filter
        self.num_of_elements = self.num_of_elements + 1

        self.updateFilterFile()
        print 'added %s to filter!!!' % key
        # self.extractFilterFromFile()

    def checkFilter(self,key):
        firstHash = int(hashlib.md5(key.encode('UTF-8')).hexdigest(),16) % self.total_bits
        secondHash = int(hashlib.sha1(key.encode('UTF-8')).hexdigest(),16) % self.total_bits

        if(self.filter.check(firstHash) and self.filter.check(secondHash)):
            print 'key: %s is possibly here' % key
        else:
            print 'key: %s is definitely not here' % key

    # update filter file with integer representation
    def updateFilterFile(self):
        #int files
        # bloomFile = open(self.file,'wb')
        # bloomFile.write(str(self.filter.int))
        # bloomFile.close()
        #bit files
        bloomFile = open(self.file,'wb')
        bloomFile.write(str(self.filter.vector))
        print 'filter length: %d'%len(self.filter.vector)

        bloomFile.close()

    # extract filter from file
    def extractFilterFromFile(self,file):
        bloomFile = open(file,'r')
        contents = bloomFile.read()
        self.num_of_hash = 2    #k
        self.total_bits = len(contents) #m
        self.expected_num_of_elements = 100 #n
        self.num_of_elements = 0
        self.filter = BitVector(self.total_bits)
        self.filter.rebuildVector(contents)
        bloomFile.close()        


    def intersection(self,filter2):
        return self.filter.intersection(filter2)




    # def retreiveBloomFilter(self):
    #   print 'retreiveBloomFilter function'
    #   takes in and opens bloom filter file with integer



def main():
    bloomObject = Bloomfilter('bloombaby.txt')
    bloomObject2 = Bloomfilter('bf_keyword.txt')

    # bloomObject.addToFilter('KKKKKKKK')
    # bloomObject.addToFilter('abcd')

    print 'Printing bloomObject:'
    print bloomObject

    print 'Printing bloomObject2:'
    print bloomObject2

    print bloomObject.intersection(bloomObject2.filter.vector)


    # bloomObject3 = Bloomfilter('bloombaby.txt')
    # print bloomObject3
    # bv = BitVector(len(bloomObject.filter.vector))
    # bv.rebuildVector(bloomObject.filter.vector)


    # print bv


    # if(bv.vector == bloomObject.filter.vector):
    #     print 'they equal my dude'

if __name__== "__main__":
    main()

# (1-e-kn/m)k
# (1-e^(-k*n/m))*k
# (1-e^(-2*100/2500))*2
# k = 7
# k = 2 n = 100 ->> m = 288
# 288*8 = 2308 ~ 2500

# k = (m/n)ln(2)
# m = n/ln(2)*k 
# k = (m/n)ln(2) number of hash functions 
# n = number of eleements expected to be inserted
# m = total size and number of bits

# filter is 10x number of elements that will be placed
# bits per entry = 1.44 log2(1/FPP)
# for 0.05 false positive false_positive_rate = 7.62957700783 bits per entry
# 1,000,000 different files on 100 nodes is 10,000 files per 10,000 different words