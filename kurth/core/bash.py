#!/usr/bin/env python

from commands import shortcommands

class Shell(object):

    env = {'PWD': '/', 'OLDPWD': '/', '?': 0, '0': 'bash'}

    def __init__(self, fs, user, source, terminal):
        self.fs = fs
        self.terminal = terminal
        self.env['USER'] = user
        self.env['SOURCE'] = source

        # TODO: Figure out how to change this if the endpoint changes size
        self.env['LINES'] = terminal.termSize.y
        self.env['COLUMNS'] = terminal.termSize.x

    def call_function(self, func, args):
        getattr(shortcommands, func)(self.terminal, self.fs, args, self.env)

    def cd(self, args):
        if len(args) == 1:
            for path in [args[0], self.env['PWD'] + args[0]]:
                ret = self.fs.check_dir_in_filesystem(path)
                if ret:
                    self.env['OLDPWD'] = self.env['PWD']
                    self.env['PWD'] = path
                    self.env['?'] = 0
                    return
        self.terminal.write('bash: cd: %s: No such file or directory'% args[0])
        self.env['?'] = 1
        self.terminal.nextLine()

    def line_in(self, line):
        split = line.split(' ')
        command = split[0]
        if command == 'cd':
            self.cd(split[1:])
        elif command:
            try:
                exitcode = self.call_function(command, split[1:])
            except AttributeError:
               self.terminal.write('bash: %s: not found\n' % command)
