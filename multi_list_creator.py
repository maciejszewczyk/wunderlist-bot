import threading
import time
import Queue
import random


class MultiThread(object):
    def __init__(self, function, argsVector, maxThreads=10, queue_results=False):
        self._function = function
        self._lock = threading.Lock( )
        self._nextArgs = iter(argsVector).next
        self._threadPool = [ threading.Thread(target=self._doSome)
                             for i in range(maxThreads) ]
        if queue_results:
            self._queue = Queue.Queue( )
        else:
            self._queue = None

    def _doSome(self):
        while True:
            self._lock.acquire( )
            try:
                try:
                    args = self._nextArgs( )
                except StopIteration:
                    break
            finally:
                self._lock.release( )
            result = self._function(args)
            if self._queue is not None:
                self._queue.put((args, result))

    def get(self, *a, **kw):
        if self._queue is not None:
            return self._queue.get(*a, **kw)
        else:
            raise ValueError, 'Not queueing results'

    def start(self):
        for thread in self._threadPool:
            time.sleep(0)  # necessary to give other threads a chance to run
            thread.start()

    def join(self, timeout=None):
        for thread in self._threadPool:
            thread.join(timeout)

if __name__ == "__main__":
    import wunderlist
    wa = wunderlist.WunderlistAPI('94c0f1728a3cb4a066d21f1a63da3d4101fa7d11deb78ef800e4b16776e6', '171f61134bea341afeff')

    def listcreate(n):
        print 'N:', n
        print wa.createlist('Maciek'+str(n))

    def createtask(n):
        print 'N:', n
        print wa.createtask(247639416, 'Task'+str(n))

    mt = MultiThread(createtask, range(1, 11))
    mt.start( )
    mt.join( )
    print "Beautiful done."

