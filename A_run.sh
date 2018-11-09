echo "REMOVING ALL CONTAINERS"
docker rm -f $(docker ps -a -q)

echo "BUILDING IMAGE"
docker build -t kvs .


docker run -p 8002:8080 --net=mynet --ip=10.0.0.2 -e VIEW="10.0.0.2:8080,10.0.0.3:8080,10.0.0.4:8080" -e ip_port="10.0.0.2:8080" kvs
# docker run -p 8081:8080 --net=mynet --ip=10.0.0.20 -e VIEW="10.0.0.20:8080" -e "ip_port"="10.0.0.20:8080" kvs
# docker run -p 8081:8080 --net=mynet --ip=10.0.0.20 -e VIEW="10.0.0.20:8080,10.0.0.21:8080,10.0.0.10:8080" -e ip_port="10.0.0.20:8080" kvs