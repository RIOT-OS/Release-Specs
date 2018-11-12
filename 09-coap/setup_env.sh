# Environment variables for tests. Source this file before running them.
#
# Tests use environment variables rather than an INI file because it matches
# how the tests also would be run from within RIOT.

export RIOTBASE="/home/kbee/dev/riot/repo" 
export AIOCOAP_BASE="/home/kbee/dev/aiocoap/repo"
export SOSCOAP_BASE="/home/kbee/dev/soscoap/repo"
export PYTHONPATH="${SOSCOAP_BASE}"
