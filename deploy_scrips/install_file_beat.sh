#!/bin/bash

beattype="$1"
logpath="$2"

if [ "$1" != "" ]; then
    echo "Installing beat for type" $beattype
else
    echo "File beat type not found"
    exit 1
fi

echo "------------------------> Download and install public signing key"
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

echo "------------------------> Install apt-transport-http"
sudo apt-get install apt-transport-https

echo "------------------------> Save repo"
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list

echo "------------------------> Install filebeat"
sudo apt-get update && sudo apt-get install filebeat

echo "------------------------> Remove current log file"
sudo rm $logpath

sudo service filebeat stop

echo "------------------------> Update filebeat yml"
cat > /etc/filebeat/filebeat.yml << EOF
filebeat.prospectors:
- type: log
  enabled: true
  paths:
    - $logpath
  fields: {log_origin: $beattype}

filebeat.config.modules:
  path: /etc/filebeat/modules.d/*.yml
  reload.enabled: false

setup.template.settings:
  index.number_of_shards: 3

setup.kibana:

output.logstash:
  hosts: ["logging.streak.ninja:5046"]
EOF

echo "------------------------> Restart filebeat service"
sudo service filebeat start

echo "------------------------> OK"

