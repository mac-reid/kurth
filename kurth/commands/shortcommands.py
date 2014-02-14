#!/usr/bin/env python


def cat(terminal, fs, args, _):
    for arg in args:
        terminal.write(fs.read(arg))


def clear(terminal, *_):
    terminal.reset()


def echo(terminal, _, args, env_variables):
    words = []
    for arg in args:
        if arg.startswith('$'):
            word = env_variables.get(arg[1:], '')
            if word:
                words.append(word)
        else:
            words.append(arg)
    terminal.write(' '.join(words))
    terminal.nextLine()


def exit(terminal, *_):
    terminal.loseConnection()


def ls(terminal, _, __, env_variables):
    from util import columnize
    data = fs.get_contents_of_dir(env_variables['PWD'])
    data = sorted(data['files'] + data['dirs'])
    terminal.write(columnize.columnize(data, env_variables['COLUMNS']))


def pwd(terminal, _, __, env_variables):
    terminal.write(env_variables['PWD'])
    terminal.nextLine()


def w(terminal, _, __, env_variables):
    if env_variables['COLUMNS'] <= 70:
        env_variables['?'] = 1
        terminal.write('w: %i column window is too narrow' %
                                                    env_variables['COLUMNS'])
        terminal.nextLine()


def who(terminal, _, __, env_variables):
    import time
    template = '%(name)s   %(line)s          %(time)s %(comment)s'
    localtime = time.strftime('%m-%e-%y %H:%M', time.localtime())
    terminal.write(template % {'name': env_variables['USER'],
                               'line': 'pts/7',
                               'time': localtime,
                               'comment': env_variables['SOURCE']})
    terminal.nextLine()


def whoami(terminal, _, __, env_variables):
    terminal.write(env_variables['USER'])
    terminal.nextLine()
