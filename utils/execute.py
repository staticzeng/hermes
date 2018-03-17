#!/usr/bin/python
import time
import subprocess, shlex
from error import *

def simp_popen(argv):
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True, close_fds=True)
    #code = p.wait()
    ret = p.communicate()
    (stdout, stderr) = ret
    p.stdout.close()
    p.stdin.close()
    return p.returncode, stdout.strip("\n").strip(" "), stderr

def get_cmd_path(cmd):
    whichcmd = "which " + cmd
    code, ret, errmsg = simp_popen(whichcmd)
    if code == 0:
        return ret
    else:
        raise ValueError("Cann't find command:%s[%s]" % (cmd, errmsg))

def execute(cmd, params=[], _type=None, attempts=1, delay_on_retry=0, input=None, progress_obj=None, _output=None):
    time_start = time.time()
    while attempts > 0:
        _PIPE = subprocess.PIPE
        attempts -= 1
        cmd = cmd.strip()
        try:
            if cmd != "":
                cmd_list = cmd.split(" ")
                tmpcmd = get_cmd_path(cmd_list[0])
                if len(cmd_list) > 1:
                    runcmd = tmpcmd + " " + cmd.split(" ", 1)[1]
                else:
                    runcmd = tmpcmd
                if isinstance(params, (str,unicode)):
                    params = [params]
            else:
                runcmd = cmd
            
            cmdstr = " ".join([runcmd]+params)
            #obj = subprocess.Popen(" ".join([runcmd] + params),
            obj = subprocess.Popen(shlex.split(str(cmdstr)),
                                   stdin=_PIPE,
                                   stdout=_output if _output else _PIPE,
                                   stderr=_output if _output else _PIPE,
                                   #stderr=_PIPE,
                                   #close_fds=True,
                                   #preexec_fn=os.setpgrp,
                                   #shell=True)
                                   shell=False)
            #print "pid:", obj.pid
            if progress_obj:
                progress_obj.pid = obj.pid
            result = None
            if input is not None:
                result = obj.communicate(input)
            else:
                result = obj.communicate()
            obj.stdin.close()
            _returncode = obj.returncode
            if _returncode:
                (stdout, stderr) = result
                raise ShellError(
                        code=_returncode,
                        msg=stdout,
                        err=stderr,
                        cmd=runcmd)
            if _type is not None:
                try:
                    result = _type("".join(result).strip("\n").strip())
                except:
                    raise ValueError("Type convert error:%s, value:%s" % (str(_type), result))
            else:
                print "execute result:", result
                result = (result[0])#give up stderr
                if result:
                    result = "".join(result).strip("\n").strip()
                else:
                    result = ''
            return result
                
        except ShellError:
            if not attempts:
                raise
            else:
                if delay_on_retry:
                    time.sleep(delay_on_retry)
if __name__ == "__main__":
    pass
