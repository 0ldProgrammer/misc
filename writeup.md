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

# FTP

We can see in the FTP server there is a file named "init.py.bak", download it with the ftp command.

    # ftp 192.168.0.44
    Connected to 192.168.0.44.
    220 (vsFTPd 3.0.3)
    Name (192.168.0.44:root): anonymous
    331 Please specify the password.
    Password:
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> ls
    200 PORT command successful. Consider using PASV.
    150 Here comes the directory listing.
    -rwxr-xr-x    1 0        0            1197 Oct 11 14:35 init.py.bak
    226 Directory send OK.
    ftp> mget init.py.bak
    mget init.py.bak? y
    200 PORT command successful. Consider using PASV.
    150 Opening BINARY mode data connection for init.py.bak (1197 bytes).
    226 Transfer complete.
    1197 bytes received in 0.02 secs (70.4226 kB/s)
    
This is probably an old backup file, when we open the file it probably looks like the Werkzeug server for port 1337, we will be interested in this for later.

    from functools import wraps
    from flask import *
    from flask_htpasswd import HtPasswdAuth
    import hashlib
    import socket
    import base64
    import pickle
    import hmac

    app = Flask(__name__, template_folder="templates", static_folder="/opt/project/static/")

    @app.route('/', methods=["GET", "POST"])
    def index_page():
      '''
        __index_page__()
      '''
      if request.method == "POST" and request.form["story"] and request.form["submit"]:
        md5_encode = hashlib.md5(request.form["story"]).hexdigest()
        paths_page  = "/opt/project/uploads/%s.log" %(md5_encode)
        write_page = open(paths_page, "w")
        write_page.write(request.form["story"])

        return "The message was sent successfully!"

      return render_template("index.html")

    @app.route('/checklist', methods=["GET", "POST"])
    def check_page():
      '''
        __check_page__()
      '''
      if request.method == "POST" and request.form["check"]:
        path_page    = "/opt/project/uploads/%s.log" %(request.form["check"])
        open_page    = open(path_page, "rb").read()
        open_command = pickle.loads(open_page)
        return str(open_command)
      else:
        return "Server Error!"

      return render_template("checklist.html")

    if __name__ == '__main__':
      app.run(host='0.0.0.0', port=1337, debug=True)

# Werkzeug HTTPd

When I open my browser to view the site, it asks for a username and password. I tried the default credentials but it didn't work.

![gdf](https://raw.githubusercontent.com/0xEX75/misc/master/Screenshot_2020-10-12_12-42-07.png)

# SNMP

SNMP can be publicly accessible, so let's use the snmpwalk command to find out more about this service. If you don't know what SNMP is, don't hesitate to check Google. To put it simply, it is simply a protocol that manages network equipment to monitor and diagnose network and hardware problems remotely.

    # snmpwalk -c public -v 1 192.168.0.44|head -n 15
    Bad operator (INTEGER): At line 73 in /usr/share/snmp/mibs/ietf/SNMPv2-PDU
    SNMPv2-MIB::sysDescr.0 = STRING: Linux pickle 4.19.0-11-amd64 #1 SMP Debian 4.19.146-1 (2020-09-17) x86_64
    SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-TC::linux
    DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (96182) 0:16:01.82
    SNMPv2-MIB::sysContact.0 = STRING: lucas:SuperSecretPassword123! # <<<<<<<<<<
    SNMPv2-MIB::sysName.0 = STRING: pickle
    SNMPv2-MIB::sysLocation.0 = STRING: Sitting on the Dock of the Bay
    SNMPv2-MIB::sysServices.0 = INTEGER: 72
    SNMPv2-MIB::sysORLastChange.0 = Timeticks: (45) 0:00:00.45
    SNMPv2-MIB::sysORID.1 = OID: SNMP-MPD-MIB::snmpMPDCompliance
    SNMPv2-MIB::sysORID.2 = OID: SNMP-USER-BASED-SM-MIB::usmMIBCompliance
    SNMPv2-MIB::sysORID.3 = OID: SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance
    SNMPv2-MIB::sysORID.4 = OID: SNMPv2-MIB::snmpMIB
    SNMPv2-MIB::sysORID.5 = OID: SNMP-VIEW-BASED-ACM-MIB::vacmBasicGroup
    SNMPv2-MIB::sysORID.6 = OID: TCP-MIB::tcpMIB
    SNMPv2-MIB::sysORID.7 = OID: IP-MIB::ip
    
We have found the crendential, we can connect to the Werkzeug service. The python script in the FTP server will allow us to continue our journey in this boxing.

# Warkzeug HTTPd

There are only 3 sections, `HOME`, `CHECK` and `RESET`. The `CHECK` and `RESET` sections only return "Server Error!"

![b](https://raw.githubusercontent.com/0xEX75/misc/master/Screenshot_2020-10-12_12-51-22.png)

The paths are also in the Python code. But there is only `/checklist` and the (`/`). It is missing `/reset` because it is probably a backup file and it is not the main file. We can see the path redirects in the Python code.

    @app.route('/', methods=["GET", "POST"])
    [...SNIP...]
    @app.route('/checklist', methods=["GET", "POST"])
    
If we take a closer look at the `index_page()` function, it performs actions if we try to send a message to the Werkzeug server.

    @app.route('/', methods=["GET", "POST"])
    def index_page():
      if request.method == "POST" and request.form["story"] and request.form["submit"]:
        md5_encode = hashlib.md5(request.form["story"]).hexdigest()
        paths_page  = "/opt/project/uploads/%s.log" %(md5_encode)
        write_page = open(paths_page, "w")
        write_page.write(request.form["story"])

        return "The message was sent successfully!"

First, there is a condition that tests if this is the correct method (POST) and also tests if the `[story]` and `[submit]` parameter exist. The `[story]` parameter corresponds to the message we send.

    if request.method == "POST" and request.form["story"] and request.form["submit"]
   
So concretely it encrypts the message we send in MD5 and it puts it in a variable named md5_encode.   
    
    md5_encode = hashlib.md5(request.form["story"]).hexdigest()
    
Here, in concrete terms, it retrieves our message, encrypts it in MD5, and will create a file with the MD5.

    paths_page  = "/opt/project/uploads/%s.log" %(md5_encode)
    
 Here we can see that the code will create a file in the `uploads/` folder and it will write our message to the file.   
    
    write_page = open(paths_page, "w")
    write_page.write(request.form["story"])

We will now study the `check_page()` function. First, we can observe that the condition tests the method if it is in `POST` and also tests if the `check` parameter exists.

    if request.method == "POST" and request.form["check"]
    
Here it seems to point to an MD5 file in the `uploads/` folder. It will probably try to open this file.    
    
    path_page = "/opt/project/uploads/%s.log" %(request.form["check"])
    
If we enter the encrypted MD5 file, we can open it with the `check` parameter.
    
    open_page = open(path_page, "rb").read()
    
pickle will pickle each of these pieces separately, and then on unpickling, will call the callable on the provided arguments to construct the new object. And so, we can construct a pickle that, when un-pickled, will execute command. (Good link [here](https://dan.lousqui.fr/explaining-and-exploiting-deserialization-vulnerability-with-python-en.html))

    open_command = pickle.loads(open_page)
    
Here it tests if there is p1 value in the file if there is not p1 value in the file, it will open the file.

    if("p1" in open_command)
      return str(open_command)
    else
      return open_page
      
 # Exploitation
 
 We have seen that the `check_page()` function loads a file, and if we do some data deserialization we can execute a command. If you don't understand, read an article [here](https://blog.nelhage.com/2011/03/exploiting-pickle/).
 
We will first do a little serialization and file reading test to better understand the context. If for example I want to read the message I sent. I need to encrypt the message in MD5 first, let's use Python for that.

    >>> import hashlib
    >>> message = "hello"
    >>> print(hashlib.md5(message).hexdigest())
    5d41402abc4b2a76b9719d911017c592
    
If now in the text field I write "hello" and now try to use the `/checklist` function, I can perfectly read my message which saved in the remote server.

    curl -u 'lucas:SuperSecretPassword123!' 'http://192.168.0.44:1337/checklist' -d "check=5d41402abc4b2a76b9719d911017c592"
    hello
    
Now we need to test with serialization to run commands. We need to create a Python script for this, get your keyboards ready.

