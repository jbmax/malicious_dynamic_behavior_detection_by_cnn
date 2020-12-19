# encoding=utf-8
# 用来将各个沙箱中的日志文件统一放到data文件夹中

import os
import shutil


def main():
    # 获取当前路径下的文件夹
    path = os.path.join(os.getcwd(), 'analysis_cuckoo')
    dirs = os.listdir(path)

    # 如果data目录不存在，则新建一个目录
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        os.mkdir('data')

    # 将不同的沙箱日志文件拷贝到新建文件夹中
    for item in dirs:
        old_path = os.path.join(path, item, 'reports', 'report.json')
        new_path = os.path.join(os.getcwd(), 'analysis_reports', 'report' + item + '.json')
        shutil.copyfile(old_path, new_path)
    return 0


if __name__ == '__main__':
    main()
