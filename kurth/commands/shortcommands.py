#!/usr/bin/env python

from util import columnize

def cat(terminal, fs, args, env_variables, write):
    for arg in args:
        write(fs.read(arg))

def clear(terminal, fs, *_):
    terminal.reset()

def echo(terminal, fs, args, env_variables, write):
    words = []
    for arg in args:
        if arg.startswith('$'):
            word = env_variables.get(arg[1:], '')
            if word:
                words.add(word)
        else:
            words.add(arg)
    write(' '.join(words))
    terminal.nextLine()

def exit(terminal, fs, *_):
    terminal.loseConnection()

def ls(terminal, fs, args, env_variables, write):
    data = fs.get_contents_of_dir(env_variables['PWD'])
    data = sorted(data['files'] + data['dirs'])
    write(columnize.columnize(data, displaywidth=env_variables['COLUMNS']))

def pwd(terminal, fs, env_variables, write):
    write(env_variables['PWD'])

def w(terminal, fs, args, env_variables, write):
    if env_variables['COLUMNS'] <= 70:
        write('w: %i column window is too narrow' % env_variables['COLUMNS'])
        terminal.nextLine()

def who(terminal, fs, args, env_variables, write):
    import time
    template = '%(name)s   %(line)s          %(time)s %(comment)s'
    localtime = time.strftime('%m-%e-%y %H:%M', time.localtime())
    write(template % {'name': env_variables['USER'],
                                'line': 'pts/7',
                                'time': localtime,
                                'comment': env_variables['SOURCE']})
    terminal.nextLine()

def whoami(terminal, fs, args, env_variables, write):
    write(env_variables['USER'])
    terminal.nextLine()