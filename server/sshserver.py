from binascii import hexlify
import socket
import sys
import threading
import traceback
import server

import paramiko
from paramiko.py3compat import u, decodebytes


class PServer(paramiko.ServerInterface):
    # 'data' is the output of base64.b64encode(key)
    # (using the "user_rsa_key" files)
    data = (
        b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
        b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
        b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
        b"UWT10hcuO4Ks8="
    )
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))
    usePty = False
    pty = None

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == "test") and (password == "password"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        # if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
        #    return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return False

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        print("Requested a shell")
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        print("Requested a Psuedo-terminal, term: {}, width: {}, height: {}, pixelwidth: {}, pixelheight: {}, modes: {}"
              .format(term, width, height, pixelwidth, pixelheight, modes))
        termString = bytes.decode(term, "ascii")
        if "xterm" in termString:
            self.usePty = True
            self.pty = server.Xterm(channel, term, width, height, pixelwidth, pixelheight, modes)
            return True
        else:
            print("Can only emulate xterm ptys")
            return False

    def check_channel_window_change_request(self, channel, width, height, pixelwidth, pixelheight):
        print("Requested a window resize, width: {}, height: {}, pixelWidth: {}, pixelHeight: {}"
              .format(width, height, pixelwidth, pixelheight))
        self.pty.resize(width, height, pixelwidth, pixelheight)
        return True

    def get_banner(self):
        if server.ServerInfo.banner is None:
            return "", "en-US"
        return server.ServerInfo.banner.join("\r\n"), "en-US"


class Server:
    portnum = 2200
    sock = None
    host_key = None

    def __init__(self, portnum, keyfile, keypass):
        self.portnum = portnum
        # setup logging
        paramiko.util.log_to_file("demo_server.log")

        self.host_key = paramiko.RSAKey(filename=keyfile, password=keypass)
        # host_key = paramiko.DSSKey(filename='test_dss.key')

        print("Read key: " + u(hexlify(self.host_key.get_fingerprint())))
        # now connect
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("", self.portnum))
        except Exception as e:
            print("*** Bind failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)

    def run(self):
        self.sock.listen(100)
        print("Listening for connection ...")
        while True:
            try:
                client, addr = self.sock.accept()
            except Exception as e:
                print("*** Listen/accept failed: " + str(e))
                traceback.print_exc()
                sys.exit(1)
            print("Got a connection!")
            handleThread = threading.Thread(target=self.handleconnection, args=[client])
            handleThread.start()

    def handleconnection(self, client):
        try:
            print("Handling the connection!")
            t = paramiko.Transport(client, gss_kex=False)
            t.set_gss_host(socket.getfqdn(""))
            try:
                t.load_server_moduli()
            except:
                print("(Failed to load moduli -- gex will be unsupported.)")
                raise
            t.add_server_key(self.host_key)
            pserver = PServer()
            try:
                t.start_server(server=pserver)
            except EOFError:
                print("*** EOF exception")
                return
            except paramiko.SSHException:
                print("*** SSH negotiation failed.")
                return

            # wait for auth
            chan = t.accept(20)
            if chan is None:
                print("*** No channel.")
                return
            print("Authenticated!")

            pserver.event.wait(10)
            if not pserver.event.is_set():
                print("*** Client never asked for a shell.")
                return
            # self.test_interface(chan, pserver.pty)
            server.mainmenu(pserver.pty)
        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass

