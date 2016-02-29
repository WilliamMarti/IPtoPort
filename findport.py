
# Called via webpage to clear F5 cache
#
# William Marti

import paramiko, sys, time, datetime, time

#main method

#hostname = gateway of address
def main(hostname, username, password, searchip):

  stepcount = 1

  tcpport = 22

  
  
  #setup ssh session to host
  #incase we cant connect to the host, exit
  try:

    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname,tcpport,username,password)
    ssh2 = ssh.invoke_shell()

  except:

    print "Could not connect to host"
    sys.exit()


  print "1. " + hostname

  ssh2.send("\n")
  output = ssh2.recv(5000)
  time.sleep(1)
  
  
  iparp = "sh ip arp | i " + searchip


  output = runCommand(ssh2,iparp)
  
  output = str(output)
  output = output.split()


  #make sure that that we got data back
  try:

    macaddress = output[9]

  except IndexError:

    print "ARP entry not found"
    sys.exit()

  except:
    print "Unknown Error, quitting!"
    sys.exit()


  #check if the ARP entry is Incomplete
  #print "Mac address: " + macaddress
  if(macaddress == 'Incomplete'):

    print "No MAC address entry for address"
    sys.exit()


  #setup 'sh mac address table command'
  shmacaddress = "sh mac address-table address " + macaddress

  output = runCommand(ssh2,shmacaddress)

  output = str(output)
  output = output.split()

  
  port = output[18]
  print "Port: " + port

  #need to find the physical switchports that are port of the PC
  if "channel" in port:

    ports = getSwitchportsFromPC(ssh2, port) 
    
    ports = ports.split("|", 1)

    #print ports[0] + ports[1]

    #check to see if there is a neighbor to this port
    #tells us if there is a layer 2 device on the other end or an end device
    
    neighborresult = hasNeighbor(ssh2, ports[0])
 
    print "Port: " + ports[0]
 
    #if the port channel is a switch, server or WLC
    if(neighborresult == True ):

      nexthost = getNeighbor(ssh2, port)[:11]

      print goToNeighbor(nexthost, username, password, macaddress, stepcount)


    else:

      print port 

  else:

    neighborresult = hasNeighbor(ssh2, port)
     
    if(neighborresult):

      nexthost = getNeighbor(ssh2, port)[:11]
    
      print goToNeighbor(nexthost, username, password, macaddress, stepcount)
  #print neighborresult

  #getNeighbor(ssh2, port)


  ts = time.time()
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

  #logging
  f = open('findport.log', 'a')
  f.write('Ran at ' + st + ' - Hostname: ' + hostname + '\n')
  f.close()


  #close session
  ssh2.close();


def goToNeighbor(neighbor, username, password, macaddress, stepcount):

  print "got here:"

  tcpport = 22

  try:

    
    sshnext = paramiko.SSHClient()
    sshnext.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshnext.connect(neighbor,tcpport,username,password)
    sshnext2 = sshnext.invoke_shell()

  except:

    print "Could not connect to host"
    sys.exit()

  stepcount += 1

  print stepcount + ". Switch" + neighbor

  shmacaddress = "sh mac address-table address " + macaddress

  
  output = runCommand(sshnext2,shmacaddress)
  output = str(output)
  output = output.split()

  
  port = output[21]
  return "Port: " + port



#check to see if physical port has a network device neighbor
#returns True of False
def hasNeighbor(ssh, port):

  shcdp = "sh cdp nei " + port

  neighbor = runCommand(ssh,shcdp)

  neighbor = str(neighbor)
  neighbor = neighbor.split()

  
  neighborcheck = True

  try:

    neighbortype = neighbor[57]

    if neighbortype == "H":

      neighborcheck = False

  except IndexError:

    neighborcheck = False


  return neighborcheck
  

#return the neighbor that has the 
def getNeighbor(ssh, port):

  shcdp = "sh cdp nei " + port

  neighbor = runCommand(ssh,shcdp)

  neighbor = str(neighbor)
  neighbor = neighbor.split()

  neighborname = neighbor[53]

  return neighborname
  


#All in one way to run Cisco commands at EXEC level
def runCommand(ssh, command):
  
  ssh.send(command)
  ssh.send("\n")
  
  time.sleep(1)
  output = ssh.recv(5000)
  return output

def getSwitchportsFromPC(ssh, portchannelnum):

  getmembers = "sh int " + portchannelnum + "  | i Members"

  members = runCommand(ssh, getmembers)

  members = str(members)
  members = members.split()

  members = members[10] + "|"  + members[11]

  return members

#boiler plate setup
if __name__ == "__main__":

  hostname = sys.argv[1]
  username = sys.argv[2]
  password = sys.argv[3]
  searchip = sys.argv[4]

  main(hostname, username, password, searchip)
