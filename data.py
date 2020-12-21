import os
import re
import hashlib
import numpy as np


def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


# 从文件夹读取实际转换好的文本
def get_examples_from_dir(data_dir, max_length, is_line_as_word=False):
    examples = []

    # 先判断传入路径是否为文件夹
    if not os.path.isdir(data_dir):
        return examples

    for fname in os.listdir(data_dir):
        # 从txt文件中读入转换好的文本
        full_path = os.path.join(data_dir, fname)
        f = open(full_path, "r")
        data = f.read()

        # 统计文本中的行数(调用api的数量？)
        line_num = len(data.split("\n"))
        if line_num < 5:
            continue

        # 不使用md5加密时
        if not is_line_as_word:
            examples.append(data.strip())   # 去掉字符串开始的注释，之后仍是一整个字符串
        
        # 对每行使用md5加密
        else:
            lines = data.split("\n")
            
            # replace each line as md5
            words = [hashlib.md5(line).hexdigest() for line in lines]
            examples.append(" ".join(words[:max_length]))
        f.close()

    return examples


def get_example_filenames_from_dir(data_dir, max_length, is_line_as_word=False):
    examples = []
    filenames = []
    if not os.path.isdir(data_dir):
        return examples, filenames
    for fname in os.listdir(data_dir):
        full_path = os.path.join(data_dir, fname)
        f = open(full_path, "r")
        data = f.read()
        line_num = len(data.split("\n"))
        new_lines = []
        for line in data.split("\n"):
            if not line.startswith("#"):
                new_lines.append(line)
        data = "\n".join(new_lines)
        if line_num < 5:
            continue
        filenames.append(full_path)
        if not is_line_as_word:
            examples.append(data.strip())
        else:
            lines = data.split("\n")
            # replace each line as md5
            words = [hashlib.md5(line).hexdigest() for line in lines]
            examples.append(" ".join(words[:max_length]))
        f.close()

    return examples, filenames


# 从文件中载入数据及标签的函数
def load_data_and_labels(data_dirs, max_document_length, is_line_as_word):
    # data_dirs中第一个路径为负样本，第二个为正样本
    x_text = []
    y = []
    labels = np.eye(len(data_dirs), dtype=np.int32).tolist()    # 生成对角矩阵并按行转换为列表
    for i, data_dir in enumerate(data_dirs):
        examples = get_examples_from_dir(data_dir, max_document_length, is_line_as_word)
        x_text += [clean_str(sent) for sent in examples]    # 利用正则表达式进行一些处理
        y += [labels[i]] * len(examples)    # 对列表中的元素进行扩展（相当于进行标记）
    y = np.array(y)
    return [x_text, y]


def load_data_label_and_filenames(data_dirs, max_document_length, is_line_as_word):
    x_text = []
    y = []
    fnames = []
    labels = np.eye(len(data_dirs), dtype=np.int32).tolist()
    for i, data_dir in enumerate(data_dirs):
        examples, fname = get_example_filenames_from_dir(data_dir, max_document_length, is_line_as_word)
        x_text += [clean_str(sent) for sent in examples]
        y += [labels[i]] * len(examples)
        fnames += fname
    y = np.array(y)
    return x_text, y, fnames


def data_iter(data, batch_size, ecoph_num, shuffle=True):
    data = np.array(data)
    data_size = len(data)
    batch_count = int((data_size - 1) / batch_size) + 1
    print("data_size: {}".format(data_size))
    print("batch_count: {}".format(batch_count))
    for e in range(ecoph_num):
        shuffle_data = data
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffle_data = data[shuffle_indices]

        for i in range(batch_count):
            yield shuffle_data[i * batch_size: (i + 1) * batch_size]
