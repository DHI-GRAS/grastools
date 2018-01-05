import concurrent.futures
import threading


class MaxSizeThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Simple subclass of ProcessPoolExecutor that has a maximum queue size"""
    def __init__(self, queue_size, *args, **kwargs):
        super(MaxSizeThreadPoolExecutor, self).__init__(*args, **kwargs)
        self._semaphore = threading.Semaphore(queue_size)

    def release(self, future):
        self._semaphore.release()

    def submit(self, *args, **kwargs):
        self._semaphore.acquire()
        future = super(MaxSizeThreadPoolExecutor, self).submit(*args, **kwargs)
        future.add_done_callback(self.release)
        return future

    def map(self, func, *iterables):
        def result_iterator():
            pending = set()
            try:
                for args in zip(*iterables):
                    future = self.submit(func, *args)
                    pending.add(future)

                    done, pending = concurrent.futures.wait(pending, timeout=0)
                    for future in done:
                        yield future.result()
            finally:
                for future in pending:
                    future.cancel()

        return result_iterator()
