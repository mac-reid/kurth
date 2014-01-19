#!/usr/bin/env python

from commands import shortcommands

class Shell(object):

    env_vars = {'PWD': '/', 'OLDPWD': '/', '?': 0, '0': 'bash'}

    def __init__(self, fs, user, source, terminal):
        self.fs = fs
        self.terminal = terminal
        self.env_vars['USER'] = user
        self.env_vars['SOURCE'] = source
        self.env_vars['LINES'] = terminal.termSize.y
        self.env_vars['COLUMNS'] = terminal.termSize.x

    def terminal_write(self, message):
        # For some reason the print keyword is printing 2 empty lines to the
        # log. The log should be clean as possible so we use stdout.write.
        self.terminal.write(message)
        self.env_vars['?'] = 1

    def call_function(self, func, args):
        getattr(shortcommands, func)(self.terminal, self.fs, args,
                                            self.env_vars, self.terminal_write)

    def cd(self, args):
        if len(args) == 1:
            ret = self.fs.check_dir_in_filesystem(args[0])
            if ret:
                self.env_vars['OLDPWD'] = self.env_vars['PWD']
                self.env_vars['PWD'] = args[0]
                self.env_vars['?'] = 0
                return
        self.terminal_write('bash: cd: %s: No such file or directory'% args[0])
        self.terminal.nextLine()

    def line_in(self, line):
        split = line.split(' ')
        command = split[0]
        if command == 'cd':
            self.cd(split[1:])
        elif command:
            #try:
                exitcode = self.call_function(command, split[1:])
            #except AttributeError:
             #   self.terminal_write('bash: %s: not found' % command)
