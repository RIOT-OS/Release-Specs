#!/bin/bash

# Get the directory of this file
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd /tmp

mkdir -p zephyrproject

docker run \
    -e LOCAL_UID=$(id -u $USER) \
    -e LOCAL_GID=$(id -g $USER) \
    -v zephyrproject:/workdir \
    docker.io/zephyrprojectrtos/zephyr-build:latest \
    /bin/bash -c '

west init 
west update cmsis hal_atmel
west zephyr-export
pip install -r ~/zephyrproject/zephyr/scripts/requirements.txt

cd /workdir/zephyr
echo "CONFIG_CPP=n

CONFIG_NET_PKT_RX_COUNT=5
CONFIG_NET_PKT_TX_COUNT=5
CONFIG_NET_BUF_RX_COUNT=5
CONFIG_NET_BUF_TX_COUNT=5
CONFIG_NET_MAX_CONTEXTS=2
CONFIG_NET_MAX_CONN=1
CONFIG_NET_MAX_ROUTES=1
CONFIG_NET_MAX_NEXTHOPS=1

CONFIG_SHELL_STACK_SIZE=512
CONFIG_SHELL_CMD_BUFF_SIZE=32
CONFIG_SHELL_ARGC_MAX=6
CONFIG_SHELL_HISTORY_BUFFER=4

CONFIG_LOG_MODE_MINIMAL=y
CONFIG_NET_IP_DSCP_ECN=n
CONFIG_NET_STATISTICS=n
CONFIG_NET_MGMT_EVENT_STACK_SIZE=384
CONFIG_IEEE802154_RF2XX_RX_STACK_SIZE=384

CONFIG_UART_USE_RUNTIME_CONFIGURE=n" > samples/net/sockets/echo_server/boards/atsamr21_xpro.conf
west build -p auto -b atsamr21_xpro samples/net/sockets/echo_server -- -DOVERLAY_CONFIG=overlay-802154.conf
'
