import logging
import os.path
import shutil


class OSUtils:
    @staticmethod
    def trans_unit_to_mb(size: float, unit: str) -> float:
        if unit == 'GB' or unit == 'GiB':
            return round(size * 1024, 2)
        elif unit == 'MB' or unit == 'MiB':
            return round(size, 2)
        elif unit == 'KB' or unit == 'KiB':
            return round(size / 1024, 2)
        elif unit == 'TB' or unit == 'TiB':
            return round(size * 1024 * 1024, 2)
        elif unit == 'PB' or unit == 'PiB':
            return round(size * 1024 * 1024 * 1024, 2)
        else:
            return size

    @staticmethod
    def trans_size_str_to_mb(size: str):
        if not size:
            return 0.0
        s = None
        u = None
        if size.find(' ') != -1:
            arr = size.split(' ')
            s = arr[0]
            u = arr[1]
        else:
            if size.endswith('GB'):
                s = size[0:-2]
                u = 'GB'
            elif size.endswith('GiB'):
                s = size[0:-3]
                u = 'GB'
            elif size.endswith('MB'):
                s = size[0:-2]
                u = 'MB'
            elif size.endswith('MiB'):
                s = size[0:-3]
                u = 'MB'
            elif size.endswith('KB'):
                s = size[0:-2]
                u = 'KB'
            elif size.endswith('KiB'):
                s = size[0:-3]
                u = 'KB'
            elif size.endswith('TB'):
                s = size[0:-2]
                u = 'TB'
            elif size.endswith('TiB'):
                s = size[0:-3]
                u = 'TB'
            elif size.endswith('PB'):
                s = size[0:-2]
                u = 'PB'
            elif size.endswith('PiB'):
                s = size[0:-3]
                u = 'PB'
        if not s:
            return 0.0
        if s.find(',') != -1:
            s = s.replace(',', '')
        return OSUtils.trans_unit_to_mb(float(s), u)

    @staticmethod
    def link_test(source_dir, target_dir):
        sfile = os.path.join(source_dir, 'testlink.txt')
        tfile = os.path.join(target_dir, 'testlink.txt')
        with open(sfile, "w") as f:
            f.write('text')
        os.link(sfile, tfile)
        os.remove(sfile)
        os.remove(tfile)

    @staticmethod
    def split_path(path: str):
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
        if path is None:
            return None
        arr = OSUtils.split_path(path)
        if len(arr) == 0:
            return ''
        return OSUtils.split_path(path)[-1]

    @staticmethod
    def my_link(src, dst, file_process_mode: str = 'link'):
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
        join_str = [path] + list(paths)
        join_str = list(filter(None, join_str))
        path = os.path.join(*join_str)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def find_file(path, filename):
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
