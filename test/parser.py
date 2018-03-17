from optparse import OptionParser
import inspect, sys, os

usage = ""
process = os.path.basename(inspect.getfile(sys.modules["__main__"]))
if process == "download_torrent_test.py":
    usage = """usage: %prog [options]
        %prog -o -s"""
elif process == "make_torrent_test.py":
    usage = """usage: %prog [options]
        %prog -f -s -y"""
elif "rsync" in process:
    usage = """usage: %prog [options]
        %prog -f -s -p"""


parser = OptionParser(usage=usage)

parser.add_option("-i", "--ip", dest="ip",
        help="host ip, default localhost")
parser.add_option("-o", "--torrent", dest="torrent",
        help="torrent file")
parser.add_option("-s", "--save", dest="save",
        help="file save path")
parser.add_option("-t", "--time", dest="time",
        help="set seed time")
parser.add_option("-f", "--file", dest="file",
        help="source file")
parser.add_option("-k", "--tracker", dest="tracker",
        help="tracker url")
parser.add_option("-p", "--password", dest="password",
        help="rsync password")
parser.add_option("-y", "--type", dest="type",
        help="make torrent type, default file, options[file|vhd]")
parser.add_option("-d", "--taskid", dest="taskid",
        help="task id")

