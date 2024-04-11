# coding=utf-8
# 2024/3/29 11:26
from util.log_handle import log
import functools, time

'''
import inspect


class DecoratedAllMethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate: before".center(50, '-'))
            try:
                # 实例方法
                ret = self.func(obj, *args, **kwargs)
            except TypeError:
                # 类方法或者静态方法
                ret = self.func(*args, **kwargs)
            print("decorate: after".center(50, '*'))
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


class DecoratedInstanceMethod:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate instance method: before".center(50, '-'))

            ret = self.func(obj, *args, **kwargs)

            print("decorate instance method: after".center(50, '*'))
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


class DecoratedClassMethod:

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        def wrapper(*args, **kwargs):
            print("decorate class method: before")
            ret = self.func(*args, **kwargs)
            print("decorate class method: after")
            return ret
        for attr in "__module__", "__name__", "__doc__":
            setattr(wrapper, attr, getattr(self.func, attr))
        return wrapper


def decorate_class(cls):
    for name, meth in inspect.getmembers(cls):
        if inspect.ismethod(meth) or inspect.isfunction(meth):
            setattr(cls, name, DecoratedAllMethod(meth))

    return cls


@decorate_class
class Person:

    def __init__(self, name):
        self.name = name
        print("__init__")

    def call(self):
        print(self.name)

    @staticmethod
    def speak(text):
        print(f"speak: {text}")

    @classmethod
    def eat(cls):
        print("eat...")


if __name__ == '__main__':
    p = Person(name='张三')
    p.call()
    p.speak('hello world')
    Person.speak('你好')
    p.eat()
    Person.eat()
'''


class SingletonDecorator(object):
    '''单例类装饰器'''
    _instance = None

    def __init__(self, cls):
        self._cls = cls

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance


class Timer:
    '''类中函数带参数的类装饰器'''
    '''计时装饰器'''

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        @functools.wraps(self.func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                # 实例方法
                ret = self.func(obj, *args, **kwargs)
            except TypeError:
                # 类方法或者静态方法
                ret = self.func(*args, **kwargs)
            end = time.time() - start
            log.info("%s计时结束,耗时%s" % (self.func.__name__, end))
            return ret

        return wrapper


def DDT(path):
    class Inner:
        def __init__(self, func):
            self.func = func

        def __get__(self,obj,cls=None):
            @functools.wraps(self.func)
            def wrapper(*args, **kwargs):
                log.info('before func')
                with open(path, encoding='utf-8') as f:
                    temp_list = f.readlines()
                column = temp_list[0].strip().split(',')
                for i in range(1, len(temp_list)):
                    if not temp_list[i].startswith('#'):
                        temp = temp_list[i].strip().split(',')
                        for j in range(len(column)):
                            kwargs[column[j]] = temp[j]
                        try:
                            # 实例方法
                            self.func(obj, *args, **kwargs)
                        except TypeError:
                            # 类方法或者静态方法
                            self.func(*args, **kwargs)
                log.info('after func')
            return wrapper
    return Inner

