# -*- coding: utf-8 -*-

import os

import errno
from . import pingparser
import platform
import re
import tempfile

from os.path import expanduser


class Tools:
    def isWritable(self, path):
        try:
            testfile = tempfile.TemporaryFile(dir=path)
            testfile.close()
        except OSError as e:
            if e.errno == errno.EACCES:  # 13
                return False
            e.filename = path
            raise
        return True

    def check_email(self, email):
        if not re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email):
            return False
        else:
            return True

    def measure_ping_latency(self, destination_host):
        ping_latency = str(os.system(
            'ping ' + ('-n 1 ' if platform.system().lower() == 'windows' else '-c 1 ') + str(destination_host)))

        ping_data_parsed = pingparser.parse(ping_latency)

        return ping_data_parsed

    def human_size(self, size_bytes):
        """
        format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
        Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
        e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
        From: <http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size>
        """
        if size_bytes == 1:
            # because I really hate unnecessary plurals
            return "1 byte"

        precision = 0
        suffixes_table = [('bytes', 0), ('KB', 0), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2)]

        suffix = ''
        num = float(size_bytes)
        for suffix, precision in suffixes_table:
            if num < 1024.0:
                break
            num /= 1024.0

        if precision == 0:
            formatted_size = '%d' % num
        else:
            formatted_size = str(round(num, ndigits=precision))

        return '%s %s' % (formatted_size, suffix)

    def get_home_user_directory(self):
        home = expanduser('~')
        return str(home)
