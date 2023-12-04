## Goal: Verify UWB Two Way Ranging

Task #01 - TWR Aloha example
==========================

### Description

TWR aloha example is functional and reports distance estimation values within +-20cm when in LOS conditions.

### Testing procedure: Local

- On two or more devices build and flash the `examples/twr_aloha` application with the following command

    $ make -C examples/twr_aloha flash term

- Choose two devices, configure one as a responder, and recover its short address

      > twr lst on
      [twr]: start listening
      > ifconfig
      Iface  3        HWaddr: 02:95  Channel: 5  NID: DE:CA

                Long HWaddr: 08:2B:31:07:CC:74:02:95
                TX-Power: 8.5dBm  TC-PGdelay: 0xb5

- The second device will be the initiator, perform a SS-TWR exchange against the responder,
  perform 100 exchanges with 100ms intervals, and parse the average `d_cm`

      > twr req -c 100 -i 100 -p ss 02:95
      [twr]: start ranging
      {"t": 23721, "src": "8E:2B", "dst": "02:95", "d_cm": 380}
      {"t": 23821, "src": "8E:2B", "dst": "02:95", "d_cm": 371}
      {"t": 23921, "src": "8E:2B", "dst": "02:95", "d_cm": 375}


- With the same initiator, perform a DS-TWR exchange against the responder
  perform 100 exchanges with 100ms intervals, and parse the average `d_cm`

      > twr req -c 100 -i 100 -p ds 02:95
      > [twr]: start ranging
      {"t": 23721, "src": "8E:2B", "dst": "02:95", "d_cm": 380}
      {"t": 23821, "src": "8E:2B", "dst": "02:95", "d_cm": 371}
      {"t": 23921, "src": "8E:2B", "dst": "02:95", "d_cm": 375}

### Testing procedure: IoT-LAB

Not all devices on IoT-LAB are in LOS conditions, and the antennas are not facing
in the same direction, this can yield to higher than expected errors in the distance
values. For those cases a dataset is provided with the TWR results between all IoT-LAB
devices on the Lille site. These values used Decawave PANS R2 firmware. Pairs of nodes
where Decawave reports mean errors above 30cm should be ignored, since not considered
LOS, see heatmap below or provided [dataset](./static/data_full.csv)

|![Decawave-Lille](./static/deca_mean_err_heatmap.jpg)|
|:---------------------------------------------------------------------:|
|                       Distance (cm) mean error                        |
|            Decawave PANS R2- distance - IoT-LAB lille                 |

### Result

When in LOS devices report distance values within +-20cm
