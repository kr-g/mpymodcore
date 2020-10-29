"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""


from .channel import FiberChannel, FiberChannelEmptyException


class FiberStreamIO(object):
    def open(self):
        pass

    # reading from fiber stream
    # return None if no data available
    # return zero length bytes() for EOF
    def read(self, fchan):
        pass

    # writing into fiber stream
    # return True is more data is available
    def write(self, fchan):
        pass

    def close(self):
        pass


class FiberStream(object):
    def __init__(self, channel=None):
        self._closable = channel == None
        if channel == None:
            channel = FiberChannel()
        self.channel = channel
        self._reader = None
        self._writer = None

    def close(self):
        if self._closable == True:
            self.channel.close()
            self.channel = None
        # close ???
        if self._reader != None:
            self._reader.close()
        if self._writer != None:
            self._writer.close()

    def reader(self, fstreamio=None):
        self._reader = fstreamio

    def writer(self, fstreamio=None):
        self._writer = fstreamio

    # if no reader is defined return chunk
    def read(self):
        try:
            if self._reader == None:
                return self.channel.pop()
            return self._reader.read(self.channel)
        except FiberChannelEmptyException:
            return bytes()

    # if given write data to channel
    def write(self, data=None):
        if data != None:
            self.channel.push(data)
        return self._writer.write(self.channel)
