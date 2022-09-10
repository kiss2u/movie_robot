import logging
import os.path
import shutil


class OSUtils:
    """包装的文件系统操作工具集"""

    @staticmethod
    def link_test(source_dir, target_dir):
        """
        硬链接测试
        :param source_dir:
        :param target_dir:
        :return:
        """
        sfile = os.path.join(source_dir, 'testlink.txt')
        tfile = os.path.join(target_dir, 'testlink.txt')
        with open(sfile, "w") as f:
            f.write('text')
        os.link(sfile, tfile)
        os.remove(sfile)
        os.remove(tfile)

    @staticmethod
    def split_path(path: str):
        """
        按不同操作系统的路径分隔符拆分字符串
        :param path:
        :return:
        """
        if path is None or len(path) == 0:
            return []
        arr = []
        if path.find('\\') != -1:
            arr = path.split('\\')
        else:
            arr = path.split(os.sep)
        if arr is None or len(arr) == 0:
            return []
        return arr

    @staticmethod
    def get_path_sub_name(path: str):
        """
        获取一个路径的最后一段名称
        :param path:
        :return:
        """
        if path is None:
            return None
        arr = OSUtils.split_path(path)
        if len(arr) == 0:
            return ''
        return arr[-1]

    @staticmethod
    def my_link(src, dst, file_process_mode: str = 'link'):
        """
        对文件进行转移操作，支持硬链接、复制、移动
        :param src:
        :param dst:
        :param file_process_mode:
        :return:
        """
        if file_process_mode is None or file_process_mode == 'link':
            if os.path.exists(dst):
                os.remove(dst)
            try:
                os.link(src, dst)
            except OSError as e:
                logging.error('%s to %s 硬链接失败，请检查源目录和目标目录是否跨盘符，更多硬链接知识请自行Google！' % (src, dst))
        elif file_process_mode == 'copy':
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copyfile(src, dst)
        elif file_process_mode == 'move':
            shutil.move(src, dst)
        else:
            logging.info('%s to %s 什么也不做：%s' % (src, dst, file_process_mode))

    @staticmethod
    def create_if_not_exists(path, *paths):
        """
        拼接一个路径，如果不存在则自动创建
        :param path:
        :param paths:
        :return:
        """
        join_str = [path] + list(paths)
        join_str = list(filter(None, join_str))
        path = os.path.join(*join_str)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def find_file(path, filename):
        """
        按名称查找一个路径内文件
        :param path:
        :param filename:
        :return:
        """
        if not path or not filename:
            return
        if not os.path.exists(path):
            return
        filename = str(filename).lower()
        if os.path.isfile(path):
            if str(path).lower().endswith(filename):
                return path
            else:
                return
        for p, dir_list, file_list in os.walk(path):
            for f in file_list:
                fp = os.path.join(p, f)
                if f.lower() == filename:
                    return fp
        return
