## Goal: Send/Receive typical CoAP messages

Introduction
============
With all of these tests, your confidence in the results will increase by
watching the CoAP messages in Wireshark.

These tests all were developed using native on a recent Ubuntu Linux. However,
they all may be run just as well on hardware.

Materials
---------

You'll need a recent copy of [aiocoap](https://github.com/chrysn/aiocoap).

Setup
-----

Some of these examples use a tap interface with a ULA configured on a Unix-like
system as:
```
    $ ip address add fd00:bbbb::1/64 dev tap0 scope global
```

Use the included `setup_tap.sh` to automate creation of this interface and
address, and `teardown_tap.sh` to remove it.

The ULA must be configured manually in the RIOT SUT at the command line with:
```
    > ifconfig 6 add unicast fd00:bbbb::2/64
```

Notice that the address for the SUT uses host '2', and the other endpoint uses
host '1'.


Task #01 - CORD Endpoint
========================
### Description

Client registers with an aiocoap CORE Resource Directory (RD) server. Exercises
confirmable (CON) client and server messaging with gcoap.

### Result

Registration succeeds, and client refreshes registration periodically.

### Details

On a Linux machine, start an aiocoap example server with the `aiocoap-rd`
script.

Start a native terminal for the RIOT cord_ep example app.

Register with the RD server with the command:
```
   > cord_ep register coap://[fd00:bbbb::1]
```

You should see the message below in the RIOT native terminal:
```
registration successful

CoAP RD connection status:
RD address: coap://[fd00:bbbb::1]:5683
   ep name: RIOT-2D0C232323232323
  lifetime: 60s
    reg if: /resourcedirectory
  location: /reg/1/

```

Periodically, the client re-registers with the server. You should see the
message below in the RIOT terminal:
```
RD endpoint event: successfully updated client registration
```


Task #02 - Confirmable retries
==============================
### Description

gcoap sends a CON GET request to an aiocoap server. The test runner delays
startup of aiocoap to trigger gcoap to resend the message.

### Result
gcoap receives the server response and stops resending messages. If the server
is not started within the timeout window, gcoap gives up and reports the timeout.

### Details
gcoap attempts a maximum of four retries; five messages altogether including
the initial one. The retries are timed with CoAP's exponential backoff mechanism
and jitter. The retry interval doubles with each attempt and varies +/- 50% of
the interval. So, the sequence is:

* original, wait  2 +- 1
* retry 1,  wait  4 +- 2
* retry 2,  wait  8 +- 4
* retry 3,  wait 16 +- 8
* retry 4,  wait 32 +-16
* timeout

Start the gcoap example and send a CON message to aiocoap:
```
    > coap get -c fd00:bbbb::1 5683 /time
```

Wait some period of time, and then start the aiocoap example server
```
    $ server.py
```

On the next retry gcoap shows it received the response:
```
gcoap: response Success, code 2.05, 16 bytes
```

or, if gcoap has timed out:
```
gcoap: timeout for msg ID 50754
```


Task #03 - Block1
=================
### Description

aiocoap slices a payload into a sequence of Block1 encoded POSTs to nanocoap.
nanocoap computes and returns the SHA-256 message digest of the payload.

### Result

nanocoap returns the expected message digest in a 2.04 response.

### Details

Start the nanocoap_server example. Then run `task03.py` as described in the
comment at the top of that file.


Task #04 - Block2
=================
### Description

aiocoap GETs a sequence of Block2 encoded packets from nanocoap that encode
information about a RIOT instance.

### Result

nanocoap returns the expected payload in a 2.05 response.

### Details

Start the nanocoap_server example. Then run `task04.py` as described in the
comment at the top of that file.


Task #05 - Observe registration and notification
================================================
### Description

aiocoap sends an Observe request to gcoap. gcoap then sends a request itself,
which updates its observed resource. This update triggers gcoap to send an
Observe notification to aiocoap.

### Result

* aiocoap receives an initial response with an Observe option
* gcoap receives a request from aiocoap for /time
* aiocoap receives a following observe notification

### Details

Start the gcoap example server. If desired, configure the ULA as described in
the Introduction section

    > ifconfig 6 add unicast fd00:bbbb::2/64

Start the aiocoap server in `task05.py`, as described at the top of that file.
aiocoap automatically sends a get request to gcoap to register for the
/cli/stats resource.

aiocoap receives the initial response, which show 0 for the resource value:
```
First response: <aiocoap.Message at 0x7f84dfa11c18: Type.ACK 2.05 Content
(MID 21466, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'0'
```

Then paste the command below into the gcoap command line:
```
    > coap get -c fd00:bbbb::1 5683 /time
```

gcoap prints the response below from aiocoap:
```
gcoap: response Success, code 2.05, 16 bytes
2018-10-30 08:19

```

aiocoap prints the response below from the Observe notification:
```
Next result: <aiocoap.Message at 0x7f84dfa15240: Type.NON 2.05 Content
(MID 17807, token 6f1d) remote <UDP6EndpointAddress [fd00:bbbb::2]:5683 with
local address>, 2 option(s), 1 byte(s) payload>
b'1'
Loop ended, wait 10 sec

```
