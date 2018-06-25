# -*- coding: utf-8 -*-

#
# Created by: BYM
#
import ui_file as ui
import sys
import codecs
import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv)
#mainWidget = Ui_Widget()
mainWindow = ui.Ui_mainwindow(0.1,"ui_conf_cn.json","")
mainWindow.show()
sys.exit(app.exec_())