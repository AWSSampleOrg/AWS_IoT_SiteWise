#!/usr/bin/env bash

CURRENT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
mkdir -p ${CURRENT_DIR}/output && cd ${CURRENT_DIR}/output

# Detail Info
# https://docs.aws.amazon.com/iot/latest/developerguide/manage-your-CA-certs.html

#####################################################
# Create a CA certificate
#####################################################
# 1. Generate a key pair.
openssl genrsa -out root_CA_key_filename.key 2048
# 2. Use the private key from the key pair to generate a CA certificate.
## use v3_ca section in openssl.cnf
openssl req -x509 -new -nodes \
    -key root_CA_key_filename.key \
    -sha256 -days 1024 \
    -out root_CA_cert_filename.pem \
    -subj "/CN=example.com" \
    -extensions v3_ca \
    -config ${CURRENT_DIR}/openssl.cnf

#####################################################
# Register a CA certificate in DEFAULT mode (CLI)
#####################################################
# 1. To get a registration code from AWS IoT, use get-registration-code. Save the returned registrationCode to use as the Common Name of the private key verification certificate. For more information, see get-registration-code in the AWS CLI Command Reference.
registration_code=$(aws iot get-registration-code --query registrationCode --output text)
# 2. Generate a key pair for the private key verification certificate:
openssl genrsa -out verification_cert_key_filename.key 2048
# 3. Create a certificate signing request (CSR) for the private key verification certificate. Set the Common Name field of the certificate to the registrationCode returned by get-registration-code.
openssl req -new \
    -key verification_cert_key_filename.key \
    -out verification_cert_csr_filename.csr \
    -subj "/CN=${registration_code}"
# 4. Use the CSR to create a private key verification certificate:
openssl x509 -req \
    -in verification_cert_csr_filename.csr \
    -CA root_CA_cert_filename.pem \
    -CAkey root_CA_key_filename.key \
    -CAcreateserial \
    -out verification_cert_filename.pem \
    -days 500 -sha256
# 5. Register the CA certificate with AWS IoT. Pass in the CA certificate file name and the private key verification certificate file name to the register-ca-certificate command, as follows. For more information, see register-ca-certificate in the AWS CLI Command Reference.
# aws iot register-ca-certificate \
#     --ca-certificate file://root_CA_cert_filename.pem \
#     --verification-cert file://verification_cert_filename.pem \
#     --set-as-active

#####################################################
# AmazonRootCA1.pem
#####################################################
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Finished
cd ${CURRENT_DIR}
