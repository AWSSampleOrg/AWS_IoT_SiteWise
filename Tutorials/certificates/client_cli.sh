#!/usr/bin/env bash

CURRENT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
mkdir -p ${CURRENT_DIR}/output && cd ${CURRENT_DIR}/output

# Detail info
# https://docs.aws.amazon.com/iot/latest/developerguide/create-device-cert.html

#####################################################
# Create a client certificate
#####################################################
# 1. Generate a key pair.
openssl genrsa -out device_cert_key_filename.key 2048
# 2. Create a CSR for the client certificate.
openssl req -new \
    -key device_cert_key_filename.key \
    -out device_cert_csr_filename.csr \
    -subj "/CN=device"
# 3. Create a client certificate from the CSR.
openssl x509 -req \
    -in device_cert_csr_filename.csr \
    -CA root_CA_cert_filename.pem \
    -CAkey root_CA_key_filename.key \
    -CAcreateserial \
    -out device_cert_filename.pem \
    -days 500 -sha256


#####################################################
# Register a client certificate
#####################################################
# aws iot register-certificate \
#     --certificate-pem file://device_cert_filename.pem \
#     --ca-certificate-pem file://root_CA_cert_filename.pem \
#     --set-as-active \
#     --query certificateArn \
#     --output text
