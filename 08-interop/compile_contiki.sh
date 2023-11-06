#!/bin/bash

cd /tmp

# Clone Contiki-NG
git clone https://github.com/contiki-ng/contiki-ng.git; cd contiki-ng || \
cd contiki-ng; git pull
git submodule update --init --recursive

# Pull the Contiki-NG Docker image
docker pull contiker/contiki-ng

# Add the `shell` service to the `examples/hello-world` application.
if ! grep -q "MODULES += os/services/shell" examples/hello-world/Makefile; then
    sed -i '/all: $(CONTIKI_PROJECT)/a\\nMODULES += os/services/shell\n' examples/hello-world/Makefile
fi


# Compile the `examples/hello-world` application for the nRF52840 platform.
export CNG_PATH=/tmp/contiki-ng
docker run \
    -e LOCAL_UID=$(id -u $USER) \
    -e LOCAL_GID=$(id -g $USER) \
    --mount type=bind,source=$CNG_PATH,destination=/home/user/contiki-ng \
    contiker/contiki-ng \
    make -C examples/hello-world TARGET=nrf52840 hello-world
