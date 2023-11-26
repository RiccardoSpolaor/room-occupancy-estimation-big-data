sudo /usr/local/hadoop-3.3.4/sbin/start-dfs.sh
sudo /usr/local/hadoop-3.3.4/sbin/start-yarn.sh

if ! grep -q 'localhost	127.0.0.1' /etc/hosts; then
	sudo sed -i '1i localhost	127.0.0.1' /etc/hosts
	echo 'added localhost line in /etc/hosts'
fi

# log into ubuntu with sudo su -l ubuntu and run these two commands:
# sudo /usr/local/spark-3.3.1-bin-hadoop3/sbin/start-history-server.sh
# jupyter notebook --no-browser --ip 0.0.0.0