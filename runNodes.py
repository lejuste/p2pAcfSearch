# python run program
import os

def portBuilder(port_itter):
	return str(8000+port_itter) + ":8080"

def ipBuilder(ip_itter):
	return "10.0.0." + str(ip_itter)

def viewBuilder(nodes):
	view = "VIEW=\""
	for i in range(2,nodes+2):
		view += "10.0.0." + str(i) + ":8080,"
	return view.rstrip(",") + "\""

def ip_portBuilder(ip_itter):
	return "ip_port=\"10.0.0." + str(ip_itter) + ":8080\""

def docker_run(number_of_nodes,detached,run_nodes):
	view = viewBuilder(number_of_nodes)
	for i in range(2,number_of_nodes +2):
		if(detached):
			bashCommand = "docker run -d -p " + portBuilder(i) + " --net=mynet --ip=" + ipBuilder(i) + " -e " + view + " -e " + ip_portBuilder(i) + " kvs"
		else:
			bashCommand = "docker run -p " + portBuilder(i) + " --net=mynet --ip=" + ipBuilder(i) + " -e " + view + " -e " + ip_portBuilder(i) + " kvs"
		print ">>>>>>>>>>"+bashCommand
		os.system(bashCommand)
		# if(i+1 >run_nodes+2):
		# 	break

def rm_containers():
	os.system("docker rm -f $(docker ps -a -q)")

def build_kvs():
	os.system("docker build -t kvs .")

def main():

	rm_containers()
	build_kvs()
	docker_run(20,True,20)

if __name__== "__main__":
    main()