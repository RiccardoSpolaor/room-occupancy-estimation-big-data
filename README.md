# Room Occupancy Estimation - Big Data Analytics
In this project a multiclassification prediction task is performed with *Spark* the ***Room Occupancy Estimation*** dataset, in order to predict the number of people in a room at a given time given information about sensor data measurements at that time.

The *Room Occupancy Estimation* dataset contains ground truth information about the number of people present in a $6m \times 4.6m$ room over time, varying from $0$ to $3$. Along with it, $16$ sensor data measurements are present at each time step. The measurements are in term of temperature, light, sound, CO2 and digital passive infrared (PIR).

The task of the experiment is to predict the number of people in a room considering the sensor data at the given timestep.

The dataset used in the work is the one presented at the following link: https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation.

The reference paper is available at the following link: https://www.semanticscholar.org/paper/e631ea26f0fd88541f42b4e049d63d6b52d6d3ac.

The Machine Learning methods presented differ from the ones in the reference paper, as *Spark* does not provide all of the presented architectures.

The models used in the experiment are
- Random Forest Classifier
- Logistic Regression
- Naive Bayes
- Multi Layer Perceptron
- Support Vector Machine
- Gradient Boosted Tree

The project has been tested on both a local cluster and *Google Colab*, although the presented results are the run obtained through the latter method.

## Run on Google Colab
In order to run the experiment on Google Colab follow these steps:
1. Open the notebook you want to run on *Google Colab* (e.g.: [`01 Random Forest Classifier.ipynb`](01%20Random%20Forest%20Classifier.ipynb))
2. Start a runtime
3. Navigate to the `./content` folder (The one that automatically opens when you click the `file` icon in the menu)
4. Copy [`utils.py`](utils.py) in `./content`
    - If you are running the [`00 Data Analysis and Splitting.ipynb`](00%20Data%20Analysis%20and%20Splitting.ipynb) notebook:
        1. Create a `./content/input/raw` subfolder
        2. Copy the [`Occupancy_Estimation.csv`](input/raw/Occupancy_Estimation.csv) file in the `./content/input/raw` subfolder
        3. Run the notebook
        4. Save the results obtained in `./content/input/processed`
    - If you are running the [`07 Results.ipynb`](07%20Results.ipynb) notebook:
        1. Copy the subfolders and files presented in the [`results`](results) folder
        3. Run the notebook
    - If you are running any other notebook notebook:
        1. Create a `./content/input/processed` subfolder
        2. Copy the [`train.csv`](input/processed/train.csv) and [`test.csv`](input/processed/test.csv) files in the `./content/input/processed` subfolder
        3. Run the notebook
        4. Save the results obtained in `./content/results`

## Run on a local Hadoop Cluster
### Requirements
-  [Vagrant 2.3.7](https://developer.hashicorp.com/vagrant/install?product_intent=vagrant)      
- [VirtualBox 7.0.6](https://www.virtualbox.org/wiki/Downloads)
- Spark 3.3.1
    - Download [spark-3.3.1-bin-hadoop3.tgz](https://archive.apache.org/dist/spark/spark-3.3.1/) and place it in the root directory

### Set up and run the cluster
Open a *command prompt* or a *Powershell* and run:
```bash
vagrant up --provision
```
This sets up the master and worker nodes.

Afterwards open the master node with:
```bash
vagrant ssh master
```
And run the following commands:
```bash
cd / 
sudo apt install dos2unix
dos2unix /vagrant/scripts/master.sh
sudo /vagrant/scripts/master.sh
exit
```
Now open the worker node with:
```bash
vagrant ssh worker1
```

And run the following commands:
```bash
cd /
dos2unix /vagrant/scripts/worker.sh
sudo /vagrant/scripts/worker.sh
exit
```

Reopen the master node with:
```bash
vagrant ssh master
```
And run the following commands:
```bash
cd /
dos2unix vagrant/scripts/start-dfs-rm.sh
sudo vagrant/scripts/start-dfs-rm.sh
/usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir /spark-logs
```


### Run the clusters if already set up 
Start the master and worker nodes with:
```bash
vagrant up master
vagrant up worker1
```
Afterwards open the master node with:
```bash
vagrant ssh master
```
Run the following commands
```bash
cd /
sudo /vagrant/scripts/start-all.sh
```

### Run the experiment within the cluster
check if the nodes are connected by pasting `192.168.33.10:9870` in a browser.

Make sure you are running the following scripts from the master node, otherwise run the following piece of code to open it:
```bash
vagrant ssh master
```

Start the Spark History Server with:
```bash
sudo su -l ubuntu
sudo /usr/local/spark-3.3.1-bin-hadoop3/sbin/start-history-server.sh
```

Launch jupyter notebook with:
```bash
jupyter notebook --no-browser --ip 0.0.0.0
```
Paste the jupyter url from the CLI in a browser and substitute `master` with `192.168.33.10`.

In the open browser window do the following in the root:
1. Create a `input` folder and the `input/raw` subfolder
2. Copy the [`Room_Occupancy_Count.csv`](input/raw/Room_Occupancy_Count.csv) in the `input/raw` subfolder
3. Copy the [`utils.py`](utils.py) file in the root
4. Copy the notebooks in the root and run them in order

### Stop the cluster
Exit from the master with
```bash
exit
```
Run the following commands:
```bash
vagrant halt master
vagrant halt worker1
```

## Repository structure

    .
    ├── config-files                            # Configuration files for the master and worker nodes.
    ├── input
    |   ├── raw
    |   |   └── Room_Occupancy_Count.csv        # The room occupancy count dataset.
    |   └── processed
    |       ├── test.csv                        # The processed test dataset.
    |       └── train.csv                       # The processed train dataset.
    ├── results                                 # Directory containing the results scores.
    ├── scripts                                 # Configuration scrips to set up the cluster nodes.
    ├── 00 Data Analysis and Splitting.ipynb    # Notebook performing data analysis and trai test split.
    ├── 01 Random Forest Classifier.ipynb       # Notebook to train the Random Forest Classifier.
    ├── 02 Logistic Regression.ipynb            # Notebook to train the Logistic Regression Classifier.
    ├── 03 Naive Bayes.ipynb                    # Notebook to train the Naive Bayes Classifier.
    ├── 04 Multi Layer Perceptron.ipynb         # Notebook to run the Multi Layer Perceptron Classifier.
    ├── 05 Support Vector Machine.ipynb         # Notebook to run the Support Vector Machine Classifier.
    ├── 06 Gradient Boosted Tree.ipynb          # Notebook to run the Gradient Boosted Tree Classifier.
    ├── 07 Results.ipynb                        # Notebook showing the results.
    ├── bootstrap.sh                            # Provisioning file for the virtual machines.
    ├── utils.py                                # Utils functions module.
    ├── .gitattributes
    ├── .gitignore
    ├── LICENSE
    └── README.md

## Versioning

Git is used for versioning.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
