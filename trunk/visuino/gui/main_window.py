#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['MainWindow', 'AppVisuino']

from PyQt4 import QtGui, QtCore
import sys, os

from visuino.gx.palette import *
from visuino.gx.blocks import *
from visuino.resources import *


class MainWindow(QtGui.QMainWindow):
    '''
    Attributes:
        _app: QApplication. The application that lauched this window.
        _opengl: bool. Says if use Open GL rendering or not.
    '''

    def __init__(self, app, opengl=None):
        ''' (QApplication, QWidget, bool) -> NoneType

        The 'app' just saves the reference for the PyQt application that
        called this class. And, if the 'opengl' flag is not None, i.e.,
        if it is True or False, this value will be used to override the
        one configurated on the INI settings.
        '''
        QtGui.QMainWindow.__init__(self, None)
        self._app = app
        self._opengl = opengl

        self.setupIniSettings()

        if self._opengl is None:
            self._opengl = False
        if self._opengl:
            print('Using Open GL engine (hardware acceleration!)')
        else:
            print('Using basic graphics engine!')

        self.initUI()


    def setupIniSettings(self):
        ''' () -> NoneType

        Reads the INI file, if there is one, and configures the application
        according to it. If there is no INI yet, then create one from scratch
        with default values.
        '''
        if self._app.MAIN_CWD:
            ini_filename = self._app.MAIN_CWD + os.path.sep + \
                           self._app.INI_NAME
        else:
            ini_filename = os.getcwd() + os.path.sep + self._app.INI_NAME

        ini = self._ini_file = QtCore.QSettings(ini_filename,
                                                QtCore.QSettings.IniFormat)

        if os.path.exists(ini_filename):
            try:
                # for python 2.7
                value_opengl = ini.value('engine/opengl').toBool()
            except:
                # for python 3.3
                value_opengl = ini.value('engine/opengl').lower()[0] == 't'

            if self._opengl is None:
                self._opengl = value_opengl

            print("The following configuration file was loaded:\n%s\n\n" \
                  % ini_filename)
        else:
            self.createDefaultIni()
            print('INI created in:')
            print(ini_filename)


    def createDefaultIni(self):
        ''' (QSettings) -> NoneType

        Create the default INI settings.
        '''
        ini = self._ini_file
        ini.setValue('engine/opengl', self._opengl
                     if self._opengl is not None else False)


    def updateIniSettings(self):
        ''' () -> NoneType

        Update the INI settings file.
        '''
        ini = self._ini_file
        ini.setValue('engine/opengl', self._opengl)


    def closeEvent(self, event):
        ''' QWidget.closeEvent(QCloseEvent) -> NoneType

        Update the INI settings before closing.
        '''
        self.updateIniSettings()
        QtGui.QMainWindow.closeEvent(self, event)


    def initUI(self):
        ''' () -> NoneType

        Initializes the User Interface by creating all the child widgets
        and setting its properties.
        '''

        # --- Blocks Area ------------------------------------------------

        self.wg_blocks_view = GxViewPalette(parent=self,
                                            opengl=self._opengl)

        # --- Code Area --------------------------------------------------

        self.wg_area_code = QtGui.QWidget(self)

        # ----------------------------------------------------------------

        self.wg_main_tab = QtGui.QTabWidget()
        self.wg_main_tab.addTab(self.wg_blocks_view, 'Blocks')
        self.wg_main_tab.addTab(self.wg_area_code, 'Code')

        # --- Main menu --------------------------------------------------

        self.action_exit = QtGui.QAction('&Exit', self)
        self.connect(self.action_exit, QtCore.SIGNAL('triggered()'),
                     self.close)
        self.wg_menu_file = QtGui.QMenu('&File', self)
        self.wg_menu_file.addAction(self.action_exit)


        self.action_open_gl = QtGui.QAction('Open&GL', self)
        self.action_open_gl.setCheckable(True)
        self.action_open_gl.setChecked(self._opengl)
        self.connect(self.action_open_gl, QtCore.SIGNAL('triggered()'),
                     self.actSetOptionOpenGl)
        self.wg_menu_options = QtGui.QMenu('&Options', self)
        self.wg_menu_options.addAction(self.action_open_gl)

        menu_bar = QtGui.QMenuBar(self)
        menu_bar.addMenu(self.wg_menu_file)
        menu_bar.addMenu(self.wg_menu_options)
        self.setMenuBar(menu_bar)

        self.setWindowTitle('Visuino')
        self.setWindowIcon(QtGui.QIcon(':python_arduino.png'))
        self.setCentralWidget(self.wg_main_tab)
        self.setGeometry(200, 100, 1000, 600)


    def actSetOptionOpenGl(self):
        ''' () -> NoneType

        Trigger of the main menu Option > Open GL. If the new checked value
        is True, will prompt for a confirmation, since the use of Open GL
        rendering may cause problems on some systems.
        '''

        if self.action_open_gl.isChecked():
            ans = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                'Confirmation', "This option will attempt to use some " \
                + "hardware acceleration. Beware that it's success depends " \
                + "on the video driver.\nFor instance, in some Linux systems " \
                + "that runs on top of generic drivers may presents some "
                + "problems.\n\nDo you want to confirm it?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No).exec_()
            if ans == QtGui.QMessageBox.Yes:
                self._opengl = self.action_open_gl.isChecked()
            else:
                self.action_open_gl.toggle()
                return
        else:
            self._opengl = self.action_open_gl.isChecked()

        QtGui.QMessageBox(QtGui.QMessageBox.Warning, 'Warning',
            "You need restart the application in order for " +
            "this change to take effect!", QtGui.QMessageBox.Ok).exec_()


class AppVisuino(QtGui.QApplication):
    '''
    The hole Visuino application is launched by this class. It holds
    the main window and all the proccess starts with the execute() method,
    and ends with it.

    Attributes:
        MAIN_CWD: str. Path to the main file of the application.
        INI_NAME: str. Name of the INI configuration file.
    '''
    INI_NAME = '.visuino.ini'

    def __init__(self, argv, main_cwd=None):
        ''' (list of str, str) -> NoneType

        The 'argv' parameter is used to pass command line arguments, and
        the 'main_cwd' is stored on the self.MAIN_CWD attribute.
        '''
        QtGui.QApplication.__init__(self, argv)
        self.MAIN_CWD = main_cwd
        self.setStyle(QtGui.QStyleFactory.create("plastique"))

    def execute(self, opengl=None):
        ''' (bool) -> int

        Creates an instance of the PyQt application and show its main
        window (instance of a MainWindow object, which uses the 'opengl'
        flag).

        Returns the QApplication.exec_() result.
        '''
        splash_pix = QtGui.QPixmap(':splash_loading.png')
        splash = QtGui.QSplashScreen(splash_pix,
                                     QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        self.processEvents()

        main_win = MainWindow(app=self, opengl=opengl)
        main_win.show()
        splash.finish(main_win)
        return self.exec_()

def main():
    app = AppVisuino(sys.argv)
    app.execute()

if __name__ == '__main__':
    main()
