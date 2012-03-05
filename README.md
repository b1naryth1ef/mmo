# About
This is a project to create a Text-Based MMO Game. It's written in Python using Twisted for server side, and the built-in socket for client side. The gui is written with PygCurse (an awesome PyGame Curse's Library).

# Code
It's released under BSD. For information on licensing and usage, please see license.txt.

## Comments
I use a tagging system created by myself. It's fairly easy to read so I wont provide documentation on it here. I feel like some of this code is pretty decent (so far I'm very happy with the server-side stuff). It's probablly horrible, but hey, w/e.

# Server/Client protocol
## Packet Prefixes
- `\x02`: The only currently used packet. A json dumped dictionary compress with zlib (Remember, its \x02content, so zlib.decompress(line[1:]))

## Server Packet Tags
PING    
WELCOME    
KICK    

## Client Packet Tags
HELLO    
JOIN_REQ      
PONG 
ACTION    
ENT_ACTION    
POS       

## Joining
Client >< Server: Gets hello, gets info. Checks protocol version, and if server is full.    
Client > Server: Packet named JOIN_REQ with username and hash (hash is none if we're a new user)  
Client < Server: KICK or WELCOME with motd and a new user hash    
Client is considered joined at this point    

# Note Bene
- I'm a nubs at some of this stuff. Dwi!
