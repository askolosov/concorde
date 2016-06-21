#!/usr/bin/env python2
import gnupg, re
from os.path import expanduser

def get_authinfo_password(filename, machine, login):
    authinfo_file = expanduser(filename)

    s = "machine\s+%s\s+login\s+%s\s+password\s+(.+)" % (machine, login)
    p = re.compile(s)    

    password = ""
    
    with open(authinfo_file, "rb") as stream:
        # if authinfo file is GPG-encrypted
        if re.search('\.gpg$', authinfo_file):
            gpg = gnupg.GPG(use_agent = True)
            authinfo = str(gpg.decrypt_file(stream))
        else:
            authinfo = stream.read()

        # Take password either from decrypted or from unencrypted
        # stream
        password = p.search(authinfo).group(1)

    return password
