# -*- coding: utf-8 -*-

#
# Created by: BYM
#
import serial
import serial.tools.list_ports
import time

def print_list(name, list, type):  # 打印报文
    print("print_list :" + name + ",len= %d" % (len(list)))
    char_temp = ""
    for dd in list:
        if type == 'HEX':
            char_temp = char_temp + "%02X" % (dd) + " "
        elif type == 'BIN':
            char_temp = char_temp + "%d" % (dd) + " "
        else:
            print("type err")
            return False
    print(char_temp)
    return True


def com_process_fnc(cmd_rx_q,revdata_parse_q,data_tx_q,status_tx_q,lock):
    parse_buf = []
    com_obj = Com_contrl_obj()

    while True:
        if cmd_rx_q.qsize() > 0:
            tmp_cmd_drit = cmd_rx_q.get_nowait()
            print(tmp_cmd_drit)
            if 'terminal' in tmp_cmd_drit:
                print("com_process_fnc exit")
                break

            if 'com cmd' in tmp_cmd_drit:
                if tmp_cmd_drit['com cmd'] == "OPEN COM":
                    print("OPEN " + tmp_cmd_drit['com info']['com'])
                    if not com_obj.connect(tmp_cmd_drit['com info']):
                        status_tx_q.put({'status':"OPEN "+tmp_cmd_drit['com info']['com']+" FAIL!",\
                                         'cmd ret':{'com open':False}})
                    else:
                        status_tx_q.put({'status':"OPEN "+tmp_cmd_drit['com info']['com']+" SUCCESS!",\
                                         'cmd ret':{'com open':True}})


                elif tmp_cmd_drit['com cmd'] == "BURD COM":
                    print("BURD COM")
                    if com_obj.connect_sta == True:
                        com_obj.burd_change(tmp_cmd_drit['burd'])
                    # status_tx_q.put({'status': "COM CLOSED!",})

                elif tmp_cmd_drit['com cmd'] == "CLOSE COM":
                    print("CLOSE COM")
                    com_obj.disconnect()
                    status_tx_q.put({'status': "COM CLOSED!", 'cmd ret': {'com open': False}})

                elif tmp_cmd_drit['com cmd'] == "SEND COM":
                    print("SEND ")
                    print_list("data",tmp_cmd_drit['data'],"HEX")
                    if com_obj.connect_sta:
                        com_obj.send(tmp_cmd_drit['data'])
                        lock.acquire()
                        data_tx_q.put({'num': 0, 'type': "SND", 'dat': tmp_cmd_drit['data'], 'time': time.time()})
                        # # dataparse_q.put(get_list)
                        lock.release()
                    else:
                        lock.acquire()
                        # sta_q.put({'com list':("test1","test2","test3")})
                        status_tx_q.put({'status': "COM CLOSED!", 'cmd ret': {'com open': False}})
                        lock.release()

                elif tmp_cmd_drit['com cmd'] == "READ COM":
                    getlen=tmp_cmd_drit['len']
                    print("READ ")

                    if len(parse_buf):
                        send_buf=[]
                        if len(parse_buf)>getlen:
                            send_buf=parse_buf[0:getlen]
                            parse_buf=parse_buf[getlen:]
                        else:
                            send_buf=parse_buf
                            parse_buf=[]
                        lock.acquire()

                        revdata_parse_q.put({ 'HEX': send_buf, 'time': time.time()})

                        lock.release()

                elif tmp_cmd_drit['com cmd'] == "CLEAN COM":
                    print("CLEAN ")
                    parse_buf=[]

                elif tmp_cmd_drit['com cmd'] == "REFSH COM":
                    print("refresh COM list")
                    if com_obj.connect_sta:
                        com_obj.disconnect()
                    del com_obj
                    com_obj = Com_contrl_obj()
                    global ports, ports_info
                    ports, ports_info = com_obj.get_com_list()
                    lock.acquire()
                    # sta_q.put({'com list':("test1","test2","test3")})
                    status_tx_q.put({'port list': ports,'info list': ports_info})
                    status_tx_q.put({'status': "COM CLOSED!", })
                    lock.release()

        if com_obj.connect_sta==True:
            # print("com open readding")
            get_temp=com_obj.read(1024)
            if get_temp=="err":
                ports, ports_info = com_obj.get_com_list()
                lock.acquire()
                # sta_q.put({'com list':("test1","test2","test3")})
                status_tx_q.put({'port list': ports, 'info list': ports_info})
                status_tx_q.put({'status': "COM CLOSED!",'cmd ret':{'com open':False} })
                lock.release()

            elif len(get_temp)>0:
                # print(get_list)
                if len(parse_buf)<204800:
                    parse_buf+=get_temp
                print_list("com rec", get_temp, "HEX")
                lock.acquire()
                data_tx_q.put({'num': 0, 'type': "REC", 'dat': get_temp, 'time': time.time()})
                lock.release()

        else:
            time.sleep(0.001)
            # print("com closed,rec process alive")

class Com_contrl_obj:
    def __init__(self):
        self.connect_sta=False
        # self.connected_port=""

    def get_com_list(self):
        self.ports = []
        self.ports_info = []
        ports_info = serial.tools.list_ports.comports()
        for port in ports_info:
            self.ports.append(port.device)
            self.ports_info.append(port.description)
            print(port.device + " : " + port.description)
        return self.ports, self.ports_info

    def get_status(self):
        return self.connect_sta#,self.connected_port

    def connect(self,port_conf):
        if not self.connect_sta:
            try:
                self.serial_obj=serial.Serial(port=port_conf['com'],baudrate=port_conf['burd'],timeout=500/port_conf['burd'])
                self.connect_sta=self.serial_obj.isOpen()
            except Exception as err:
                print("open com Fail!")
                print(err)

        return self.connect_sta

    def burd_change(self,burd):
        if self.connect_sta:
            now_setting=self.serial_obj.get_settings()
            now_setting['baudrate']=burd
            try:
                self.serial_obj.apply_settings(now_setting)
            except Exception as err:
                print("open com Fail!")
                print(err)

    def disconnect(self):
        try:

            self.serial_obj.close()
        except Exception as err:
            print(err)
            self.connect_sta=False
            return self.connect_sta
        self.connect_sta=self.serial_obj.isOpen()
        print(self.connect_sta)
        return self.connect_sta

    def send(self,datlist):
        print("send",datlist)
        if self.serial_obj.isOpen():
            self.serial_obj.write(datlist)
            return True
        else:
            return False

    def read(self,len_s):
        datlist = []
        if self.connect_sta:
            try:
                datstr = self.serial_obj.read(len_s)
                for dat in datstr:
                    datlist.append(int(dat))

            except Exception as err:
                print(err)
                self.connect_sta=False
                return "err"
            # print(datstr)
            # print(type(datstr))
        return datlist

