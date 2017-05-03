import math
import os
from .log_manager import logger
from six import print_

# global SHARD_MULTIPLES_BACK, MAX_SHARD_SIZE

# MAX_SHARD_SIZE = 4294967296  # 4Gb
# SHARD_MULTIPLES_BACK = 4


class ShardingTools():

    def __init__(self):
        self.MAX_SHARD_SIZE = 4294967296  # 4Gb
        self.SHARD_MULTIPLES_BACK = 4

    def get_optimal_shard_parametrs(self, file_size):
        shard_parameters = {}
        accumulator = 0
        shard_size = None
        while (shard_size is None):
            shard_size = self.determine_shard_size(file_size, accumulator)
            accumulator += 1
        shard_parameters["shard_size"] = str(shard_size)
        shard_parameters["shard_count"] = math.ceil(file_size / shard_size)
        shard_parameters["file_size"] = file_size
        return shard_parameters

    def determine_shard_size(self, file_size, accumulator):

        # Based on <https://github.com/aleitner/shard-size-calculator/blob/master/src/shard_size.c>

        hops = 0

        if (file_size <= 0):
            return 0
            # if accumulator != True:
            # accumulator  = 0
        logger.debug(accumulator)

        # Determine hops back by accumulator
        if ((accumulator - self.SHARD_MULTIPLES_BACK) < 0):
            hops = 0
        else:
            hops = accumulator - self.SHARD_MULTIPLES_BACK

        # accumulator = 10
        byte_multiple = self.shard_size(accumulator)

        check = file_size / byte_multiple
        # print_(check)
        if (check > 0 and check <= 1):
            while (hops > 0 and self.shard_size(hops) > self.MAX_SHARD_SIZE):
                if hops - 1 <= 0:
                    hops = 0
                else:
                    hops = hops - 1
            return self.shard_size(hops)

        # Maximum of 2 ^ 41 * 8 * 1024 * 1024
        if (accumulator > 41):
            return 0

            # return self.determine_shard_size(file_size, ++accumulator)

    def shard_size(self, hops):
        return (8 * (1024 * 1024)) * pow(2, hops)

    def sort_index(self, f1, f2):

        index1 = f1.rfind('-')
        index2 = f2.rfind('-')

        if index1 != -1 and index2 != -1:
            i1 = int(f1[index1:len(f1)])
            i2 = int(f2[index2:len(f2)])
            return i2 - i1

    def join_shards(self, shards_filepath, pattern, destination_file_path):
        # Based on <http://code.activestate.com/recipes/224800-simple-file-splittercombiner-module/>
        import re

        logger.info('Creating file', destination_file_path)

        bname = str((os.path.split(destination_file_path))[1]).decode('utf-8')
        bname_input = str((os.path.split(shards_filepath))[1]).decode('utf-8')
        bname2_input = bname_input

        print_("sciezka shardow" + shards_filepath + " " + destination_file_path)

        input_directory = str((os.path.split(shards_filepath))[0]).decode('utf-8')
        output_directory = str((os.path.split(destination_file_path))[0]).decode('utf-8')

        # bugfix: if file contains characters like +,.,[]
        # properly escape them, otherwise re will fail to match.
        for a, b in zip(['+', '.', '[', ']', '$', '(', ')'],
                        ['\+', '\.', '\[', '\]', '\$', '\(', '\)']):
            bname2 = bname2_input.replace(a, b)

        chunkre = re.compile(bname2_input + '-' + '[0-9]+')

        chunkfiles = []
        for f in os.listdir(str(input_directory).decode('utf-8')):
            logger.debug(f)
            if chunkre.match(f):
                chunkfiles.append(f)

        logger.info('Number of chunks', len(chunkfiles))
        chunkfiles.sort(self.sort_index)
        logger.info(chunkfiles)
        data = ''
        for f in chunkfiles:

            try:
                logger.info('Appending chunk',
                            os.path.join(str(input_directory), f))
                data += open(str(str(input_directory) + "/" + str(f)).decode('utf-8'), 'rb').read()
                logger.info(str(input_directory) + "/" + str(f) +
                            "katalog wejsciowy")
            except (OSError, IOError, EOFError) as e:
                logger.error(e)
                continue

        try:
            logger.info(str(output_directory) + "katalog wyjsciowy")
            f = open(str(str(output_directory) + "/" + str(bname)).decode('utf-8'), 'wb')
            f.write(data)
            f.close()
        except (OSError, IOError, EOFError) as e:
            raise ShardingException(str(e))

        logger.info('Wrote file', bname)
        return 1


class ShardingException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
