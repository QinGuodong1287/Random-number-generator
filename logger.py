import io
import traceback

errorLogFile = r"error.log"
errorLogBuffer = io.StringIO()

def flushErrorToBuffer():
    global errorLogBuffer
    print("Call stack:", file=errorLogBuffer)
    traceback.print_stack(file=errorLogBuffer)
    traceback.print_exc(file=errorLogBuffer)
    errorLogBuffer.write("\n")
    # errorLogBuffer.truncate()
    # errorLogBuffer.seek(0)

def logError():
    global errorLogFile, errorLogBuffer
    errorLogBuffer.seek(0)
    errorLog = errorLogBuffer.read()
    if not errorLog:
        return
    with open(errorLogFile, "w") as log:
        log.write(errorLog)

def closeBuffer(ensureWrittenInFile=False):
    if ensureWrittenInFile:
        logError()
    global errorLogBuffer
    errorLogBuffer.close()

def logCall(func, default=None, error_handler=None, *args, **kwargs):
    """This function calls a function without raising error.
    Be cautious when using it."""
    try:
        res = func(*args, **kwargs)
    except Exception as e:
        flushErrorToBuffer()
        res = default
        if callable(error_handler):
            error_handler(e)
    return res

class LogCall:
    """This class calls a function without raising error.
    Be cautious when using it."""
    def __init__(self, func, default=None, error_handler=None):
        self.func = func
        self.default = default
        self.error_handler = error_handler

    def __call__(self, *args, **kwargs):
        try:
            res = self.func(*args, **kwargs)
        except Exception as e:
            flushErrorToBuffer()
            res = self.default
            if callable(self.error_handler):
                self.error_handler(e)
        return res
