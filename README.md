# weechat-atcompletion
WeeChat plugin (Python) for @nick completion

Enagle and configure for server and buffers to enable nick completion to include '@' symbol. Useful for protocols like HipChat, Slack, and possibly a few others.

# Commands
```
/atcomplete enable|disable|toggle
/atcomplete status
/atcomplete servers [list | add name | del name]
/atcomplete buffers [list | add name | del name]
```

servers name: %(irc_servers) (e.g. bitlbee / freenode / myircserver)
buffers name: supports simple regex. (e.g. bitlbee.#* or bitlbee.#hc*)
