Ecode = {
        "VtransError":          100000,
        "OtherError":           100001,
        "InvalidParamError":    100100,
        "ShellError":           100200,
        "VhdutilError":         100300,
        "RsyncError":           100400,
        "TaskError":            100500,
        "CancelTaskError":      100501,
        "TaskNotfoundError":    100502,
        }


class VtransError(Exception):
    def code(self):
        return Ecode.get(self.__class__.__name__, 0)

class OtherError(Exception):
    '''some undefined error'''
    @classmethod
    def code(self):
        return Ecode["OtherError"]

class InvalidParamError(VtransError):
    pass

class ShellError(VtransError):
    def __init__(self, code, msg, err, cmd):
        self._code = code
        self.msg = msg
        self.err = err
        self.cmd = cmd
        message = ('\n\tCommand:%(cmd)s\n\tExit code: %(code)s\n'
                    '\tStdout: %(msg)r\n'
                    '\tStderr: %(err)r') % locals()
        super(ShellError, self).__init__(message)

class VhdutilError(VtransError):
    pass

class RsyncError(VtransError):
    pass

class TaskError(VtransError):
    pass

class CancelTaskError(TaskError):
    pass

class TaskNotfoundError(TaskError):
    pass
