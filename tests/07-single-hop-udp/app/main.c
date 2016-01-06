/*
 * Copyright (C) 2015 Freie Universität Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     examples
 * @{
 *
 * @file
 * @brief       Example application for demonstrating the RIOT network stack
 *
 * @author      Hauke Petersen <hauke.petersen@fu-berlin.de>
 *
 * @}
 */

#include <stdio.h>

#include "shell.h"
#include "msg.h"

#include "net/gnrc.h"
#include "net/gnrc/ipv6.h"
#include "net/gnrc/udp.h"

#define PKTSIZE         (1000U)
#define ITER            (1000)
#define DELAY           (1000000U)
#define PORT            (12345U)

#define PRIO            (THREAD_PRIORITY_MAIN - 1)

static uint8_t load[PKTSIZE];
static msg_t msg_queue[8];
static char stack[THREAD_STACKSIZE_DEFAULT];

static volatile int cnt = 0;

static gnrc_netreg_entry_t server = { NULL, GNRC_NETREG_DEMUX_CTX_ALL, KERNEL_PID_UNDEF };

void udp_send(ipv6_addr_t *addr, uint16_t p, uint8_t *data, size_t len)
{
    uint8_t port[2];

    /* parse port */
    port[0] = (uint8_t)p;
    port[1] = p >> 8;

    gnrc_pktsnip_t *payload, *udp, *ip;
    /* allocate payload */
    payload = gnrc_pktbuf_add(NULL, data, len, GNRC_NETTYPE_UNDEF);
    if (payload == NULL) {
        puts("UDP Error: unable to copy data to packet buffer");
        return;
    }
    /* allocate UDP header, set source port := destination port */
    udp = gnrc_udp_hdr_build(payload, port, 2, port, 2);
    if (udp == NULL) {
        puts("UDP Error: unable to allocate UDP header");
        gnrc_pktbuf_release(payload);
        return;
    }
    /* allocate IPv6 header */
    ip = gnrc_ipv6_hdr_build(udp, NULL, 0, addr->u8, sizeof(ipv6_addr_t));
    if (ip == NULL) {
        puts("UDP Error: unable to allocate IPv6 header");
        gnrc_pktbuf_release(udp);
        return;
    }
    /* send packet */
    if (!gnrc_netapi_dispatch_send(GNRC_NETTYPE_UDP, GNRC_NETREG_DEMUX_CTX_ALL, ip)) {
        puts("UDP Error: unable to locate UDP thread");
        gnrc_pktbuf_release(ip);
        return;
    }
}

static void *svr_thread(void *arg)
{
    (void)arg;
    msg_t msg;
    gnrc_pktsnip_t *snip;

    /* setup the message queue */
    msg_init_queue(msg_queue, 8);

    while (1) {
        msg_receive(&msg);

        switch (msg.type) {
            case GNRC_NETAPI_MSG_TYPE_RCV:
                snip = (gnrc_pktsnip_t *)msg.content.ptr;
                    if (snip->size != PKTSIZE) {
                        puts("SVR: UDP packet has invalid size");
                    }
                    else {
                        printf("got pkt #%i\n", cnt++);
                    }
                    gnrc_pktbuf_release(snip);
                break;
            default:
                puts("SVR: got invalid message");
                break;
        }
    }

    /* never reached */
    return NULL;
}

static int cmd_run(int argc, char **argv)
{
    uint32_t last = xtimer_now();
    ipv6_addr_t addr;

    if (argc != 2) {
        printf("usage: %s <target IP address>\n", argv[0]);
        return 1;
    }
    /* parse destination address */
    if (ipv6_addr_from_str(&addr, argv[1]) == NULL) {
        puts("Error: unable to parse destination address");
        return 1;
    }

    char foo[128];
    ipv6_addr_to_str(foo, &addr, 128);
    printf("got addr: %s\n", foo);

    for (int i = 0; i < ITER; i++) {
        udp_send(&addr, PORT, load, PKTSIZE);
        printf("send pkt #%i\n", i);
        xtimer_usleep_until(&last, DELAY);
    }

    return 0;
}

static int cmd_clr(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    cnt = 0;
    puts("Count cleared");
    return 0;
}

static const shell_command_t shell_commands[] = {
    { "run", "send 1000 1K UDP packets to specified addr", cmd_run },
    { "clr", "reset receive counter", cmd_clr },
    { NULL, NULL, NULL }
};

int main(void)
{
    /* initialize the payload */
    for (size_t i = 0; i < PKTSIZE; i++) {
        load[i] = (uint8_t)(i & 0xff);
    }

    /* start UDP listener */
    server.pid = thread_create(stack, sizeof(stack), PRIO, 0,
                               svr_thread, NULL, "svr");
    server.demux_ctx = (uint32_t)PORT;
    gnrc_netreg_register(GNRC_NETTYPE_UDP, &server);
    printf("Started UDP server on port %i\n", (int)PORT);

    /* start shell */
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should be never reached */
    return 0;
}
