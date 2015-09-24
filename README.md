# IPtoPort

App to be able to search ARP and MAC address tables on Cisco gear to correlate an IP address to a switchport. 

Developed for Python 2.7

# Usage

x = Layer 3 switch or router

y = username

z = password

a = IP to find port for

---
λ python findport.py x y z a

#Example
λ python findip.py myrouter.test.com username password 10.10.10.2
