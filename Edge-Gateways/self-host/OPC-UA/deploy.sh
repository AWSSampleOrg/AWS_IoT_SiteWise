#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

STACK_NAME="IoT-SiteWise-Edge-OPC-UA"

aws cloudformation deploy \
    --template-file template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    ProjectPrefix="" \
    --capabilities CAPABILITY_NAMED_IAM
