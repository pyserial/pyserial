
class FileLike:
    """An abstract file like class.
    
    This class implements readline and readlines based on read and
    writelines based on write.
    This class is used to provide the above functions for to Serial
    port objects.
    
    Note that when the serial port was opened with _NO_ timeout that
    readline blocks until it sees a newline (or the specified size is
    reached) and that readlines would never return and therefore
    refuses to work (it raises an exception in this case)!
    """

    def read(self, size): raise NotImplementedError
    def write(self, s): raise NotImplementedError

    def readline(self, size=None):
        """read a line which is terminated with '\\n' or until timeout"""
        line = ''
        while 1:
            c = self.read(1)
            if c:
                line += c   #not very efficient but lines are usually not that long
                if c == '\n':
                    break
                if size is not None and len(line) >= size:
                    break
            else:
                break
        return line

    def readlines(self, sizehint=None):
        """read alist of lines, until timeout
        sizehint is ignored"""
        if self.timeout is None:
            raise ValueError, "Serial port MUST have enabled timeout for this function!"
        lines = []
        while 1:
            line = self.readline()
            if line:
                lines.append(line)
                if line[-1] != '\n':
                    break
            else:
                break
        return lines

    def xreadlines(self, sizehint=None):
        """just call readlines - just here for compatibility"""
        return self.readlines()

    def writelines(self, sequence):
        for line in sequence:
            self.write(line)

    def flush(self):
        """map flush to flushOutput, ignore  exception when that
        method is not available"""
        try:
            self.flushOutput()
        except NameError:
            pass

