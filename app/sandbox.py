# ./sandbox.py
import sys
import requests

from dotenv import dotenv_values

# Custom imports
import general_methods as gm

config = dotenv_values("./app/.env")


def main():
    str_ = "%ssdljfg;lsdfhgl'%s''%s'%ssdf%s"
    print(str_)
    ind = gm.find_all_strings(str_, "'%s'")
    print(ind)
    # [print(str_[x[0]:x[1]]) for x in ind]


if __name__ == '__main__':
    pass
    main()
