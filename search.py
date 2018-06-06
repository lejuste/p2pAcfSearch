from create_nodes import findOwner
#search on the nodes!!


#lets create a search
def search_keywords(query):
	keywords_list = query.split(" ")
	print keywords_list   

	#find a list of nodes with following keywords

	for key in keywords_list:
        x = int(findOwner(key,hash_list))
        print 'node %s has files with keyword %s '% str(hash_list[x][1]), key


def main():
	keywords = raw_input("Which keywords are you looking for associated with files?")
	search_keywords(keywords)

if __name__== "__main__":
    main()

    # bloomObject3 = Bloomfilter('bloombaby.txt')
    # print bloomObject3
    # bv = BitVector(len(bloomObject.filter.vector))
    # bv.rebuildVector(bloomObject.filter.vector)


    # print bv


    # if(bv.vector == bloomObject.filter.vector):
    #     print 'they equal my dude'




# 	hash the keywords:
# 		create list of nodes you should talk to.

# 	loop around to each node:

# 		contact first ndoe to start the search

# 		check the 



# #oracle node:
# #creates a client request



# 	talk on that list to get an intersection of all files?

# 	F(a)->node b

# 	node b returns file names to a

# 	node a<-F(a)n node b

# 	node a has a filter that is sent to node b.

# #check a bunch of 

# #start from a like a total alias call on the entire system


# #check for a



# #main:

# search for some set of keywords search for some keywords :)
# returns the file names at some certain nodes
# returns the 


