# About
This is a project to create a Text-Based MMO Game. It's based off Pythons *built-in* asyncore networking stuff. I probablly could have used Twisted, but it seemed overly bulky for this type of project. 

# Code
It's released under BSD. For information on licensing and usage, please see license.txt.

## Comments
I use a tagging system created by myself. It's fairly easy to read so I wont provide documentation on it here. I feel like some of this code is pretty decent (so far I'm very happy with the server-side stuff). It's probablly horrible, but hey, w/e.

# Server/Client protocol
## Packet Prefixes
`\x00`: Plain text (aka just an event, no data)
`\x01`: Zlib.
`\x02`: Json compress with zlib. (Is always a dict, with at least key 'tag')

## Server Packet Tags
PING
WELCOME
KICK

## Client Packet Tags
HELLO
JOIN_REQ
AUTH
PONG

## Joining
Client >< Server: Gets hello, gets info. Checks protocol version, and if server is full.
Client > Server: JOIN_REQ, a `\x02` packet tagged the same with username and a hash (none if we're a new user)
Client < Server: KICK or WELCOME with motd and a new user hash
Client is considered joined at this point

# Note Bene
- I'm a nubs at some of this stuff. Dwi!

# Todo
- Near 100% cpu usage when a client is active. Doing it wrong? ()