"""GUI for application deployment and monitoring of servers and 
applications related to specific apparatus.
"""
__version__ = 'v1.0.4 2025-06-01'# Minimal row height set to 20.
#TODO: xdg_open does not launch if other editors not running. 

import sys, os, time, subprocess, argparse, threading
from functools import partial
from importlib import import_module

from qtpy import QtWidgets as QW, QtGui, QtCore

from . import helpers as H
from . import detachable_tabs

#``````````````````Constants``````````````````````````````````````````````````
ManCmds =       ['Check',    'Start',    'Stop',     'Command']
AllManActions = ['Check All','Start All','Stop All', 'Edit', 'Delete',
                'Condense', 'Uncondense']
Col = {'Applications':0, 'status':1, 'action':2, 'response':3}
BoldFont = QtGui.QFont("Helvetica", 14, QtGui.QFont.Bold)
FilePrefix = 'apparatus'
MinimalRowHeight = 20
#``````````````````Helpers````````````````````````````````````````````````````
def select_files_interactively(directory, title=f'Select {FilePrefix}*.py files'):
    dialog = QW.QFileDialog()
    dialog.setFileMode( QW.QFileDialog.FileMode() )
    ffilter = f'pypet ({FilePrefix}*.py)'
    files = dialog.getOpenFileNames( None, title, directory, ffilter)[0]
    return files

def create_folderMap():
    # create map of {folder1: [file1,...], folder2...} from pargs.apparatus
    #print(f'c,a: {Window.pargs.configDir, Window.pargs.apparatus}')
    folders = {}
    if Window.pargs.configDir is None:
        files = [os.path.abspath(i) for i in Window.pargs.apparatus]
    else:
        absfolder = os.path.abspath(Window.pargs.configDir)
        if len(Window.pargs.apparatus) == 0:
            files = select_files_interactively(absfolder)
        else:
            files = [absfolder+'/'+i for i in Window.pargs.apparatus]
    for f in files:
        folder,tail = os.path.split(f)
        if not (tail.startswith(FilePrefix) and tail.endswith('.py')):
            H.printe(f'Config file should have prefix {FilePrefix} and suffix ".py"')
            sys.exit(1)
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(tail)

    # sort the file lists
    for folder in folders:
        folders[folder].sort()
    return folders

def launch_default_editor(configFile):
    cmd = f'xdg-open {configFile}'
    H.printi(f'Launching editor: {cmd}')
    subprocess.call(cmd.split())

def is_process_running(cmdstart):
    try:
        subprocess.check_output(["pgrep", '-f', cmdstart])
        return True
    except subprocess.CalledProcessError:
        return False
#``````````````````Table Widget```````````````````````````````````````````````
def current_mytable():
    return Window.tabWidget.currentWidget()
class MyTable(QW.QTableWidget):
    def __init__(self, folder, fname, tabName):
        super().__init__()
        mname = fname[:-3]
        H.printv(f'importing {mname}')
        try:
            module = import_module(mname)
        except SyntaxError as e:
            H.printe(f'Syntax Error in {fname}: {e}')
            sys.exit(1)
        H.printv(f'imported {mname} {module.__version__}')
        self.startup = module.startup
        self.configFile = folder+'/'+fname
        self.setColumnCount(len(Col))
        self.setHorizontalHeaderLabels(Col.keys())
        self.verticalHeader().setMinimumSectionSize(MinimalRowHeight)
        self.manRow = {}
        try:
            H.printv(f'title: {module.title}')
            wideRow(self, 0, module.title)
        except:
            wideRow(self, 0,'Applications')

        # Create AllManActions combobox in top row
        sb = QW.QComboBox()
        sb.addItems(AllManActions)
        sb.activated.connect(self.tableWideAction)
        sb.setToolTip('Execute selected action for all applications of this tab')
        self.setCellWidget(0, Col['action'], sb)

        # Set up all rows 
        operationalManager = True
        for manName,props in self.startup.items():
            rowPosition = self.rowCount()
            if manName.startswith('tst_'):
                if operationalManager:
                    operationalManager = False
                    wideRow(self, rowPosition,'Test Apps')
                    rowPosition += 1
            insertRow(self, rowPosition)
            self.manRow[manName] = rowPosition
            item = QW.QTableWidgetItem(manName)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            try:    item.setToolTip(props['help'])
            except: pass
            self.setItem(rowPosition, Col['Applications'], item)
            if operationalManager:
                item.setFont(BoldFont)
                item.setBackground(QtGui.QColor('lightCyan'))
            self.setItem(rowPosition, Col['status'],
              QW.QTableWidgetItem('?'))
            sb = QW.QComboBox()
            sb.addItems(ManCmds)
            sb.activated.connect(partial(self.manAction, manName))
            try:    sb.setToolTip(f'Control of {manName}')
            except: pass
            self.setCellWidget(rowPosition, Col['action'], sb)
            self.setItem(rowPosition, Col['response'],
              QW.QTableWidgetItem(''))

        # Set up headers
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        if Window.pargs.condensed:
            self.set_headersVisibility(False)

    def contextMenuEvent(self, event):
        menu = QW.QMenu()
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        row = index.row()
        cmds = AllManActions if row == 0 else ManCmds
        for cmd in cmds:
            print(f'addAction: {cmd}')
            action = menu.addAction(cmd)
        res = menu.exec_(event.globalPos())
        manName = index.data()
        if res is None:
            return
        cmd = res.text()
        if row == 0:
            cmdIdx = AllManActions.index(cmd)
            print(f'res@{row},{cmdIdx}:{manName}')
            self.tableWideAction(cmdIdx)
        else:
            cmdIdx = ManCmds.index(cmd)
            print(f'res@{row},{cmdIdx}:{manName}')
            self.manAction(manName, cmdIdx)

    def manAction(self, manName:str, cmdIdx:int):
        # Execute action, indexed by cmdIdx
        try:
            cmd = ManCmds[cmdIdx]
        except Exception as e:
            H.printw(f'ManName,cmdIdx = {manName,cmdIdx}')
            return
        rowPosition = self.manRow[manName]
        H.printvv(f'manAction: {manName, cmd}')
        startup = self.startup
        cmdstart = startup[manName]['cmd']
        process = startup[manName].get('process', f'{cmdstart}')

        if cmd == 'Check':
            H.printvv(f'checking process {process} ')
            status = ['not running','is started'][is_process_running(process)]
            item = self.item(rowPosition,Col['status'])
            if not 'tst_' in manName:
                color = 'lightGreen' if 'started' in status else 'pink'
                item.setBackground(QtGui.QColor(color))
            item.setText(status)

        elif cmd == 'Start':
            self.item(rowPosition, Col['response']).setText('')
            if is_process_running(process):
                txt = f'Is already running manager {manName}'
                #print(txt)
                self.item(rowPosition, Col['response']).setText(txt)
                return
            H.printv(f'starting {manName}')
            item = self.item(rowPosition, Col['status'])
            if not 'tst_' in manName:
                item.setBackground(QtGui.QColor('lightYellow'))
            item.setText('starting...')
            path = startup[manName].get('cd')
            H.printi('Executing commands:')
            if path:
                path = path.strip()
                expandedPath = os.path.expanduser(path)
                try:
                    os.chdir(expandedPath)
                except Exception as e:
                    txt = f'ERR: in chdir: {e}'
                    self.item(rowPosition, Col['response']).setText(txt)
                    return
                print(f'cd {os.getcwd()}')
            print(cmdstart)
            expandedCmd = os.path.expanduser(cmdstart)
            cmdlist = expandedCmd.split()
            shell = startup[manName].get('shell',False)
            H.printv(f'popen: {cmdlist}, shell:{shell}')
            try:
                proc = subprocess.Popen(cmdlist, shell=shell, #close_fds=True,# env=my_env,
                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except Exception as e:
                H.printv(f'Exception: {e}') 
                self.item(rowPosition, Col['response']).setText(str(e))
                return
            Window.timer.singleShot(5000,partial(self.deferredCheck,(manName,rowPosition)))

        elif cmd == 'Stop':
            self.item(rowPosition, Col['response']).setText('')
            H.printv(f'stopping {manName}')
            cmd = f'pkill -f "{process}"'
            H.printi(f'Executing:\n{cmd}')
            os.system(cmd)
            time.sleep(0.1)
            self.manAction(manName, ManCmds.index('Check'))

        elif cmd == 'Command':
            try:
                cd = startup[manName]['cd']
                cmd = f'cd {cd}; {cmdstart}'
            except Exception as e:
                cmd = cmdstart
            print(f'Command in row {rowPosition}:\n{cmd}')
            self.item(rowPosition, Col['response']).setText(cmd)
            return

    def set_headersVisibility(self, visible:bool):
        #print(f'set_headersVisibility {visible}')
        #self.setColumnWidth(Col['action'], 40)
        self.horizontalHeader().setVisible(visible)
        self.verticalHeader().setVisible(visible)

    def tableWideAction(self, cmdidx:int):
        # Execute table-wide action
        #print(f'tableWideAction: {cmdidx}')
        if cmdidx == AllManActions.index('Edit'):
            launch_default_editor(self.configFile)
        elif cmdidx == AllManActions.index('Delete'):
            idx = Window.tabWidget.currentIndex()
            tabtext = Window.tabWidget.tabText(idx)
            H.printi(f'Deleting {idx,tabtext}')
            del Window.tableWidgets[tabtext]
            Window.tabWidget.removeTab(idx)
            self.deleteLater()# it is important to properly delete the associated widget
        elif cmdidx == AllManActions.index('Condense'):
            self.set_headersVisibility(False)
        elif cmdidx == AllManActions.index('Uncondense'):
            self.set_headersVisibility(True)
        else:
            for manName in self.startup:
                #print(f'man {manName,cmdidx}')
                if manName.startswith('tst') and cmdidx != ManCmds.index('Check'):
                    continue
                self.manAction(manName, cmdidx)

    def deferredCheck(self, args):
        manName,rowPosition = args
        self.manAction(manName, ManCmds.index('Check'))
        if 'start' not in self.item(rowPosition, Col['status']).text():
            self.item(rowPosition, Col['response']).setText('Failed to start')

#``````````````````Main Window````````````````````````````````````````````````
class Window(QW.QMainWindow):# it may sense to subclass it from QW.QMainWindow
    pargs = None
    tableWidgets = {}
    timer = QtCore.QTimer()

    def __init__(self):
        super().__init__()
        H.Verbose = Window.pargs.verbose
        folders = create_folderMap()
        if len(folders) == 0:
            sys.exit(1)
        H.printi(f'Configuration files: {folders}')
        self.setWindowTitle('manman')

        # Create tabWidget
        Window.tabWidget = detachable_tabs.DetachableTabWidget()
        Window.tabWidget.currentChanged.connect(periodicCheck)
        self.setCentralWidget(Window.tabWidget)
        H.printv(f'tabWidget created')

        # Add tables, configured from files, to tabs
        for folder,files in folders.items():
            sys.path.append(folder)
            for fname in files:
                tabName = fname[len(FilePrefix):-3]
                mytable = MyTable(folder, fname, tabName)
                Window.tableWidgets[tabName] = mytable
                #print(f'Adding tab: {fname}')
                Window.tabWidget.addTab(mytable, tabName)

        # Update tables and set up periodic check
        periodicCheck()
        if Window.pargs.interval != 0.:
            Window.timer.timeout.connect(periodicCheck)
            Window.timer.setInterval(int(Window.pargs.interval*1000.))
            Window.timer.start()

def wideRow(mytable, rowPosition, txt):
    insertRow(mytable, rowPosition)
    mytable.setSpan(rowPosition,0,1,2)
    item = QW.QTableWidgetItem(txt)
    item.setTextAlignment(QtCore.Qt.AlignCenter)
    item.setBackground(QtGui.QColor('lightGray'))
    item.setFont(BoldFont)
    mytable.setItem(rowPosition, Col['Applications'], item)

def insertRow(mytable, rowPosition):
    mytable.insertRow(rowPosition)
    #print(f'row {rowPosition}, {mytable.rowHeight(rowPosition)}')
    mytable.setRowHeight(rowPosition, 1)  
    #print(f'row {rowPosition}, {mytable.rowHeight(rowPosition)}')

def periodicCheck():
    # execute tableWideAction on current tab
    current_mytable().tableWideAction(ManCmds.index('Check'))
    # execute tableWideAction on all detached tabs
    for tabName,mytable in Window.tableWidgets.items():
        detached  = tabName in Window.tabWidget.detachedTabs
        #print(f'periodic for {tabName,detached}')
        if detached:
            mytable.tableWideAction(ManCmds.index('Check'))

