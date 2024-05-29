# Setting up certificates from ZScaler


As part of the security practices at MCRI and RCH, some devices use [ZScaler](https://www.zscaler.com/company/faqs) for secure connections from company devices.

This means a lot of tools will scream about local cert issuer errors, but this can be resolved by providing your ZScaler cert to them.

Firstly, export your ZScaler cert from Keychain Access (assuming you are on macOS):

**Keychain Access -> Certificates ZScaler Root CA -> Right-Click -> Export -> Choose .pem as the file format**.

Save this to a directory on your home folder or dev folder. We will refer to this folder as `PATH_TO_YOUR_CERT_FOLDER` below, so remember it!

Next we export the bundle via the command line with this snippet:

```bash
(security find-certificate -a -p ls /System/Library/Keychains/SystemRootCertificates.keychain && security find-certificate -a -p ls /Library/Keychains/System.keychain) > $HOME/.mac-ca-roots
```

Next, we can set environment variables that will point to these certs and this should suppress any errors for Python/NPM packages:

```bash
export CERT_PATH=PATH_TO_YOUR_CERT_FOLDER/ca.pem
export CERT_DIR=PATH_TO_YOUR_CERT_FOLDER/
export SSL_CERT_FILE=${CERT_PATH}
export SSL_CERT_DIR=${CERT_DIR}
export REQUESTS_CA_BUNDLE="$HOME/.mac-ca-roots"
export NODE_EXTRA_CA_CERTS=${CERT_PATH}
```

For `gcloud` you can add this to your configuration:

```shell
gcloud config set core/custom_ca_certs_file ${CERT_PATH}
```

When running `docker` commands, for instance, to run `pip-compile` when managing requirements, you will need to pass your Zscaler certificates:

```shell
docker run --platform linux/amd64 \
    -v $(pwd):/opt/metamist \
    -v /local/path/to/certs/:/etc/ssl/certs:z \
    -e SSL_CERT_FILE=/etc/ssl/certs/ca.pem \
    -e SSL_CERT_DIR=/etc/ssl/certs \
    -e REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca.pem \
    python:3.11 /bin/bash -c '
    cd /opt/metamist;
    pip install pip-tools;
    echo "Installed pip-tools!";
    echo "Compiling from requirements.in";
    pip-compile requirements.in > requirements.txt;
    echo "Compiling from requirements-dev.in";
    pip-compile --output-file=requirements-dev.txt requirements-dev.in requirements.in'
```

You would need to similarly pass appropriate environment variables to use `npm` inside `docker run` too.

You can configure the environment variables for additional software using the instructions from: [Adding Custom Certificate to an Application Specific Trust Store
](https://help.zscaler.com/zia/adding-custom-certificate-application-specific-trust-store)
