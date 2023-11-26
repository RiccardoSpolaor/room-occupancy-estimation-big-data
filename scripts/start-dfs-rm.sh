# quick check if the worker is reachable
sudo -i -u ubuntu bash << EOF
ssh worker1
exit
echo "connection with the worker established"
echo "ssh out of the worker"
EOF

sudo -i -u ubuntu bash << EOF
echo "now in ubuntu"
echo "removing previously created hdfs"
sudo rm -r ~/hdfs
EOF

echo "creating a brand new hdfs"
sudo /usr/local/hadoop-3.3.4/bin/hdfs namenode -format

echo "starting dfs and yarn"
sudo /usr/local/hadoop-3.3.4/sbin/start-dfs.sh
sudo /usr/local/hadoop-3.3.4/sbin/start-yarn.sh


if ! grep -q 'localhost	127.0.0.1' /etc/hosts; then
	sudo sed -i '1i localhost	127.0.0.1' /etc/hosts
	echo 'added localhost line in /etc/hosts'
fi

# log into ubuntu with sudo su -l ubuntu and run these two commands:
# /usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir /spark-logs
# sudo /usr/local/spark-3.3.1-bin-hadoop3/sbin/start-history-server.sh
# jupyter notebook --no-browser --ip 0.0.0.0