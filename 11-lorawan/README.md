## Goal: Verify LoRaWAN networking

Task #01 - LoRaWAN example
==========================

### Description

LoRaWAN example is fully functional

### Testing procedure

Build and flash the `examples/networking/misc/lorawan` application with the following command

    $ make BOARD=<board> DEVEUI=<device eui> APPEUI=<application eui> APPKEY=<application key> -C examples/networking/misc/lorawan flash term

_Note:_ The application can be tested on IoT-LAB with a device register on
TheThingsNetwork backend: start an experiment with one of the st-lrwan1 boards
and pass `IOTLAB_NODE=auto-ssh` to the make command.

### Result

With valid device EUI, application EUI and application key, the example
application can join the backend. Messages are received on the backend every
~20s.


Task #02 - OTAA join procedure
==============================

### Description

OTAA join procedure and uplink with datarates indexes 0, 3, 5 (others are optional)

### Testing procedure

- Build and flash the `tests/pkg/semtech-loramac`

      $ make BOARD=<board> -C tests/pkg/semtech-loramac flash term

- Configure the devive EUI, application EUI, application key

      > loramac set deveui 0011223344556677
      > loramac set appeui 0011223344556677
      > loramac set appkey 00112233445566770011223344556677

- Configure the desired datarate index

      > loramac set dr <datarate index>

- Join the network using OTAA

      > loramac join otaa

- Send confirmed messages on port 123

      > loramac tx <message> cnf 123

- Send unconfirmed messages on port 42

      > loramac tx <message> uncnf 42

- Reboot the node after each datarate test

### Result

All joins are successful, messages are sent with success and correctly received
on the LoRaWAN backend (same datarate, same port).
TX attempts within the dutycycle are skipped (very likely to happen with low
datarates). Messages sent from the backend to the device are received.
The device doesn't hang: the shell is responsive after the send/receive is
finished.


Task #03 - ABP join procedure
=============================

ABP join procedure and uplinks with datarates indexes 0, 3, 5 (others are optional)

### Testing procedure

- Build and flash the `tests/pkg/semtech-loramac`

      $ make BOARD=<board> -C tests/pkg/semtech-loramac flash term

- Configure the devive EUI, application EUI, application key

      > loramac set deveui 0011223344556677
      > loramac set appeui 0011223344556677
      > loramac set devaddr 00112233
      > loramac set appskey 00112233445566770011223344556677
      > loramac set nwkskey 00112233445566770011223344556677

- Configure the desired datarate index

      > loramac set dr <datarate index>

- If using TheThingsNetwork backend, configure the RX2 window datarate
  parameter:

      > loramac set rx2_dr 3

- Join the network using ABP

      > loramac join abp

- Send confirmed messages on port 123

      > loramac tx <message> cnf 123

- Send unconfirmed messages on port 42

      > loramac tx <message> uncnf 42

- Reboot the node after each datarate test. _Note:_ When using a board without
  EEPROM support, the frame counters must also be reset on the LoRaWAN backend.

### Result

All messages are sent with success and correctly received on the LoRaWAN
backend (same datarate, same port).
TX attempts within the dutycycle are skipped (very likely to happen with low
datarates). Messages sent from the backend to the device are received.
The device doesn't hang: the shell is responsive after the send/receive is
finished.


Task #04 - LoRaWAN device parameters persistence
================================================

### Description

Device parameters (DevEUI, AppEUI, AppKey, etc) persistence works.


### Testing procedure

This procedure can only be performed on a board with EEPROM storage. Use the
ST B-L072Z-LRWAN1 or any other STM32 L0/L1 Nucleo 64 with an Mbed LoRa shield.

- Build and flash the `tests/pkg/semtech-loramac`

      $ make BOARD=<board> -C tests/pkg/semtech-loramac flash term

- Erase any previously stored parameters:

      > loramac erase

- Verify parameters are erased: all get subcommand should return lists of 0

      > reboot
      > loramac get deveui
      > loramac get appeui
      > loramac get appkey
      > loramac get devaddr
      > loramac get appskey
      > loramac get nwkskey

- Set OTAA parameters and save them:

      > loramac set deveui 0011223344556677
      > loramac set appeui 0011223344556677
      > loramac set appkey 00112233445566770011223344556677
      > loramac save

- Reboot and verify OTAA parameters have been reloaded:

      > reboot
      > loramac get deveui
      > loramac get appeui
      > loramac get appkey
      > loramac erase

- Set ABP parameters and save them:

      > loramac set devaddr 00112233
      > loramac set appskey 00112233445566770011223344556677
      > loramac set nwkskey 00112233445566770011223344556677
      > loramac save

- Reboot and verify ABP parameters have been reloaded:

      > reboot
      > loramac get devaddr
      > loramac get appskey
      > loramac get nwkskey

### Result

The erase subcommand correctly erases stored parameters. All saved parameters
are correctly reloaded after a reboot.

Task #05 - GNRC LoRaWAN (Over The Air Activation)
=================================================

### Description

GNRC LoRaWAN is able to join a LoRaWAN network using Over The Air Activation and
send/receive LoRaWAN frames.

### Testing procedure

- Build and flash the `examples/networking/gnrc/lorawan`

      $ make BOARD=<board> -C examples/networking/gnrc/lorawan flash term

- Configure the device EUI, application EUI, application the `ifconfig` command

      > ifconfig <lw_if> set deveui 0011223344556677
      > ifconfig <lw_if> set appeui 0011223344556677
      > ifconfig <lw_if> set appkey 00112233445566778899AABBCCDDEEFF

- Configure join method to OTAA
      > ifconfig <lw_if> otaa

- Trigger the join procedure
      > ifconfig <lw_if> up

- Wait for the OTAA procedure to finish (usually around 6 seconds). After that,
  `ifconfig` should report that the interface is up (Link: up)
      > ifconfig <lw_if>

- Schedule a confirmable downlink message to this node (port 2). This is done
  in the Network Server (if using TTN, this is available in the Overview tab
  of the device)

- Configure GNRC LoRaWAN to send unconfirmed messages.
      > ifconfig <lw_if> -ack_req

- Send a message using the `send` command
      > send <lw_if> "This is an unconfirmed RIOT message!"

- After 2 seconds the downlink message should be shown in the RIOT shell.

- Configure GNRC LoRaWAN to send confirmed messages.
      > ifconfig <lw_if> ack_req

- Send a message using the `send` command
      > send <lw_if> "This is a confirmed RIOT message!"

### Result

GNRC LoRAWAN should be able to send and receive data from the Network Server.
Both send functions should print `Successfully sent packet`
The Network Server should notify the reception of an ACK (carried with the
frame right after the node receives data)