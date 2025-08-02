#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/13 10:28 
# @File    : __init__.py.py

from ._version import __version__
import os


def check_version():
    os.system("pip index versions sagea --pre")


import pathlib

from sagea.pysrc.data_class.__SHC__ import SHC
from sagea.pysrc.data_class.__GRD__ import GRD

import sagea.pysrc.load_file as load

from sagea.pysrc.auxiliary.MathTool import MathTool
from sagea.pysrc.auxiliary.TimeTool import TimeTool
from sagea.pysrc.auxiliary.FileTool import FileTool
import sagea.pysrc.auxiliary.Preference as Preference

from sagea.pysrc.data_collection.collect_auxiliary import collect_auxiliary as collect_auxiliary_data
