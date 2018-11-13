#cuckoo
from cuckoopy import CuckooFilter


# class CuckooFilter:
    # self.capacity = capacity
    # self.bucket_size = bucket_size
    # self.fingerprint_size = fingerprint_size
    # self.max_displacements = max_displacements
    # self.buckets = [bucket.Bucket(size=bucket_size)
    #                 for _ in range(self.capacity)]
    # self.size = 0

def toString(self):
    returnString = ""
    for bucket in self.buckets:
        if(len(str(bucket)[10:-2]) < 1):
            returnString += "0,"
        else:
            returnString += str(bucket)[10:-2] + ","


    print ( "return string from to string: " + returnString[:-1])
    print( self.bucket_size)
    print( self.capacity)
    return returnString[:-1]


def fromString(self,cfString):
    print (cfString)
    print ('cfString')
    bucket_list = cfString.split(',')
    print (len(bucket_list))
    for i in range(len(bucket_list)):
        if(int(bucket_list[i]) > 0):
            print (i)
            print ( bucket_list[i])
            self.buckets[i].insert(int(bucket_list[i]))
            self.size = self.size + 1


    # returnString = ""
    # for bucket in self.buckets:
    #     returnString += str(bucket) + ","


def printIt(self):
    print (self.size)
    print (self.size + 1)
    print ('cuckoo!')
    print (self.buckets)


 # .contains
 # .insert
 # .delete
 # .len

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




def main():
    print("Hello World!")
if __name__== "__main__":
    main()
