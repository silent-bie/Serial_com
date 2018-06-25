# -*- coding: utf-8 -*-

#
# Created by: BYM
#
import ui_file as ui
import sys
import codecs
import os
import json

import time
# import multiprocessing
# import mul_process_package
import queue
import threading
import com_hardware
import user_code

from com_hardware import Com_contrl_obj

from PyQt5 import QtCore, QtGui, QtWidgets
# from multiprocessing import Process,Queue,Pool

comobj = Com_contrl_obj()


# def main_ui_process():
#     app = QtWidgets.QApplication(sys.argv)
#     #mainWidget = Ui_Widget()
#     mainWindow = ui.Ui_mainwindow(0.1,"ui_conf_cn.json","")
#     mainWindow.show()
#     sys.exit(app.exec_())

def app(str):
    global mainWindow

    try:
        mainWindow.rec_addend_str(str)
    except Exception as err:
        print("err:")
        print(err)


# def ui_deal_process(main_q):
#     print("ui_deal_process start")
#     while True:
#         print("ui_deal_process run")
#         temp_get=main_q.get()
#         print(temp_get)
#         app(str(temp_get))
#         # mainWindow.textrec.append(str(temp_get))
#         time.sleep(0.2)

class Thread_fnc(threading.Thread):
    def __init__(self, function, args=()):
        threading.Thread.__init__(self)
        self.fuc = function
        self.args = args

    def run(self):
        self.args = self.args
        self.fuc(*self.args)

def t_est_send_fnc(data_q,sta_q,lock):
    count=0
    lock.acquire()
    sta_q.put({'status':"DEBUG Running..",'progress':0})
    lock.release()

    while True:
        print("test"+str(count))
        lock.acquire()
        # html_str="""<p style="font-family:arial;color:#FF00FF;font-size:16px;">Aparagraph.</p>"""
        data_q.put({'num':count,'type':"REC",'dat':[0x33,0x28,0x35,0x4A],'time':time.time()})
        data_q.put({'num':count,'type':"REC",'dat':[0x33,0x2C,0x34,0x46],'time':time.time()})
        data_q.put({'num':count,'type':"SND",'dat':[0x32,0x35,0x40,0x42],'time':time.time()})
        data_q.put({'num':count,'type':"LOG",'str':"log",'time':time.time()})
        data_q.put({'num':count,'type':"ERR",'str':"err",'time':time.time()})
        sta_q.put({'progress': (count/100)*100})
        # main_q.put(html_str)
        lock.release()
        time.sleep(0.2)
        count+=1
        if count==100:
            break
    lock.acquire()
    sta_q.put({'status':"DEBUG Finish !",'progress':100})
    lock.release()


def cmd_parse_fnc(cmdrx_q,sta_q,comcmd_q,lock):
    while True:
        tmp_cmd_drit=cmdrx_q.get()
        print(tmp_cmd_drit)
        if 'terminal' in tmp_cmd_drit:
            print("cmd_parse_fnc exit")
            break

        if 'com cmd' in tmp_cmd_drit:
            lock.acquire()
            comcmd_q.put(tmp_cmd_drit)
            # dataparse_q.put(get_list)
            lock.release()

def show_ui(*args):
    app = QtWidgets.QApplication(sys.argv)
    #mainWidget = Ui_Widget()
    global mainWindow
    mainWindow = ui.Ui_mainwindow(*args)
    mainWindow.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    print("Serial soft is running!")
    # ports,ports_info=comobj.get_com_list()
    data_tx_q=queue.Queue()
    cmd_rx_q=queue.Queue()
    # com_cmd_q=queue.Queue()
    status_tx_q=queue.Queue()
    revdata_parse_q=queue.Queue()
    user_cmd_q=queue.Queue()

    lock = threading.Lock()
    print(comobj)
    cmd_rx_q.put({'com cmd':"REFSH COM"})
    # cmd_parse_process = Thread_fnc(cmd_parse_fnc, args=(cmd_rx_q,status_tx_q,com_cmd_q,lock))
    com_rec_process = Thread_fnc(com_hardware.com_process_fnc, args=(cmd_rx_q,revdata_parse_q,data_tx_q,status_tx_q,lock))
    ui_process = Thread_fnc(show_ui,args=(0.1,"ui_conf_cn.json","",data_tx_q,cmd_rx_q,status_tx_q,user_cmd_q))

    user_process = Thread_fnc(user_code.usr_code_process,args=(user_cmd_q,data_tx_q,cmd_rx_q,status_tx_q,revdata_parse_q))

    ui_process.start()
    # cmd_parse_process.start()
    com_rec_process.start()
    user_process.start()

    ui_process.join()
    lock.acquire()
    cmd_rx_q.put({'terminal': True})
    # com_cmd_q.put({'terminal': True})
    user_cmd_q.put({'terminal': True})
    # dataparse_q.put(get_list)
    lock.release()

    print("UI process end")
