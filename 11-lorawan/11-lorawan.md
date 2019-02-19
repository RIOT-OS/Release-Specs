## Goal: Verify LoRaWAN networking

Task #01 - LoRaWAN example
==========================

### Description

LoRaWAN example is fully functional

### Testing procedure

Build and flash the `examples/lorawan` application with the following command

    $ make BOARD=<board> DEVEUI=<device eui> APPEUI=<application eui> APPKEY=<application key> -C examples/lorawan flash term

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

- Build and flash the `tests/pkg_semtech-loramac`

      $ make BOARD=<board> -C tests/pkg_semtech-loramac flash term

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

- Build and flash the `tests/pkg_semtech-loramac`

      $ make BOARD=<board> -C tests/pkg_semtech-loramac flash term

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


Task #03 - LoRaWAN device parameters persistence
================================================

### Description

Device parameters (DevEUI, AppEUI, AppKey, etc) persistence works.


### Testing procedure

This procedure can only be performed on a board with EEPROM storage. Use the
ST B-L072Z-LRWAN1 or any other STM32 L0/L1 Nucleo 64 with an Mbed LoRa shield.

- Build and flash the `tests/pkg_semtech-loramac`

      $ make BOARD=<board> -C tests/pkg_semtech-loramac flash term

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
