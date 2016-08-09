#!/bin/bash
set -e
base_dir=$(readlink -f $(dirname ${0}))
source "${base_dir}/utils.sh"

function deploy_on_host(){
    hostname="${2}@${1}"
    ssh_key="${3}"

    if $(easy_ssh "${hostname}" "ls" "${ssh_key}" &> /dev/null)
    then
        stylishEcho "#     Deploying on host ${hostname}..."
        easy_ssh "${hostname}" "sudo rm -rf monitoring_daemon*" "${ssh_key}"
        easy_scp "dist/${sdist_filename}.tar.gz" "${hostname}:" "${ssh_key}"
        easy_ssh "${hostname}" "tar -zxf ${sdist_filename}.tar.gz && rm ${sdist_filename}.tar.gz; bash ${sdist_filename}/sbin/setup.sh" "${ssh_key}"
    else
        stylishEcho "#     Host ${hostname} not found!"
    fi
}

if [ -z ${1} ]
then
    stylishEcho "# ERROR: Missing argument."
    stylishEcho "#     Usage: ${0} <hosts-file>"
    exit -1
fi

previous_pwd=$(pwd)
cd "${base_dir}/../../"

stylishEcho "# Installing required packages..."
sudo -ks << EOF
apt-get update
apt-get -f install
apt-get install -y python3-setuptools
EOF

stylishEcho "# Creating distribution of Monitoring Daemon..."
python3 setup.py sdist
for file in $(ls "dist/")
do
    if [ $(echo "${file}" | grep ".tar.gz") ]
    then
        sdist_filename="$(echo "${file}" | sed -e 's/.tar.gz//')"
        break
    fi
done

stylishEcho "# Deploying on hosts taken from ${1}..."
while read -r line || [[ -n "${line}" ]]
do
    declare -A host_information # declare an associative array
    host_information=()
    for word in ${line}
    do
        IFS='=' read -ra fields <<< "${word}"
        field_name="$(echo -e "${fields[0]}")"
        # trim  the leading and trailing spaces
        field_value="$(echo -e "${fields[1]}" | sed -e 's/"//g')"
        host_information+=([${field_name}]=${field_value})
    done

    deploy_on_host "${host_information[name]}" "${host_information[user]}" "${host_information[ssh_key]}" &

done < "${1}"
wait
stylishEcho "# Installation Completed!"
cd ${previous_pwd}
