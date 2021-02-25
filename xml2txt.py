import logging
from logging import handlers
import os
import time
from threading import Thread
from multiprocessing import Process
import xml.etree.cElementTree as ET


# 进行日志文件处理
def set_logger(filename, logmod):
    try:
        log_size = 100000000
        log_backupcount = 1

        handler = handlers.RotatingFileHandler(filename, maxBytes=log_size, backupCount=log_backupcount)
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt='[%b %d %H:%M:%S]')
        handler.setFormatter(formatter)
        logger = logging.getLogger(logmod)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger
    except IOError:
        return logging


# 设置日志目录参数等
root_path = os.path.dirname(os.path.realpath(__file__))


# 自定义转换类
class Xml2txt(object):
    def __init__(self, xmlpath, dstpath, alogger):
        self.xmlpath = xmlpath
        self.dstpath = dstpath
        self.logger = alogger

    def convert(self, filepath, flags):
        dst_path = self.dstpath
        if flags[0] == 1:
            if flags[2] == 1:
                dst_path = os.path.join(self.dstpath, 'black')
            elif flags[3] == 1:
                dst_path = os.path.join(self.dstpath, 'white')
        elif flags[1] == 1:
            dst_path = self.dstpath

        try:
            tree = ET.ElementTree(file=filepath)
            lines = []
            
            for action in tree.iter(tag='action'):
                string = action.attrib['api_name']
                for arg in action.iter(tag='exInfo'):
                    string += "  " + arg.attrib['value']
                lines.append(string)

            ori_name = os.path.basename(filepath)
            filename = ori_name.replace("xml", "txt")
            dst_path = os.path.join(dst_path, filename)
            with open(dst_path, "w", encoding='utf-8') as dst_f:
                dst_f.write("\n".join(lines))
        except:
            self.logger.exception("error when convert %s" % filepath)

    def deal_thread(self, func):
        self.logger.info("=======start convert xml to txt=======")
        thlist = []
        max_threads = 20
        for root, dirs, files in os.walk(self.xmlpath):
            flags = [0, 0, 0, 0]
            if 'train' in root:
                flags[0] = 1
                if 'black' in root:
                    flags[2] = 1
                elif 'white' in root:
                    flags[3] = 1
            elif 'test' in root:
                flags[1] = 1
            
            for mfile in files:
                while len(thlist) >= max_threads:
                    time.sleep(5)
                    for t in thlist:
                        t.join(2.0)
                        if not t.is_alive():
                            thlist.remove(t)
                            self.logger.info("finish convert one report")
                full_path = os.path.join(root, mfile)
                t = Thread(target=func, args=(full_path, flags, ))
                thlist.append(t)
                t.start()

        for t in thlist:
            t.join()
            self.logger.info("finish convert one xml")

    # 通过多进程方式并行进行转换
    def deal_process(self, func):
        self.logger.info("=======start convert xml to txt=======")
        plist = []
        max_process = 50
        for root, dirs, files in os.walk(self.xmlpath):
            flags = [0, 0, 0, 0]
            if 'train' in root:
                flags[0] = 1
                if 'black' in root:
                    flags[2] = 1
                elif 'white' in root:
                    flags[3] = 1
            elif 'test' in root:
                flags[1] = 1
            
            for mfile in files:
                while len(plist) >= max_process:
                    for p in plist:
                        p.join(1.0) # 等待当前进程结束
                        if not p.is_alive():
                            plist.remove(p)
                            self.logger.info("finish convert one xml")
                full_path = os.path.join(root, mfile)
                p = Process(target=func, args=(full_path, flags, ))
                plist.append(p)
                p.start()

        for p in plist:
            p.join()
            self.logger.info("finish convert one report")

    def xml2txt(self, mode="process"):
        if mode == "process":
            self.deal_process(self.convert)
        else:
            self.deal_thread(self.convert)        


# 主函数入口
def main():
    report_path = "./data/xmls/datacon"
    dst_path = "./data/xmls/txts"

    for string in ['train', 'test']:
        log_path = os.path.join(root_path, "log", "xml2txt_" + string + ".log")
        alogger = set_logger(log_path, "XML2TXT_" + string)
        src = os.path.join(report_path, string)
        dst = os.path.join(dst_path, string)
        obj = Xml2txt(src, dst, alogger)
        obj.xml2txt()


if __name__ == '__main__':
    main()