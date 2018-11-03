echo starting mynet images

docker network rm mynet
docker network create   \
--subnet=10.0.0.0/24 \
mynet