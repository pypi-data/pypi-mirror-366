"""GUI for application deployment and monitoring of servers and 
applications related to specific apparatuses.
"""
__version__ = 'v1.1.1 2025-07-30'# added --interactive

import sys, os, argparse
from qtpy.QtWidgets import QApplication
from . import manman, helpers

#``````````````````Main```````````````````````````````````````````````````````
def main():
    global pargs
    parser = argparse.ArgumentParser('python -m manman',
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      epilog=f'Version {manman.__version__}')
    parser.add_argument('-c', '--configDir', help=\
      ('Root directory of config files, one config file per apparatus, '
      'if None, then ./config directory will be used'))
    parser.add_argument('-C', '--condensed', action='store_true', help=\
      'Condensed arrangement of tables: no headers, narrow columns')
    parser.add_argument('-i', '--interactive', default=False, action='store_true', help=
      'Select files interactively')
    parser.add_argument('-t', '--interval', default=10., help=\
      'Interval in seconds of periodic checking. If 0 then no checking')
    parser.add_argument('-v', '--verbose', action='count', default=0, help=\
      'Show more log messages (-vv: show even more).')
    parser.add_argument('-z', '--zoomin', help=\
      'Zoom the application window by a factor, factor must be >= 1')
    parser.add_argument('apparatus', nargs='*', help=\
      ('Path of apparatus config files, can include wildcards. '
       'If None, then an interactive dialog will be opened to select files.')),
    pargs = parser.parse_args()
    helpers.Verbose = pargs.verbose
    if pargs.configDir is None and len(pargs.apparatus) == 0:
        pargs.configDir = 'config'
    manman.Window.pargs = pargs# transfer pargs to manman module

    # handle the --zoomin
    if pargs.zoomin is not None:
        os.environ["QT_SCALE_FACTOR"] = pargs.zoomin

    # arrange keyboard interrupt to kill the program
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # start GUI
    app = QApplication(sys.argv)
    window = manman.Window()
    window.show()
    app.exec_()
    print('Application exit')

if __name__ == '__main__':
    main()

