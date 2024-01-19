# Setting up certificates from ZScaler


As part of the security practices at CPG, we use ZScaler for secure connections from the company devices.

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

<<<<<<< Updated upstream
You can configure the environment variables for additional software using the instructions from: https://help.zscaler.com/zia/adding-custom-certificate-application-specific-trust-store
=======
You can configure the environment variables for additional software using the instructions from: [Adding Custom Certificate to an Application Specific Trust Store
](https://help.zscaler.com/zia/adding-custom-certificate-application-specific-trust-store)
>>>>>>> Stashed changes

