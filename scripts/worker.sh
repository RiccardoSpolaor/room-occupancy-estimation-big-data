# downloading dos2unix to convert text files from dos format (with \r\n as newline char)
# to unix format.
sudo apt install dos2unix
echo "switching user to ubuntu"
sudo -i -u ubuntu bash << EOF
# setting master as authorized node for ssh
echo "acquiring ssh key of the master"
cat /vagrant/ssh-keys/id_rsa.pub >> ~/.ssh/authorized_keys
EOF
# delete the line of the hosts file containing the ip associated to "master"
echo "deleting the line containing master in the hosts file"
sed -i '/master/d' /etc/hosts
sed -i '/worker1/d' /etc/hosts

# add the line where we create the alias 'master' for the ip of the master
echo "adding the line about the chosen master ip in the hosts file"
echo '192.168.33.10 master' >> /etc/hosts

# add the line where we create the alias 'worker1' for the ip of the worker1
echo "adding the line about the chosen worker ip in the hosts file"
echo '192.168.33.11 worker1' >> /etc/hosts

# copying hadoop and yarn configuration files
echo "copying configuration files"
dos2unix /vagrant/config-files/core-site.xml
dos2unix /vagrant/config-files/hdfs-site-1.xml
dos2unix /vagrant/config-files/yarn-site-2.xml
dos2unix /vagrant/config-files/mapred-site.xml
dos2unix /vagrant/config-files/workers
cat /vagrant/config-files/core-site.xml > /usr/local/hadoop-3.3.4/etc/hadoop/core-site.xml
cat /vagrant/config-files/hdfs-site-1.xml > /usr/local/hadoop-3.3.4/etc/hadoop/hdfs-site.xml
cat /vagrant/config-files/yarn-site-2.xml > /usr/local/hadoop-3.3.4/etc/hadoop/yarn-site.xml
cat /vagrant/config-files/workers > /usr/local/hadoop-3.3.4/etc/hadoop/workers
cat /vagrant/config-files/workers > /usr/local/hadoop-3.3.4/etc/hadoop/workers
cat /vagrant/config-files/mapred-site.xml > /usr/local/hadoop-3.3.4/etc/hadoop/mapred-site.xml

