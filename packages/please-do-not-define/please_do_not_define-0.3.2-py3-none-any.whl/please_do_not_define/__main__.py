from please_do_not_define.all_name import get_name_usages_with_location
from please_do_not_define.invalid_name import _is_illegal_name as is_illegal_name
from please_do_not_define.__version__ import __version__
import sys
import os

def analyse_code(code):
    all_name = get_name_usages_with_location(code)
    illegal_name_dict = {}
    for key, value in all_name.items():
        if is_illegal_name(key):
            illegal_name_dict[key] = value
    return illegal_name_dict

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '-h'):
    sys.stderr.write(
        '''Usage:
    checkname filename: analyse the name in the python code file
    checkname -s code: analyse the name in the code
    checkname -h: for help
    checkname -v: show the version''')

elif len(sys.argv) == 2 and sys.argv[1] == '-v':
    print("version:", __version__)

elif len(sys.argv) == 2 and sys.argv[1] not in ("-h", "-v", "-s"):
    try:
        with open(sys.argv[0], encoding='utf-8') as f:
            illegal_name_dict = analyse_code(f.read())
            if len(illegal_name_dict) == 0:
                print("no illegal name")
            else:
                print("found the illegal name below:", end="\n\n", file=sys.stderr)
                for key, value in illegal_name_dict:
                    print("name", key, "at",
                          os.path.abspath(sys.argv[1]), "line",
                          value[0], "offset", value[1], file=sys.stderr)
                print("please don't try to define a female", file=sys.stderr)
    except Exception as e:
        sys.stderr.write(
            f"""cannot analyse file {sys.argv[1]}: {str(e)}
please ensure:
    1 the file is exist and encode with "utf-8"
    2 the file is a python code""")

elif len(sys.argv) == 3 and sys.argv[0] == "-s":
    try:
        illegal_name_dict = analyse_code(sys.argv[2])
        if len(illegal_name_dict) == 0:
            print("no illegal name")
        else:
            print("found the illegal name below:", end="\n\n", file=sys.stderr)
            for key, value in illegal_name_dict:
                print("name", key, "at",
                "input", "line",
                value[0], "offset", value[1], file=sys.stderr)
            print("please don't try to define a female", file=sys.stderr)
    except Exception as e:
        sys.stderr.write(
            f"""code wrong: {str(e)}""")
else:
    sys.stderr.write(
        f"""Unknown for command {" ".join(sys.argv)}
Use checkname -h for help.""")
