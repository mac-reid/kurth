import re
import sys
import time
import socket
import urllib2


def is_valid_ip(addr):
    """
    Thanks to @Markus Jarderot on Stack Overflow
    http://stackoverflow.com/a/319293
    """
    return is_valid_ipv4(addr) or is_valid_ipv6(addr)


def is_valid_ipv4(addr):
    """
    Thanks to @Markus Jarderot on Stack Overflow
    http://stackoverflow.com/a/319293
    """
    pattern = re.compile(r"""
        ^
        (?:
            # Dotted variants:
            (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
                0x0*[0-9a-f]{1,2}  # Hex 0x0 - 0xFF (possible leading 0's)
            |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
            )
            (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
                0x0*[0-9a-f]{1,2}
            |
                0+[1-3]?[0-7]{0,2}
                )
            ){0,3}
        |
            0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
            0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
            # Decimal notation, 1-4294967295:
            429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
            42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
            4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(addr) is not None


def is_valid_ipv6(addr):
    """
    Thanks to @Markus Jarderot on Stack Overflow
    http://stackoverflow.com/a/319293
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most 4 hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(addr) is not None


def ip_is_resolvable(ip_addr):
    try:
        return socket.gethostbyaddr(ip_addr)
    except (socket.herror, socket.gaierror):
        return None


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    if percent:
        equals = '=' * int(percent * 39)
    else:
        equals = ''
    equals += '>'
    space = ' ' * (39 - len(equals))
    percentage = '[%s%s] ' % (equals, space)
    str_percent = str(int(percent * 100)) + '%'
    text = "{:<4}{} {:,}\r".format(str_percent, percentage, bytes_so_far)

    # slick way to print text on a single line repeatedly
    print text,

    if bytes_so_far >= total_size:
        print '\n'


def chunk_read(response, chunk_size=8192, report_hook=None):
    total_size = int(response.info().getheader('Content-Length').strip())
    bytes_so_far = 0

    while True:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

    return bytes_so_far


def num_fmt(num):
    # ignore anything smaller than a kilobyte
    num /= 1024.0
    if num < 1024.0:
        return

    for x in ['K', 'M', 'G']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'T')


def wget(args):
    url = args[0]
    url_s = url.split('/')[0]
    if not '://' in url:
        url = 'http://' + url
    localtime = str(time.strftime('%Y-%m-%e %H:%M:%S', time.localtime()))
    print '--%s--  %s' % (localtime, url)
    if is_valid_ip(url):
        host = url_s
    else:
        host = url_s + ' (%s)' % url_s
        sys.stdout.write('Resolving %s... ' % host)
        addr = ip_is_resolvable(url_s)
        if not addr:
            print 'failed: Name or service not known.'
            print 'wget: unable to resolve host address `%s\'' % url_s
            return
        else:
            print addr[2][0]
            host = host + '|%s|:80' % addr[2][0]
    sys.stdout.write('Connecting to %s... ' % host)
    try:
        connection = urllib2.urlopen(url)
    except:  # make this smarter
        print 'failed.'
        return
    print 'connected.'
    print 'HTTP request sent, awaiting response... %s %s' % \
                                    (connection.code, connection.msg)
    ddl_size = connection.info().getheader('content-length')
    size_fmt = num_fmt(int(ddl_size))
    if size_fmt:
        text = 'Length: %s (%s) [%s]' % (ddl_size, num_fmt(int(ddl_size)),
                                         connection.info().type)
    else:
        text = 'Length: %s [%s]' % (ddl_size, connection.info().type)
    print text

    ddl_file = connection.info().getheader('content-disposition')
    if not ddl_file:
        ddl_file = urllib2.urlparse.urlsplit(url)[2].split('/')
        ddl_file = ddl_file[len(ddl_file) - 1]
    if not ddl_file:
        ddl_file = 'index.html'
    print "Saving to: '%s'\n" % ddl_file

    localtime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    speed = '6.59 MB/s'
    chunk_read(connection, report_hook=chunk_report)
    print "%s (%s) - '%s' saved [%s/%s]" % (localtime, speed, ddl_file,
                                            ddl_size, ddl_size)
    print ''

# for testing
# wget(['www.csl.mtu.edu/~mareid/files/echo.sh'])
