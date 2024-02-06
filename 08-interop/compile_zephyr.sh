#!/bin/bash

# Get the directory of this file
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd /tmp

mkdir -p zephyrproject

docker run \
    --privileged \
    -e LOCAL_UID=$(id -u $USER) \
    -e LOCAL_GID=$(id -g $USER) \
    -v  /tmp/zephyrproject:/workdir \
    docker.io/zephyrprojectrtos/zephyr-build:latest \
    /bin/bash -c '

west init
west update cmsis hal_atmel
west zephyr-export
pip install -r ~/zephyrproject/zephyr/scripts/requirements.txt

cd /workdir/zephyr
west build -p auto -b atsamr21_xpro samples/net/sockets/echo_server -- -DOVERLAY_CONFIG=overlay-802154.conf
west flash
'
