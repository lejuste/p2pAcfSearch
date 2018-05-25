# p2pAcfSearch
Using Adaptive Cuckoo filters for p2p keyword search

Programs:
pie.py -- Generates dynamic data file
create_nodes.py -- creates large set of nodes




File: pie.py
Usage: pie.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILES, --files=FILES
                        number of files for the system
  -k KEYS, --keywords=KEYS
                        keywords per file
  -o OUTPUT, --output=OUTPUT
                        output file to save data
  -i INPUT, --input=INPUT
                        input file for a list of keyword options

EXAMPLE RUN:
	python pie.py -f 1000000 -k 6
  
  creates f files with k keywords. 



File create_nodes.py
Usage: create_nodes.py [options]

Options:
  -h, --help            show this help message and exit
  -n NODES, --nodes=NODES
                        number of nodes created within the system
  -i INPUT, --input=INPUT
                        data file for data store
  -f FILEAMOUNT, --files=FILEAMOUNT
                        number of files to initially add to the network


EXAMPLE RUN:
  python create_nodes.py -n 10 -i data1.csv -f 3	

  makes n nodes and stores f files from the input data (i)
