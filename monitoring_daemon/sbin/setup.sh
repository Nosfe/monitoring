#!/usr/bin/env bash

base_dir=$(readlink -f $(dirname ${0}))
previous_pwd=$(pwd)
cd "${base_dir}/../"

sudo -Hks << EOF
echo "# Installing required packages..."
apt-get update
apt-get -f install
apt-get install -y build-essential python3-pip python3-dev python3-setuptools

echo "# Uninstalling possible conflict files..."
python3 setup.py install --record files.txt
cat files.txt | xargs rm -rf
rm files.txt

echo "# Installing Monitoring Daemon..."
python3 setup.py install
echo "# Done."
EOF



cd ${previous_pwd}


