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

[gdf](https://raw.githubusercontent.com/0xEX75/misc/master/Screenshot_2020-10-12_12-42-07.png)
