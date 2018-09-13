# p2pAcfSearch
Using Adaptive Cuckoo filters for p2p keyword search

Programs:
pie.py -- Generates dynamic data file
create_nodes.py -- creates large set of nodes

node_app.py -- Flask application for each node within the network



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


DOCKER EXAMPLE RUN:
  ./A_run.sh in one node
  ./B_run.sh in another node



  PUT to localhost:8081/data with 
    {
    "fileName":"Johnny",
    "keywords":[ "Honda", "Toyota", "Kia" ]
    }

  PUT to localhost:8038/data with 
    {
    "fileName":"John",
    "keywords":[ "Ford", "BMW", "Fiat" ]
    }



  GET  to localhost:8038/throwup should show:
  {
    "count": 2,
    "lookup": {
        "John": [
            "Fiat"
        ],
        "Johnny": [
            "Honda",
            "Toyota",
            "Kia"
        ]
    }
  }

  GET  to localhost:8081/throwup should show:
  {
      "count": 1,
      "lookup": {
          "John": [
              "Ford",
              "BMW"
          ]
      }
  }

