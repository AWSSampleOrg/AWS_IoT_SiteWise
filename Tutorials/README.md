# You might need to register your certificate authority (CA) with AWS IoT if you are using client certificates signed by a CA that AWS IoT doesn't recognize.

[See details on AWS docs](https://docs.aws.amazon.com/iot/latest/developerguide/manage-your-CA-certs.html)



# Generate certificates using CLI

1. cd

```sh
cd certificates
```

2. Create a CA certificate with AWS IoT

```sh
. ca_cli.sh
```

3. Create a client certificate with AWS IoT

```sh
. client_cli.sh
```
