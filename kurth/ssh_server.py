#!/usr/bin/env python

'''
Do I care to document anything? Maybe later...
'''

from twisted.python import log
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.conch.ssh import connection, factory, session, transport, userauth
from twisted.conch import recvline, avatar, interfaces

import os
import sys
import time
import traceback
from sys import stdout
from zope.interface import implements

from core import bash
from filesystem import fs as filesystem

log.startLogging(file('kurth.log', 'w'))
log.addObserver(log.FileLogObserver(stdout).emit)


class Output:
    def __init__(self, terminal):
        self.terminal = terminal

    def log(self, text):
        global log
        log.msg(text)

    def write(self, text):
        self.log(text)
        self.terminal.write(text)


class KurthProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user
        self.hostname = 'localhost'
        end = '#' if user == 'root' else '$'
        self.prompt = '[%s@%s]%s ' % (self.user.username, self.hostname, end)
        self.fs = filesystem.FS_Walker()

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)

        # This took far too long to figure out
        self.remote_ip = self.terminal.transport.getPeer().address.host

        self.output = Output(self.terminal)
        sys.stdout = self.output
        self.shell = bash.Shell(self.fs, self.user.username, self.remote_ip,
                                self.terminal)
        self.terminal.reset()
        self.show_prompt()
        self.keyHandlers.update(dict.fromkeys(['\x0B', '\x0C', '\x0E',
            '\x0F', '\x01', '\x02', '\x05', '\x06', '\x07', '\x08', '\x10',
            '\x11', '\x12', '\x13', '\x14', '\x16', '\x17', '\x18', '\x19'],
            self.ignore))
        self.keyHandlers.update({
            '\x09':     self.handle_tab,
            '\x03':     self.handle_ctrl_c,
            '\x04':     self.handle_ctrl_d,
            '\x15':     self.handle_ctrl_u,
            '\x1A':     self.handle_ctrl_z
            })

    def lineReceived(self, line):
        # don't waste log space if the user hits enter with nothing typed
        if line:
            self.output.log(line)

            # log any rampant exception and make sure we still print a prompt -
            # don't want to risk losing that deep User Experience(TM) /joke
            try:
                self.shell.line_in(line)
            except Exception:
                self.output.log(traceback.format_exc())
        self.show_prompt()

    def show_prompt(self):
        self.terminal.write(self.prompt)

    def handle_ctrl_c(self):
        self.terminal.nextLine()
        self.show_prompt()

    def handle_ctrl_d(self):
        self.terminal.loseConnection()

    def handle_ctrl_u(self):
        self.terminal.deleteLine()
        self.terminal.cursorBackward(len(self.prompt) + self.lineBufferIndex)
        self.terminal.write(self.prompt)
        self.lineBuffer = []
        self.lineBufferIndex = 0

    def handle_ctrl_z(self):
        pass

    def handle_tab(self):
        pass

    def ignore(self):
        pass


class KurthAvatar(avatar.ConchUser):
    implements(interfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup['session'] = session.SSHSession

    def openShell(self, protocol):
        server = insults.ServerProtocol(KurthProtocol, self)
        server.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(server))

    def getPty(self, terminal, window_size, attrs):
        self.windowSize = window_size
        return None

    def windowChanged(self, size):
        self.windowSize = size

    def eofReceived(self):
        pass

    def closed(self):
        pass


class KurthRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarID, mind, *items):
        print 'request'
        if interfaces.IConchUser in items:
            return items[0], KurthAvatar(avatarID), lambda: None
        else:
            log.msg('No supported interfaces found')
            log.err()


class KurthSSHFactory(factory.SSHFactory):
    def __init__(self):
        self.starttime = time.time()
        self.services = {'ssh-userauth': userauth.SSHUserAuthServer,
                         'ssh-connection': connection.SSHConnection}

    # as implemented by Kojoney
    def buildProtocol(self, addr):
        trans = transport.SSHServerTransport()
        trans.ourVersionString = 'SSH-2.0-OpenSSH_5.3p1'
        trans.supportedPublicKeys = self.privateKeys.keys()

        if not self.primes:
            ske = trans.supportedKeyExchanges[:]
            ske.remove('diffie-hellman-group-exchange-sha1')
            trans.supportedKeyExchanges = ske
        trans.factory = self
        self.protocol = trans
        return trans


def generateRSAKeys():
    if not (os.path.isfile('keys/public.key') and
            os.path.isfile('keys/private.key')):
        print 'Generating RSA keypair...'
        from Crypto import Random
        from Crypto.PublicKey import RSA
        key_length = 1024
        random_generator = Random.new().read
        rsa_key = RSA.generate(key_length, random_generator)
        private_key = rsa_key.exportKey()
        public_key = rsa_key.publickey().exportKey(format='OpenSSH')
        file('keys/public.key', 'wb').write(public_key)
        file('keys/private.key', 'wb').write(private_key)
        print 'done.'

if __name__ == '__main__':
    sshFactory = KurthSSHFactory()
    # sshFactory = factory.SSHFactory()

    sshFactory.portal = portal.Portal(KurthRealm())
    users = {'user': 'user', 'root': 'root'}
    sshFactory.portal.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

    generateRSAKeys()
    with open('keys/public.key') as pub:
        PUBBLOB = pub.read()
        sshFactory.publicKeys = {'ssh-rsa': Key.fromString(data=PUBBLOB)}
    with open('keys/private.key') as priv:
        PRIVBLOB = priv.read()
        sshFactory.privateKeys = {'ssh-rsa': Key.fromString(data=PRIVBLOB)}

    reactor.listenTCP(2022, sshFactory)
    reactor.run()
