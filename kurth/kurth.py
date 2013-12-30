#!/usr/bin/env python

'''
Do I care to document anything? Maybe later...
'''

from twisted.python import log
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.insults import insults
from twisted.application import service, internet
from twisted.cred import portal, checkers, credentials
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.conch import recvline, error, avatar, interfaces

import os, rsa
from sys import stdout
from zope.interface import implements

from util import columnize
from filesystem import fs as filesystem

log.startLogging(stdout)
log.addObserver(log.FileLogObserver(file("kurth.log", 'w')).emit)

class KurthProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user
        self.hostname = 'localhost'
        end = '#' if user == 'root' else '$'
        self.prompt = '[%s@%s]%s ' % (self.user.username, self.hostname, end)
        self.commands = {'whoami': self.whoami,
                         'clear': self.clear,
                         'echo': self.echo,
                         'exit': self.exit,
                         'pwd': self.pwd,
                         'who': self.who,
                         'ls': self.ls,
                         'cd': self.cd,
                         'w': self.w}
        fs_file = os.path.dirname(os.path.realpath(__file__)) + \
                                  '/filesystem/fs.gz'
        self.fs = filesystem.FS_Walker(fs_file)

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.reset()
        self.show_prompt()
        self.keyHandlers.update({
            '\x09':     self.handle_TAB,
            '\x03':     self.handle_CTRL_C,
            '\x04':     self.handle_CTRL_D,
            '\x15':     self.handle_CTRL_U
            })

    def terminalSize(self, width, height):
        self.width = width
        self.height = height

    def lineReceived(self, line):
        self.log(self.prompt + line)
        if line:
            cmd_split = line.split()
            command = cmd_split[0]
            args = cmd_split[1:]
            try:
                self.commands[command](args)
            except KeyError:
                self.output(command + ': command not found')
                self.terminal.nextLine()
        self.show_prompt()

    def show_prompt(self):
        self.terminal.write(self.prompt)

    def log(self, text):
        global log
        log.msg(text)

    def output(self, text):
        self.log(text)
        self.terminal.write(text)

    # def output_greedy(self, words):
    #     '''
    #     We want to keep the number of log calls down as to save time writing
    #     the log file. We only want one output called per each command called.
    #     '''

    #     current_length = 0
    #     for word, index in enumerate(words):
    #         current_length += len(word)
    #         if current_length < self.width:
    #             words.insert(index, '\n')
    #             current_length = 0
    #     out = ' '.join(words)
    #     self.output(out)

    #     return ''

    def output_columned(self, words):
        self.output(columnize.columnize(words))

##### start commands ##########################################################

    def cat(self, args):
        for arg in args:
            self.output(self.fs.read(arg))
            self.terminal.nextLine()

    def cd(self, args):
        ret = self.fs.cd(args)
        if ret:
            self.output(ret)
            self.terminal.nextLine()

    def clear(self, *_):
        self.terminal.reset()

    def echo(self, args):
        self.output(' '.join(args))
        self.terminal.nextLine()

    def exit(self, *_):
        self.terminal.loseConnection()

    def grep(self, args):
        pass

    def ls(self, args):
        data = self.fs.ls(args)
        self.output_columned(data)

    def pwd(self, *_):
        self.output(self.fs.pwd())

    def sed(self, args):
        pass

    def w(self, args):
        if self.width <= 70:
            self.output('w: %i column window is too narrow' % self.width)

    def who(self, args):
        template = '%(name)s   %(line)s          %(time)s %(comment)s'
        self.output(template % {'name': self.user.username, 'line': 'pts/7',
                    'time': '2013-12-25 00:00', 'comment': '(:0)'})
        self.terminal.nextLine()

    def whoami(self, args):
        self.output(self.user.username)
        self.terminal.nextLine()

##### start handlers ##########################################################

    def handle_CTRL_C(self):
        self.terminal.nextLine()
        self.show_prompt()

    def handle_CTRL_D(self):
        self.terminal.loseConnection()

    def handle_CTRL_U(self):
        self.terminal.write(self.prompt)

    def handle_TAB(self):
        pass

class KurthAvatar(avatar.ConchUser):
    implements(interfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session':session.SSHSession})

    def openShell(self, protocol):
        server = insults.ServerProtocol(KurthProtocol, self)
        server.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(server))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError

    def eofReceived(self):
        pass

    def windowChanged(self, winSize):
        pass

    def closed(self):
        pass

class KurthRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarID, mind, *items):
        if interfaces.IConchUser in items:
            return items[0], KurthAvatar(avatarID), lambda: None
        else:
            log.msg('No supported interfaces found')
            log.err()
            pass

def generateRSAKeys():
    if not (os.path.isfile('keys/public.key') and
            os.path.isfile('keys/private.key')):
        print "Generating RSA keypair..."
        from Crypto import Random
        from Crypto.PublicKey import RSA
        KEY_LENGTH = 1024
        random_generator = Random.new().read
        rsaKey = RSA.generate(KEY_LENGTH, random_generator)
        privateKey = rsaKey.exportKey()
        publicKey = rsaKey.publickey().exportKey(format='OpenSSH')
        file('keys/public.key', 'w+b').write(publicKey)
        file('keys/private.key', 'w+b').write(privateKey)
        print "done."

if __name__ == '__main__':
    sshFactory = factory.SSHFactory()
    sshFactory.portal = portal.Portal(KurthRealm())
    users = {'user': 'user', 'root': 'root'}
    sshFactory.portal.registerChecker(
                    checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

    generateRSAKeys()
    with open('keys/public.key', 'r+b') as pub:
        pubblob = pub.read()
        sshFactory.publicKeys = {'ssh-rsa': Key.fromString(data=pubblob)}
    with open('keys/private.key', 'r+b') as priv:
        privblob = priv.read()
        sshFactory.privateKeys = {'ssh-rsa': Key.fromString(data=privblob)}

    reactor.listenTCP(2022, sshFactory)
    reactor.run()
