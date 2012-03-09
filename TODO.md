#TODO
- Work on chat (Probablly should be channel based just in case)
- Figure out how to transmit entities cleanly (Json seems overly bulky in that case. *maybe* pickle?)
- Check state before parsing game packets (e.g. shouldnt be in INIT if we get a POS)

#DONE
- Kick should be \x02 with a reason
- Client code needs to be cleaned up. Maybe move to a more event-like system?
- Server should be disconnecting clients...
- Add pinging
- Get some basic movement and action events working