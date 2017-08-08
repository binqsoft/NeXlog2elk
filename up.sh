sudo chmod -R 777 elasticsearch/esdata/
docker-compose -f docker-compose.yml -f extensions/logspout/logspout-compose.yml up