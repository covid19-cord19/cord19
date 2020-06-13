mkdir solr
cd solr
wget https://www.apache.org/dyn/closer.lua/lucene/solr/8.5.0/solr-8.5.0.tgz
tar zxf solr-8.5.0.tgz 
rm -f solr-8.5.0.tgz 
sudo ln -s /opt/solr-8.5.0/ /opt/solr
cd solr
bin/solr status
# Start Solr server
bin/solr start
# Copy confifsets/sample_ config to create covid19 core
cd ./server/solr/configsets/
cp -r sample_techproducts_configs/ ../cores/covid19_dev/
#then browse to solr UI at http://localhost:8983 and create core

