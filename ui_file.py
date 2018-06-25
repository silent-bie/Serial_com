# -*- coding: utf-8 -*-

#
# Created by: BYM
#
import sys
import codecs
import os
import json
import time
import re
import string
import pyperclip

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
# def strlist(list):
#     ret=[]
#     for n in list:
#         ret.append(str(n))
#     return ret
#
def myhex(n):
     return "%02X "%(n)

# def strasclist(list):
#     ret=[]
#     for n in list:
#         ret.append(chr(n))
#     return ret
#
def deal_list(list,fun):
    ret=[]
    for n in list:
        ret.append(fun(n))
    return ret

def list_to_str(list):
    ret="".join(list)
    return ret

def str_to_hex(strget):
    # str_list=deal_list(string,chr)
    strget=strget.lower()
    # print(strget)
    ret=""
    for n in strget:
        num=ord(n)
        if (num>=ord('0') and num<=ord('9')) or (num>=ord('a') and num<=ord('f')):
            ret=ret+n
            # print(n)
    if len(ret)%2:
        ret=ret[0:len(ret)-1]

    try:
        ret=codecs.decode(ret,"hex_codec")
    except Exception as err:
        print("err:")
        print(err)

    return  ret

# def str_to_list(str):
#     ret=[]
#     for n in str:
#         ret.append(n)
#     return ret


class Ui_mainwindow(QtWidgets.QMainWindow):
    tx_count=0
    rx_count=0
    clean_sta=False
    tool_json_file="tool.json"
    rem_num=0
    receiving = False
    rec_none_times=0
    def __init__(self,softver,ui_conf_file,conf_file,data_rx_q,cmd_tx_q,status_rx_q,user_cmd_q):
        super().__init__()
        self.softver=softver
        self.ui_conf_file=ui_conf_file
        self.conf_file=conf_file
        self.setWindowIcon(QtGui.QIcon("cpu.ico"))
        self.initUI()
        self.create_background()
        self.timer_recdata= QtCore.QTimer(self)
        self.timer_recdata.timeout.connect(self.update_recdata)
        self.timer_recdata.start(10)
        self.timer_reccmd= QtCore.QTimer(self)
        self.timer_reccmd.timeout.connect(self.update_reccmd)
        self.timer_reccmd.start(5)
        self.auto_send_timer = QtCore.QTimer(self)
        self.auto_send_timer.timeout.connect(self.send_edit_str)

        self.data_rx_q=data_rx_q
        self.cmd_tx_q=cmd_tx_q
        self.status_rx_q=status_rx_q
        self.user_cmd_q=user_cmd_q


    def movecenter(self):

        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        print(QtWidgets.QDesktopWidget().availableGeometry().center())
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def closeEvent(self, event):
        print("closeEvent")
        event.ignore()
        reply = QtWidgets.QMessageBox.question(self,'Message','是否隐藏到任务栏?',
                                               QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Yes:
            self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.Popup)
            self.icon.show()
            self.close()

        elif reply == QtWidgets.QMessageBox.No:
            self.icon.hide()
            QtWidgets.qApp.quit()
            # event.accept()

    def keyPressEvent(self,event):
        print("test keyPressEvent:")
        print("%X"%event.key())
        if event.key() == 0x1000004:
            print("send key press")
            self.send_edit_str()

    # def keyReleaseEvent(self,event):
    #     print("test keyReleaseEvent:")
    #     print("%X"%event.key())

    # def mouseReleaseEvent(self,event):
    #     print("test mouseReleaseEvent:")
    #     print("%X"%event.key())

    def create_background(self):
        def quit_app():
            self.icon.hide()
            QtWidgets.qApp.quit()
            print("quit_app")

        def restore_app():
            self.icon.hide()
            self.setWindowFlags(QtCore.Qt.Window)
            self.show()
            print("restore_app")

        def iconClied(reason):
            if reason==self.icon.DoubleClick:
                restore_app()
        self.icon=QtWidgets.QSystemTrayIcon(self)
        self.icon.setIcon(QtGui.QIcon("cpu.ico"))
        self.icon.setVisible(True)
        self.icon.setToolTip(self.uiconf['windows_title'])
        self.minimizeAction = QtWidgets.QAction(u"最小化", self, )
        self.minimizeAction.triggered.connect(self.close)
        self.restoreAction = QtWidgets.QAction(u"还原大小", self, )
        self.restoreAction.triggered.connect(restore_app)
        self.quitAction = QtWidgets.QAction(u"退出", self,)
        self.quitAction.triggered.connect(quit_app)
        self.trayIconMenu = QtWidgets.QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()  # 分割行
        self.trayIconMenu.addAction(self.quitAction)
        self.icon.setContextMenu(self.trayIconMenu)
        self.icon.activated.connect(iconClied)
        self.icon.hide()

    def initUI(self,first=True):
#        self.create_StatusBar()
        self.uiconf=self.get_json_conf(self.ui_conf_file)
        if first:
            self.create_MeunBar()
            self.create_Toolbar()

            self.setGeometry(400, 400, 300, 200)
            # self.movecenter()
            self.move(100,100)
            self.setWindowTitle(self.uiconf['windows_title']\
            +"   ver:"+str(self.softver)\
            +"   uiver:"+str(self.uiconf['uiconf_ver']))
        self.create_Content()
        self.show()

    #获得配置文件
    def get_json_conf(self,file_name):
        file=codecs.open(file_name,"r",'utf-8')
        ui_conf=json.loads(file.read(4096))
        file.close()
        print ("ui_conf:")
        print(ui_conf)
        return ui_conf

    #写入配置文件
    def save_json_conf(self,json_obj,file_name):
        print ("json_obj:")
        # print(json_obj)
        ss = json.dumps(json_obj,indent=2)
        print(ss)
        file=codecs.open(file_name,"w",'utf-8')
        file.write(ss)
        file.close()

    #状态栏
    def create_StatusBar(self):
        self.statusBar()

    def read_conf(self):
        fileName, filetype=QFileDialog.getOpenFileName(self,'open tool file',filter="tool-*.json")
        if len (fileName)==0:
            return
        print(fileName)
        print(self.ui_conf_file)

        self.tool_json_file=fileName
        self.destroy()
        self.initUI(False)
        self.cmd_tx_q.put({'com cmd': "REFSH COM", 'com info': {'com': "COM1", }})


    def save_conf(self):
        tool_num=len(self.tool_json["tool_conf"])
        if tool_num>self.uiconf['TOOL']['num']:
            tool_num=self.uiconf['TOOL']['num']
        for n in range(0,tool_num):
            print(self.tool_send[n].text())
            self.tool_json["tool_conf"][n]['text']=self.tool_send[n].text()
        # self.tool_json
        self.save_json_conf(self.tool_json,self.tool_json_file)

    #菜单栏
    def create_MeunBar(self):

        openAction = QtWidgets.QAction(QtGui.QIcon(), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open tool file')
        openAction.triggered.connect(self.read_conf)

        saveAction = QtWidgets.QAction(QtGui.QIcon(), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('save tool file')
        saveAction.triggered.connect(self.save_conf)

        exitAction = QtWidgets.QAction(QtGui.QIcon(), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit app')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        menubar = self.menuBar()
        menu_fig=self.uiconf['meun']
        fileMenu = menubar.addMenu(menu_fig[0])
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        ConfigMenu = menubar.addMenu(menu_fig[1])

    #工具栏
    def create_Toolbar(self):
        def tool_hide_fun(bool):
            if bool:
                print("tool conf display")
                self.tool_layout.show()
            else:
                print("tool conf hide")
                self.tool_layout.hide()

        def tool_open_com(bool):
            print("ui get open com cmd")
            COM_fig = self.uiconf['COM_Config']
            port=self.port_list[self.COM_PORT.currentIndex()]
            burd=int(self.COM_BURD.currentText())
            print(port)
            print(burd)
            self.cmd_tx_q.put({'com cmd':"OPEN COM",'com info':{'com':port,'burd':burd}})
            # print(str(self.cmd_tx_q.qsize()))
            self.toolbar_list[0][0].setChecked(True)

        def tool_close_com(bool):
            print("ui get close com cmd")
            self.cmd_tx_q.put({'com cmd':"CLOSE COM",})
            self.toolbar_list[0][0].setChecked(False)

        def tool_refresh_com(bool):
            print("ui get refresh com cmd")
            self.cmd_tx_q.put({'com cmd':"REFSH COM",'com info':{'com':"COM1",}})
            self.toolbar_list[0][0].setChecked(False)

        def tool_clean(bool):
            print("ui get clean cmd")
            self.tx_count = 0
            self.rx_count = 0
            self.clean_sta=True
            self.textrec.setText("")

        toolbar_fig = self.uiconf['toolbar']
        self.toolbar_list=[]

        for tool in toolbar_fig:
            temp_tools=[]
            temp_tool=self.addToolBar(str(tool))
            for key in toolbar_fig[tool]:
                # print(key)
                tmp_action=QtWidgets.QAction(key, self)
                # tmp_action.triggered.connect(tool_hide_fun)
                temp_tool.addAction(tmp_action)
                temp_tools.append(tmp_action)
            self.toolbar_list.append(temp_tools)
            temp_tool.addSeparator()

        self.toolbar_list[1][1].triggered.connect(tool_hide_fun)
        self.toolbar_list[1][1].setCheckable(True)
        self.toolbar_list[1][1].setChecked(True)

        self.toolbar_list[0][0].triggered.connect(tool_open_com)
        self.toolbar_list[0][0].setCheckable(True)

        self.toolbar_list[0][1].triggered.connect(tool_close_com)

        self.toolbar_list[0][2].triggered.connect(tool_refresh_com)

        self.toolbar_list[1][0].triggered.connect(tool_clean)

    # UI的内容
    def create_Content(self):
        main_Widget = QtWidgets.QWidget()
        main_box = QtWidgets.QVBoxLayout()
        content_Box = QtWidgets.QHBoxLayout()

        self.com_conf_layout=self.create_leftbox()
        content_Box.addLayout(self.com_conf_layout)

        self.com_text_layout=self.create_rightbox()
        content_Box.addLayout(self.com_text_layout, stretch=1)

        self.tool_layout=self.create_toolbox()
        content_Box.addWidget(self.tool_layout)

        main_Widget.setLayout(main_box)
        main_box.addLayout(content_Box)
        main_box.addLayout(self.create_buttombox())

        self.setCentralWidget(main_Widget)

    # 左侧框架
    def create_leftbox(self):
        def send_conf_get():
            # print(btn.windowTitle())
            # print(btn.isDown())
            box_count=0
            for ckbox in self.recv_conf_wdg:
                if box_count==0:
                    if ckbox.isChecked():
                        self.recv_conf_wdg[1].setDisabled(False)
                        self.recv_conf_wdg[2].setDisabled(False)
                        self.recv_conf_wdg[3].setDisabled(False)
                        self.recv_conf_wdg[4].setDisabled(False)
                    else:
                        self.recv_conf_wdg[1].setDisabled(True)
                        self.recv_conf_wdg[2].setDisabled(True)
                        self.recv_conf_wdg[3].setDisabled(True)
                        self.recv_conf_wdg[4].setDisabled(True)
                        break
                elif box_count<=4:
                    if ckbox.isChecked():
                        self.recv_conf_wdg[0].setDisabled(True)
                        self.recv_conf_wdg[1].setDisabled(False)
                        self.recv_conf_wdg[2].setDisabled(False)
                        self.recv_conf_wdg[3].setDisabled(False)
                        self.recv_conf_wdg[4].setDisabled(False)
                    elif not(self.recv_conf_wdg[1].isChecked() or self.recv_conf_wdg[2].isChecked() or\
                                     self.recv_conf_wdg[3].isChecked() or self.recv_conf_wdg[4].isChecked()):
                        self.recv_conf_wdg[0].setDisabled(False)
                box_count+=1

        def auto_send(bool):
            print("autosend chicked ")
            print(bool)
            sendtime=self.AUTO_SEND_TIME.value()
            print(sendtime)
            if bool:
                self.auto_send_timer.start(sendtime)
            else:
                self.cmd_tx_q.queue.clear()
                print("cmd_tx_q is empty",self.cmd_tx_q.empty())
                self.auto_send_timer.stop()

        def SEND_mode_chg(void):
            print("SEND_mode_chg ")
            self.AUTO_ODOA.setDisabled(not self.SEND_ASC.isChecked())

        def com_change(value):
            if self.toolbar_list[0][0].isChecked():
                print("com_change")
                self.cmd_tx_q.put({'com cmd': "CLOSE COM", })
                COM_fig = self.uiconf['COM_Config']
                port=self.port_list[self.COM_PORT.currentIndex()]
                burd=int(self.COM_BURD.currentText())
                print(port)
                print(burd)
                self.cmd_tx_q.put({'com cmd':"OPEN COM",'com info':{'com':port,'burd':burd}})
                # print(str(self.cmd_tx_q.qsize()))
                # self.toolbar_list[0][0].setChecked(True)

        def burd_change(value):
            print("burd_change")
            burd = int(self.COM_BURD.currentText())
            print(burd)
            self.cmd_tx_q.put({'com cmd': "BURD COM",  'burd': burd})

        def debug_2():
            print("debug_2")
            fileName, filetype = QFileDialog.getOpenFileName(self, 'open python file',"","Python3 Files (*.py);;All Files (*)")
            if len(fileName)==0:
                return
            print(fileName)
            self.user_cmd_q.put({'exec file': fileName})

        def debug_3():
            print("debug_3")
            edit_str=self.textedit.toPlainText()
            try:
                if len(edit_str):
                    if not self.SEND_ASC.isChecked():
                        hexret = str_to_hex(edit_str)  # {1,2,3,4}
                        if len(hexret):
                            check_sum=0
                            for one_hex in hexret:
                                check_sum+=one_hex
                            check_sum%=0xFFFF
                            print(check_sum)
                            ret_a=bytearray(hexret)
                            ret_a.append(check_sum%0x100)
                            ret_a.append(int(check_sum/0x100))
                            print(ret_a)
                            self.cmd_tx_q.put({'com cmd': "SEND COM", 'data': ret_a})
            except Exception as err:
                print(err)
        hbox_left = QtWidgets.QVBoxLayout()

        COM_fig=self.uiconf['COM_Config']
        # hbox_left.addStretch(0)
        lay_COM_config = QtWidgets.QGridLayout()
        self.COM_PORT = QtWidgets.QComboBox()
        self.COM_PORT.addItem("test com name(COM1)")
        # self.COM_PORT.setMaximumWidth(180)
        self.COM_PORT.activated.connect(com_change)

        self.COM_BURD = QtWidgets.QComboBox()
        self.COM_BURD.addItems(deal_list(COM_fig['BURD']['list'],str))
        self.COM_BURD.setCurrentIndex(COM_fig['BURD']['default'])
        self.COM_BURD.activated.connect(burd_change)

        self.COM_DATALEN = QtWidgets.QComboBox()
        self.COM_DATALEN.addItems(deal_list(COM_fig['DATA BIT']['list'],str))
        self.COM_DATALEN.setCurrentIndex(COM_fig['DATA BIT']['default'])

        self.COM_ERC = QtWidgets.QComboBox()
        self.COM_ERC.addItems(deal_list(COM_fig['ERC BIT']['list'],str))
        self.COM_ERC.setCurrentIndex(COM_fig['ERC BIT']['default'])

        self.COM_STOPLEN = QtWidgets.QComboBox()
        self.COM_STOPLEN.addItems(deal_list(COM_fig['STOP BIT']['list'],str))
        self.COM_STOPLEN.setCurrentIndex(COM_fig['STOP BIT']['default'])

        self.COM_FLOWC = QtWidgets.QComboBox()
        self.COM_FLOWC.addItems(COM_fig['FLOW BIT']['list'])
        self.COM_FLOWC.setCurrentIndex(COM_fig['FLOW BIT']['default'])

        lay_cont=0
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['PORT']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_PORT,lay_cont,1)
        lay_cont=lay_cont+1
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['BURD']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_BURD,lay_cont,1)
        lay_cont = lay_cont + 1
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['DATA BIT']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_DATALEN,lay_cont,1)
        lay_cont = lay_cont + 1
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['ERC BIT']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_ERC,lay_cont,1)
        lay_cont = lay_cont + 1
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['STOP BIT']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_STOPLEN,lay_cont,1)
        lay_cont = lay_cont + 1
        lay_COM_config.addWidget(QtWidgets.QLabel(COM_fig['FLOW BIT']['name']),lay_cont,0)
        lay_COM_config.addWidget(self.COM_FLOWC,lay_cont,1)
        wdg_COM_config = QtWidgets.QGroupBox()
        wdg_COM_config.setLayout(lay_COM_config)
        wdg_COM_config.setTitle(COM_fig['Group'])

        RECV_fig = self.uiconf['RECV_Config']
        lay_RECV_config = QtWidgets.QGridLayout()
        self.REC_ASC = QtWidgets.QRadioButton("ASCII")
        self.REC_ASC.click()
        REC_HEX = QtWidgets.QRadioButton("Hex")
        lay_RECV_config.addWidget(self.REC_ASC,0,0)
        lay_RECV_config.addWidget(REC_HEX,0,1)
        self.recv_conf_wdg=[]
        wdg_count=1
        for wdg in RECV_fig['list']:
            tmp_wdg=QtWidgets.QCheckBox(wdg)
            tmp_wdg.setChecked(RECV_fig['default'][wdg_count-1])
            tmp_wdg.clicked.connect(send_conf_get)
            print(tmp_wdg.objectName())
            self.recv_conf_wdg.append(tmp_wdg)
            lay_RECV_config.addWidget(tmp_wdg, wdg_count, 0, 1, 2)
            wdg_count=wdg_count+1

        # self.recv_conf_wdg[0].setChecked(True)
        # self.recv_conf_wdg[5].setChecked(True)
        # AUTO_NEXT_LINE = QtWidgets.QCheckBox("Auto next line")
        # DIS_SEND_DATA = QtWidgets.QCheckBox("Show send data")
        # DIS_SEND_TIME = QtWidgets.QCheckBox("Shoe com time")
        # lay_RECV_config.addWidget(AUTO_NEXT_LINE,1,0,1,2)
        # lay_RECV_config.addWidget(DIS_SEND_DATA,2,0,1,2)
        # lay_RECV_config.addWidget(DIS_SEND_TIME,3,0,1,2)
        wdg_RECV_config = QtWidgets.QGroupBox()
        wdg_RECV_config.setLayout(lay_RECV_config)
        wdg_RECV_config.setTitle(RECV_fig['Group'])

        SEND_fig = self.uiconf['SEND_Config']
        lay_SEND_config = QtWidgets.QGridLayout()
        self.SEND_ASC = QtWidgets.QRadioButton("ASCII")
        self.SEND_ASC.click()
        self.SEND_ASC.clicked.connect(SEND_mode_chg)

        SEND_HEX = QtWidgets.QRadioButton("Hex")
        SEND_HEX.clicked.connect(SEND_mode_chg)
        self.AUTO_SEND = QtWidgets.QCheckBox(SEND_fig['list'][0])
        self.AUTO_SEND_TIME = QtWidgets.QSpinBox()
        self.AUTO_SEND_TIME.setMaximum(10000)
        self.AUTO_SEND_TIME.setMinimum(50)
        self.AUTO_SEND.clicked.connect(auto_send)
        self.AUTO_ODOA = QtWidgets.QCheckBox(SEND_fig['list'][1])

        lay_SEND_config.addWidget(self.SEND_ASC,0,0,)
        lay_SEND_config.addWidget(SEND_HEX,0,1)
        lay_SEND_config.addWidget(self.AUTO_SEND,1,0)
        lay_SEND_config.addWidget(self.AUTO_ODOA,2,0)
        lay_SEND_config.addWidget(self.AUTO_SEND_TIME,1,1)
        lay_SEND_config.addWidget(QtWidgets.QLabel("ms"),1,2)
        wdg_SEND_config = QtWidgets.QGroupBox()
        wdg_SEND_config.setLayout(lay_SEND_config)
        wdg_SEND_config.setTitle(SEND_fig['Group'])

        BUTTON_fig = self.uiconf['BUTTON']
        lay_BUTTON = QtWidgets.QVBoxLayout()
        wdg_BUTTON = QtWidgets.QGroupBox()
        wdg_BUTTON.setLayout(lay_BUTTON)
        wdg_BUTTON.setTitle(BUTTON_fig['Group'])
        #lay_BUTTON.setSpacing(1)
        self.debug_button=[]
        for btn in BUTTON_fig['list']:
            tmp_btn=QtWidgets.QPushButton(btn)
            self.debug_button.append(tmp_btn)
            lay_BUTTON.addWidget(tmp_btn)
        self.debug_button[2].clicked.connect(debug_3)
        self.debug_button[1].clicked.connect(debug_2)
        # okButton = QtWidgets.QPushButton("OK")
        # cancelButton = QtWidgets.QPushButton("Cancel")
        # lay_BUTTON.addWidget(okButton)
        # lay_BUTTON.addWidget(cancelButton)

        wdg_COM_config.setMaximumWidth(260)
        wdg_COM_config.setMinimumWidth(180)
        # wdg_RECV_config.setMaximumWidth(240)
        # wdg_RECV_config.setMinimumWidth(180)
        # wdg_SEND_config.setMaximumWidth(240)
        # wdg_SEND_config.setMinimumWidth(180)
        # wdg_BUTTON.setMaximumWidth(240)
        # wdg_BUTTON.setMinimumWidth(180)

        hbox_left.addWidget(wdg_COM_config)
        hbox_left.addWidget(wdg_RECV_config)
        hbox_left.addWidget(wdg_SEND_config)
        hbox_left.addWidget(wdg_BUTTON)

        return hbox_left

    # 右侧框架
    def create_rightbox(self):
        def read_rem(value):
            print("read rem")
            print(self.sendRemember.itemText(value))
            self.textedit.setText(self.sendRemember.itemText(value))
        hbox_Right = QtWidgets.QVBoxLayout()
        #        hbox_Right.addStretch(1)
        #        hbox_Right.setSpacing(60)
        send_box = QtWidgets.QGridLayout()

        self.textedit = QtWidgets.QTextEdit()
        self.textedit.setMinimumHeight(120)
        self.textedit.setMinimumWidth(300)
        self.textedit.setMaximumHeight(120)

        sendButton = QtWidgets.QPushButton(self.uiconf['SEND_buton'])
        sendButton.clicked.connect(self.send_edit_str)
        sendButton.setMinimumWidth(50)
        sendButton.setMaximumWidth(50)
        sendButton.setMinimumHeight(40)

        # copy_Button = QtWidgets.QPushButton(self.uiconf['copy_buton'])
        # copy_Button.clicked.connect(self.copy_str)
        # copy_Button.setMinimumWidth(50)
        # copy_Button.setMaximumWidth(50)
        #
        # paste_Button = QtWidgets.QPushButton(self.uiconf['paste_buton'])
        # paste_Button.clicked.connect(self.paste_str)
        # paste_Button.setMinimumWidth(50)
        # paste_Button.setMaximumWidth(50)

        execButton = QtWidgets.QPushButton(self.uiconf['EXEC_buton'])
        execButton.clicked.connect(self.exec_edit_str)
        execButton.setMinimumWidth(50)
        execButton.setMaximumWidth(50)
        execButton.setMinimumHeight(40)

        self.sendRemember = QtWidgets.QComboBox()
        self.sendRemember.setMaxCount(40)
        self.sendRemember.activated.connect(read_rem)

        send_box.addWidget(self.textedit,0,0,2,1)
        send_box.addWidget(sendButton,0,1)
        send_box.addWidget(execButton,1,1)

        # send_box.addWidget(copy_Button,1,1)
        # send_box.addWidget(paste_Button,2,1)
        send_box.addWidget(self.sendRemember,2,0,1,2)

        self.textrec = QtWidgets.QTextBrowser()
        doc_rec=self.textrec.document()
        doc_rec.setMaximumBlockCount(10000)
#        ui.text->document()->setMaximumBlockCount(1000);
        self.textrec.setMinimumHeight(200)
        self.textrec.setMinimumWidth(300)

        hbox_Right.addWidget(self.textrec)
        hbox_Right.addLayout(send_box)
        return hbox_Right

    #工具框架
    def create_toolbox(self):
        def send_button_get():
            for btn in self.tool_button:
                # print(btn.windowTitle())
                # print(btn.isDown())
                if btn.isDown():
                    print("get send key:" + btn.windowTitle())
                    btn_num=int(self.tool_button.index(btn))
                    # temp_str=self.tool_send[btn_num].text()
                    # print("send: "+temp_str)
                    # ret = deal_list(temp_str, ord)
                    # self.cmd_tx_q.put({'com cmd':"SEND COM",'data':ret})
                    self.send_data(self.tool_send[btn_num].text())
            # print("get send key:")

        vbox_tool = QtWidgets.QGridLayout()
        tool_fig = self.uiconf['TOOL']
        self.tool_json=self.get_json_conf(self.tool_json_file)
        #        hbox_Right.setSpacing(60)
        self.tool_send=[]
        self.tool_button=[]
        tool_c_n=0
        for tool_c in self.tool_json['tool_conf']:
            # print("create_toolbox:%d"%(n))
            temp_input=QtWidgets.QLineEdit(tool_c['text'])
            temp_input.setMinimumWidth(100)
            temp_input.setMaximumWidth(200)
            self.tool_send.append(temp_input)
            temp_label = QtWidgets.QLabel(tool_c['name'])
            temp_label.setMinimumWidth(24)
            temp_label.setMaximumWidth(70)
            send_button= QtWidgets.QPushButton(tool_fig['button'])
            send_button.setMaximumWidth(40)
            send_button.setWindowTitle(str(tool_c_n))
            send_button.pressed.connect(send_button_get)
            self.tool_button.append((send_button))
            vbox_tool.addWidget(temp_input, tool_c_n, 1)
            vbox_tool.addWidget(temp_label, tool_c_n, 0)
            vbox_tool.addWidget(send_button, tool_c_n, 2)
            tool_c_n=tool_c_n+1
            if tool_c_n==tool_fig['num']:
                break
        print(len(self.tool_send))
        # for btn in self.tool_button:
        #     print(btn.windowTitle())
        # print (self.tool_send)
        wdg_tool = QtWidgets.QGroupBox()
        wdg_tool.setLayout(vbox_tool)
        wdg_tool.setTitle(tool_fig['Group'])
        wdg_tool.setMaximumWidth(256)
        # wdg_tool_scroll = QtWidgets.QScrollArea()
        # wdg_tool_scroll.setLayout(vbox_tool)
        return wdg_tool

    # 底侧框架
    def create_buttombox(self):
        buttombox = QtWidgets.QHBoxLayout()
        self.status_progress = QtWidgets.QProgressBar()
        self.status_progress.setMinimumWidth(200)
        self.status_progress.setMaximumWidth(400)
        self.status_text=QtWidgets.QLabel("status_text")
        self.status_text.setMinimumWidth(160)
        self.status_text.setMaximumWidth(160)
        self.status_tx_count=QtWidgets.QLabel("0"+" bytes")
        self.status_tx_count.setMinimumWidth(60)
        self.status_tx_count.setMaximumWidth(60)
        self.status_rx_count=QtWidgets.QLabel("0"+" bytes")
        self.status_rx_count.setMinimumWidth(60)
        self.status_rx_count.setMaximumWidth(60)

        buttombox.addWidget(self.status_text)
        buttombox.addWidget(QtWidgets.QLabel("TX:"))
        buttombox.addWidget(self.status_tx_count)
        buttombox.addWidget(QtWidgets.QLabel("RX:"))
        buttombox.addWidget(self.status_rx_count)
        buttombox.addWidget(QtWidgets.QLabel("Progress"))
        buttombox.addWidget(self.status_progress)

        return buttombox

    def html_text_format(self,text_dict):
        # html_str="""<p style="font-family:arial;color:#FF00FF;font-size:16px;">Aparagraph.</p>"""
        html_head="""<P """
        html_end="""</P>"""
        html_style_head="""style=" """
        html_style_end=""" "> """
        html_mark=""";"""
        html_font="arial"
        if text_dict['type']=="rec":
            html_color="#FF0000"
            print(self.recv_conf_wdg[0].isChecked())
            if self.old_type=="rec" and not self.recv_conf_wdg[0].isChecked():
                OD_OA=False
        elif text_dict['type'] == "snd":
                html_color = "#00FF00"
        elif text_dict['type'] == "log":
            html_color = "#0000FF"
        elif text_dict['type'] == "err":
            html_color = "#000000"

        self.old_type = text_dict['type']
        html_size=16
        if OD_OA:
            string="<br />"+text_dict['str']
        else:
            string = text_dict['str']
        style_str="font-family:"+html_font+html_mark+"color:"+html_color+html_mark+"font-size:"+str(html_size)+"px"
        print(style_str)
        html_str=html_head+html_style_head+style_str+html_style_end+string+html_end
        print(html_str)
        return html_str

    def recv_text_format(self,text_dict):
        ret_str=""
        rec_len=0
        rec_str=""
        mark=True
        if text_dict['type']=="LOG" or text_dict['type']=="ERR":
            rec_str=text_dict['str']
        elif text_dict['type']=="CLEAR":
            print("ui get clean cmd")
            self.tx_count = 0
            self.rx_count = 0
            self.clean_sta=True
            self.textrec.setText("")
            return "",mark
        else:
            rec_len=len(text_dict['dat'])
            if self.REC_ASC.isChecked():
                rec_str=list_to_str(deal_list(text_dict['dat'],chr))
            else:
                rec_str = list_to_str(deal_list(text_dict['dat'],myhex))
            if text_dict['type']=="SND":
                self.tx_count+=rec_len
            elif text_dict['type'] == "REC":
                self.rx_count+=rec_len

        if self.recv_conf_wdg[0].isChecked():
            if (not self.recv_conf_wdg[1].isChecked()) and text_dict['type']=="LOG":
                return "",mark
            if (not self.recv_conf_wdg[2].isChecked()) and text_dict['type']=="SND":
                return "",mark
            if self.recv_conf_wdg[4].isChecked():
                ret_str=ret_str+time.strftime("%H:%M:%S ",time.localtime(text_dict['time']))
            if text_dict['type'] == "REC":
                self.rec_none_times = 0
                if self.receiving==False:
                    self.receiving=True
                    pass
                else:
                    mark = False
            if mark:
                ret_str=ret_str+text_dict['type']+": "

                if self.recv_conf_wdg[3].isChecked() and rec_len>0:
                    ret_str = ret_str +"("+str(rec_len)+") "
            ret_str=ret_str+rec_str
            return ret_str,mark

        else:
            if text_dict['type'] == "LOG" or text_dict['type'] == "ERR"or text_dict['type'] == "SND":
                return "",mark
            else:
                return rec_str,mark

    def recv_cmd_parse(self,cmd_dict):
        print(cmd_dict)
        # print(type(cmd_dict))
        if 'status' in cmd_dict:
            self.status_text.setText(cmd_dict['status'])
        if 'progress' in cmd_dict:
            self.status_progress.setValue(cmd_dict['progress'])
        if 'info list' in cmd_dict:
            self.COM_PORT.clear()
            self.COM_PORT.addItems(cmd_dict['info list'])
        if 'port list' in cmd_dict:
            self.port_list=cmd_dict['port list']
        if 'cmd ret' in cmd_dict:
            cmd_ret=cmd_dict['cmd ret']
            if 'com open' in cmd_ret:
                self.toolbar_list[0][0].setChecked(cmd_ret['com open'])

    def update_recdata(self):
        # print("data_rx_q "+str(self.data_rx_q.qsize()))
        if self.status_rx_q.qsize()==0 and self.receiving==True:
            if self.rec_none_times>=20:
                self.receiving=False
                self.rec_none_times=0
                print("receving = False")
            else:
                self.rec_none_times +=1
        while self.data_rx_q.qsize()>0:
            temp_get = self.data_rx_q.get_nowait()
            # print(temp_get)
            # self.textrec.insertHtml(self.html_text_format(temp_get))
            temp_text,mark=self.recv_text_format(temp_get)
            if len(temp_text)>0:
                if self.recv_conf_wdg[0].isChecked() and  mark==True:
                    self.textrec.append(temp_text)
                else:
                    self.textrec.insertPlainText(temp_text)
                if self.recv_conf_wdg[5].isChecked():
                    self.textrec.moveCursor(0)
            self.status_rx_count.setText(str(self.rx_count) + " bytes")
            self.status_tx_count.setText(str(self.tx_count) + " bytes")
    def update_reccmd(self):
        # print("status_rx_q "+str(self.status_rx_q.qsize()))
        while self.status_rx_q.qsize()>0:
            temp_get = self.status_rx_q.get_nowait()
            self.recv_cmd_parse(temp_get)
        if self.clean_sta:
            self.clean_sta=False
            self.status_rx_count.setText(str(self.rx_count)+" bytes")
            self.status_tx_count.setText(str(self.tx_count)+" bytes")

    def send_edit_str(self):
        self.send_data(self.textedit.toPlainText())
        if self.toolbar_list[0][0].isChecked():
            self.rem_num+=1
            self.sendRemember.insertItem(0,self.textedit.toPlainText())
            self.sendRemember.setCurrentIndex(0)
            for n in range(1,self.rem_num):
                old_item=self.sendRemember.itemText(n)
                print(old_item)
                if old_item==self.textedit.toPlainText():
                    print("same text in index%d del it now"%(n))
                    self.sendRemember.removeItem(n)
                    self.rem_num-=1
                    break
            print("rem_num=%d"%(self.rem_num))

    def copy_str(self):
        copy_buf=self.textedit.toPlainText()
        if len(copy_buf):
            pyperclip.copy(copy_buf)

    def paste_str(self):
        copy_buf=pyperclip.paste()
        if len(copy_buf):
            self.textedit.clear()
            self.textedit.insertPlainText(copy_buf)

    def exec_edit_str(self):
        print("exec edit str")
        str=self.textedit.toPlainText()
        if len(str):
            self.user_cmd_q.put({'exec string':str})

    def send_data(self,edit_str):
        print("send edit str")
        # edit_str=self.textedit.toPlainText()
        # print(edit_str)
        if len(edit_str):
            if self.SEND_ASC.isChecked():
                ret = deal_list(edit_str, ord)
                if self.AUTO_ODOA.isChecked():
                    ret.append(0x0D)
                    ret.append(0x0A)
            else:
                ret = str_to_hex(edit_str)#{1,2,3,4}
#            ret=deal_list(edit_str,ord)
            if len(ret):
                print(ret)
                self.cmd_tx_q.put({'com cmd': "SEND COM", 'data': ret})



class Ui_Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        okButton = QtWidgets.QPushButton("OK")
        cancelButton = QtWidgets.QPushButton("Cancel")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        buttombox = QtWidgets.QVBoxLayout()
        status_lab= QtWidgets.QLabel("status label")
        buttombox.addWidget(status_lab)
        vbox.addLayout(buttombox)
        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')
        self.show()


# app = QtWidgets.QApplication(sys.argv)
# #mainWidget = Ui_Widget()
# mainWindow = Ui_mainwindow(0.1,"ui_conf_cn.json","")
# mainWindow.show()
# sys.exit(app.exec_())