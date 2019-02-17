# -*- coding: utf-8 -*-
import threading

class Source:

    # 队列成员标识
    __N = None

    __isFair = False

    # 排他锁
    __X = 0
    # 意向排他锁
    __IX = 1
    # 共享锁标识
    __S = 2
    # 意向共享标识
    __IS = 3

    # 同步排他锁
    __lockX = threading.Lock()

    # 事件通知
    __events = [
        threading.Event(),
        threading.Event(),
        threading.Event(),
        threading.Event()
    ]

    # 事件通知队列
    __eventsQueue = [
        [],
        [],
        [],
        []
    ]

    # 事件变更锁
    __eventsLock = [
        threading.Lock(),
        threading.Lock(),
        threading.Lock(),
        threading.Lock()
    ]

    # 相互互斥的锁
    __mutexFlag = {}

    # 锁类
    class __ChildLock:

        # 锁标识
        __flag = 0
        # 锁定的资源
        __source = None

        def __init__(self, source, flag):
            self.__flag = flag
            self.__source = source

        # 加锁
        def lock(self):
            self.__source.lock(self.__flag)

        # 解锁
        def unlock(self):
            self.__source.unlock(self.__flag)

    def __init__(self, isFair=False):
        self.__isFair = isFair
        self.__initMutexFlag()
        self.__initEvents()

    # 不建议直接在外面使用，以免死锁
    def lock(self, flag):
        # 如果是排他锁，先进进行枷锁
        if flag == self.__X: self.__lockX.acquire()
        if self.__isFair:
            # 如果是公平锁则，先将互斥的锁给阻塞，防止其他线程进入
            self.__lockEventsWait(flag)
            self.__events[flag].wait()
            self.__lockEventsQueue(flag)
        else:
            # 如果是非公平锁，如果锁拿不到，则先等待
            self.__events[flag].wait()
            self.__lockEvents(flag)

    # 不建议直接在外面使用，以免死锁
    def unlock(self, flag):
        self.__unlockEvents(flag)
        if flag == self.__X: self.__lockX.release()

    # 获取相互互斥
    def __getMutexFlag(self, flag):
        return self.__mutexFlag[flag]

    def __initMutexFlag(self):
        self.__mutexFlag[self.__X] = [self.__X, self.__IX, self.__S, self.__IS]
        self.__mutexFlag[self.__IX] = [self.__X, self.__S]
        self.__mutexFlag[self.__S] = [self.__X, self.__IX]
        self.__mutexFlag[self.__IS] = [self.__X]

    def __initEvents(self):
        for event in self.__events:
            event.set()

    # 给事件加锁， 调用 wait 时阻塞
    def __lockEvents(self, flag):
        mutexFlags = self.__getMutexFlag(flag)
        for i in mutexFlags:
            # 为了保证原子操作，加锁
            self.__eventsLock[i].acquire()
            self.__eventsQueue[i].append(self.__N)
            self.__events[i].clear()
            self.__eventsLock[i].release()
    # 给事件加锁等待
    def __lockEventsWait(self, flag):
        mutexFlags = self.__getMutexFlag(flag)
        for i in mutexFlags:
            # 为了保证原子操作，加锁
            self.__eventsLock[i].acquire()
            self.__events[i].clear()
            self.__eventsLock[i].release()

    # 加入队列标识
    def __lockEventsQueue(self, flag):
        mutexFlags = self.__getMutexFlag(flag)
        for i in mutexFlags:
            # 为了保证原子操作，加锁
            self.__eventsLock[i].acquire()
            self.__eventsQueue[i].append(self.__N)
            self.__eventsLock[i].release()

    # 给事件解锁， 调用 wait 不阻塞
    def __unlockEvents(self, flag):
        mutexFlags = self.__getMutexFlag(flag)
        for i in mutexFlags:
            # 为了保证原子操作，加锁
            self.__eventsLock[i].acquire()
            self.__eventsQueue[i].pop(0)
            if len(self.__eventsQueue[i]) == 0:
                self.__events[i].set()
            self.__eventsLock[i].release()

    # 获取锁
    def __getLock(self, flag):
        lock = self.__ChildLock(self, flag)
        lock.lock()
        return lock

    # 获取 X 锁
    def lockX(self):
        return self.__getLock(self.__X)

    # 获取 IX 锁
    def lockIX(self):
        return self.__getLock(self.__IX)

    # 获取 S 锁
    def lockS(self):
        return self.__getLock(self.__S)

    # 获取 IS 锁
    def lockIS(self):
        return self.__getLock(self.__IS)
