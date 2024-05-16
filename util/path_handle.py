# coding=utf-8
# 2024/3/28 14:23
from pathlib import Path
from util.log_handle import log


class PathHandle:

    def __init__(self):
        self.ROOT = Path(__file__).parent.parent.resolve()
        log.info('获取到项目根目录为%s' % self.ROOT)

    def create_dir(self, path):
        '''构建目录'''
        self.ROOT.joinpath(path).mkdir(parents=True, exist_ok=True)
        log.info('创建目录:{}'.format(self.ROOT.joinpath(path)))

    def rename(self, src, dst):
        '''重命名'''
        src = self.ROOT.joinpath(src)
        dst = self.ROOT.joinpath(dst)
        if not dst.exists():
            self.ROOT.joinpath(src).rename(dst)
            log.info('将【{}】重命名为【{}】'.format(src, dst))
            return
        log.warning("{}已存在".format(dst))

    def file_golb(self, path, pattern, recursive=False):
        '''列出所有满足pattern的文件'''
        dir = self.ROOT.joinpath(path)
        if not dir.is_dir():
            log.warning('{}不是目录'.format(dir))
            return
        if not recursive:
            file_list = list(dir.glob(pattern))
            log.info("{}目录下所有包含{}的文件列表为{} ！非递归".format(dir, pattern, file_list))
        else:
            file_list = list(dir.rglob(pattern))
            log.info("{}目录下所有包含{}的文件列表为{} ！递归".format(dir, pattern, file_list))
        return file_list

    def get_suffixe(self, path):
        '''获取文件后缀'''
        file = self.ROOT.joinpath(path)
        print(file)
        if file:
            suffix = self.ROOT.joinpath(path).suffix
            log.info("{}的后缀为{}".format(file, suffix))
            return suffix
        log.warning('{}不是文件'.format(file))

    def exists(self, path):
        return self.ROOT.joinpath(path).exists()


if __name__ == '__main__':
    p = PathHandle()
    # p.create_dir('data2')
    # p.rename('data2','data3')
    # p.file_golb('util','*.py')
    # p.get_suffixe('config/config.yaml')
    print(p.exists('config/config.yaml'))
