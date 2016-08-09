#!/bin/bash

function stylishEcho(){
        RED="\e[31m"
        BOLD="\e[1m"
        RESET_ALL="\e[0m"
        echo -e "${RED}${BOLD}$1${RESET_ALL}"
}

function easy_ssh(){
        ssh_prefix='ssh -o StrictHostKeyChecking=no'
        host=${1}
        command=${2}

        if [ ! -z "${3}" ]
        then
                ssh_prefix="${ssh_prefix} -i ${3}"
        fi
        ${ssh_prefix} "${host}" "${command}"
}

function easy_scp(){
        scp_prefix='scp -o StrictHostKeyChecking=no -r'
        from=${1}
        to=${2}

        if [ ! -z "${3}" ]
        then
                scp_prefix="${scp_prefix} -i ${3}"
        fi

        ${scp_prefix} ${from} "${to}"
}
