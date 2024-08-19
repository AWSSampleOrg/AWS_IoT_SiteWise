#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

S3_BUCKET=''

STACK_NAME="IoT-Core"
CA_PEM_STRING=$(cat certificates/output/root_CA_cert_filename.pem)
CERTIFICATE_PEM_STRING=$(cat certificates/output/device_cert_filename.pem)
VERIFICATION_CERTIFICATE_PEM_STRING=$(cat certificates/output/verification_cert_filename.pem)

aws cloudformation package \
    --template-file template.yml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged_template.yml

aws cloudformation deploy \
    --template-file packaged_template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    ProjectPrefix="" \
    CACertificatePem="${CA_PEM_STRING}" \
    CertificatePem="${CERTIFICATE_PEM_STRING}" \
    VerificationCertificatePem="${VERIFICATION_CERTIFICATE_PEM_STRING}" \
    --capabilities CAPABILITY_NAMED_IAM
