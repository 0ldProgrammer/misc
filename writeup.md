# Pickle

# Scan Nmap
  
    # nmap -p1-65535 -sC -sV 192.168.0.44
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-10-12 12:31 CEST
    Stats: 0:00:07 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
    Service scan Timing: About 50.00% done; ETC: 12:31 (0:00:06 remaining)
    Nmap scan report for 192.168.0.44
    Host is up (0.00057s latency).

    PORT     STATE SERVICE VERSION
    21/tcp   open  ftp     vsftpd 3.0.3
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    |_-rwxr-xr-x    1 0        0            1197 Oct 11 14:35 init.py.bak
    | ftp-syst: 
    |   STAT: 
    | FTP server status:
    |      Connected to ::ffff:192.168.0.17
    |      Logged in as ftp
    |      TYPE: ASCII
    |      No session bandwidth limit
    |      Session timeout in seconds is 300
    |      Control connection is plain text
    |      Data connections will be plain text
    |      At session startup, client count was 2
    |      vsFTPd 3.0.3 - secure, fast, stable
    |_End of status
    1337/tcp open  http    Werkzeug httpd 1.0.1 (Python 2.7.16)
    | http-auth: 
    | HTTP/1.0 401 UNAUTHORIZED\x0D
    |_  Basic realm=Pickle login
    |_http-server-header: Werkzeug/1.0.1 Python/2.7.16
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    MAC Address: 08:00:27:2F:5D:59 (Oracle VirtualBox virtual NIC)
    Service Info: OS: Unix

    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 8.19 seconds

The scan shows us that there are 2 open port port 21 (FTP), and 1337 (Werkzeug HTTPd). Now let's analyze the UDP ports.

    # nmap -sU -sC -sV 192.168.0.44
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-10-12 12:34 CEST
    Nmap scan report for 192.168.0.44
    Host is up (0.00096s latency).

    PORT    STATE SERVICE VERSION
    161/udp open  snmp    SNMPv1 server; net-snmp SNMPv3 server (public)
    | snmp-info: 
    |   enterprise: net-snmp
    |   engineIDFormat: unknown
    |   engineIDData: 8ac2e5721551835f00000000
    |   snmpEngineBoots: 15
    |_  snmpEngineTime: 3m22s
    | snmp-sysdescr: Linux pickle 4.19.0-11-amd64 #1 SMP Debian 4.19.146-1 (2020-09-17) x86_64
    |_  System uptime: 3m22.59s (20259 timeticks)
    MAC Address: 08:00:27:2F:5D:59 (Oracle VirtualBox virtual NIC)
    Service Info: Host: pickle

    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 2.04 seconds

The SNMP port was found which works in public, we will analyze this later and the same for the FTP.

# 21



