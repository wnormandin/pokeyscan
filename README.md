# pokeyscan.py
### a simple port scanner

This utility was designed as a bare-bones Python 3 port scanner for circumstances where other tools might not be available.
Usage follows these basic guidelines:
```
usage: pokeyscan.py [-h] [--ports [PORTS [PORTS ...]]] [--probe]
                       [--maxprocs MAXPROCS] [--nocolor] [--verbose]
                       [--timeout TIMEOUT] [--yes] [--showall]
                       host

positional arguments:
  host                  Specify a hostname to scan

optional arguments:
  -h, --help            show this help message and exit
  --ports [PORTS [PORTS ...]]
                        Specify ports individually or in hyphenated ranges
  --probe               Probe for services on open ports
  --maxprocs MAXPROCS   Specify max number of worker processes
  --nocolor             Skip color in console output
  --verbose             Increase output verbosity
  --timeout TIMEOUT     Request timeout in s (Default = 0.25s)
  --yes                 Start scan immediately after parsing input
  --showall             Show all port tests
```
The script can be obtained directly from my script repository
```
wget https://scripts.pokeybill.us/port_scanner.py
```
The *--port* option takes individual ports or hyphenated ranges
```
# python3 pokeyscan.py --ports 25-26 587 443 --yes --verbose --maxprocs 10 server.test.us
[*] PokeyScan Port Scanner v0.1a (Development)
 -  Command Line Arguments Parsed
 -  timeout   :                 0.25
 -  probe     :                False
 -  maxprocs  :                   10
 -  ports     : ['25-26', '587', '443']
 -  host      :  server.test.us
 -  nocolor   :                False
 -  verbose   :                 True
 -  yes       :                 True
 -  showall   :                False
 -  ip        :        108.89.121.24
[*] User chose --yes, beginning scan
 -  Worker Pool Created (10 worker(s))
 -  Checking 4 ports
[*] Workers spawned
[*] Workers joined
--------------------------------------------
Port 25 OPEN
Port 26 OPEN
Port 443 OPEN
Port 587 OPEN
```
The *--probe* option will read the first few lines of output.  Basic HTTP requests are sent to probe ports which do not respond upon connection.
```
# python3 pokeyscan.py --ports 5000-8000 --yes --probe --maxprocs 10 server.test.us
[*] PokeyScan Port Scanner v0.1a (Development)
[*] User chose --yes, beginning scan
--------------------------------------------
Port 7001 OPEN: SSH-2.0-OpenSSH_5.3 % 
```
