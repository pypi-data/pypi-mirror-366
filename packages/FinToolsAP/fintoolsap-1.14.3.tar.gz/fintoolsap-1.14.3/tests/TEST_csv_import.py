import os
import sys
import time
import numpy
import pandas
import pathlib
import datetime
import functools
import matplotlib.pyplot as plt

# add source directory to path
sys.path.insert(0, '../src/FinToolsAP/')

import LaTeXBuilder
import LocalDatabase
import PortfolioSorts
import UtilityFunctions

# set printing options
import shutil
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', shutil.get_terminal_size()[0])
pandas.set_option('display.float_format', lambda x: '%.3f' % x)

# directory for loacl wrds database
LOCAL_DB = pathlib.Path('/home/andrewperry/Documents')

def main():
    
    DW_DB_NAME = 'DisWindowDB'
    DW_DB_DIRECTORY = '/home/andrewperry/Nextcloud/Research/Discount Window'

    DB = LocalDatabase.LocalDatabase(save_directory = DW_DB_DIRECTORY, database_name = DW_DB_NAME)


if __name__ == '__main__':
    main()