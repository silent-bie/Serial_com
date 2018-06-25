# -*- coding: utf-8 -*-

#
# Created by: BYM
#
import codecs
import time


def myhex(n):
    return "%02X " % (n)


def deal_list(list, fun):
    ret = []
    for n in list:
        ret.append(fun(n))
    return ret


def list_to_str(list):
    ret = "".join(list)
    return ret


def str_to_hex(strget):
    strget = strget.lower()
    ret = ""
    for n in strget:
        num = ord(n)
        if (num >= ord('0') and num <= ord('9')) or (num >= ord('a') and num <= ord('f')):
            ret = ret + n
            # print(n)
    if len(ret) % 2:
        ret = ret[0:len(ret) - 1]

    try:
        ret = codecs.decode(ret, "hex_codec")
    except Exception as err:
        print("err:")
        print(err)

    return ret




def usr_code_process(user_cmd_q,data_tx_q,com_cmd_q,status_tx_q,revdata_parse_q):
    def status(strg):
        status_tx_q.put({'status': strg, })

    def progress(n):
        status_tx_q.put({'progress': n, })

    def send_string(strg):
        if len(strg):
            ret = deal_list(strg, ord)
            com_cmd_q.put({'com cmd': "SEND COM", 'data': ret})

    def send_hex(hex):
        if len(hex):
            com_cmd_q.put({'com cmd': "SEND COM", 'data': hex})

    def log(strg):
        if len(strg):
            data_tx_q.put({'type': "LOG", 'str': strg, 'time': time.time()})

    def log_err(strg):
        if len(strg):
            data_tx_q.put({'type': "ERR", 'str': strg, 'time': time.time()})

    def read(buf_len=10240,timeout=200):
        com_cmd_q.put({'com cmd': "READ COM","len":buf_len})
        for n in range(0,timeout):
            com_get=[]
            try:
                com_get = revdata_parse_q.get_nowait()
            except Exception as err:
                pass
            if len(com_get)>0:
                print("com read:>")
                print(com_get)
                return com_get['HEX']
            time.sleep(0.001)

        print("read nothing")
    def clean():
        com_cmd_q.put({'com cmd': "CLEAN COM"})

    def clear():
        data_tx_q.put({'type': "CLEAR", 'str': "", 'time': time.time()})
		
    def delay(ms):
        time.sleep(ms)

    while True:
        cmd=user_cmd_q.get()
        print("usr_code_process")
        print(cmd)
        if 'terminal' in cmd:
            print("usr_code_process exit")
            break
        elif 'exec file' in cmd:
            status_tx_q.put({'status': "exec file ...", })
            try:
                with codecs.open(cmd['exec file'], 'r',"utf-8") as file:
                    f_str = file.read()
                    exec(f_str)
            except Exception as err:
                print(err)
                log_err("exec file %s occur err:\r\n"%(cmd['exec file'])+str(err))
            status_tx_q.put({'status': "exec file finish!", })

        elif 'exec string' in cmd:
            status_tx_q.put({'status': "exec edit string ...", })
            try:
                exec(cmd['exec string'])
            except Exception as err:
                print(err)
                log_err("exec string occur err:\r\n"+str(err))
            status_tx_q.put({'status': "exec edit string finish!", })
