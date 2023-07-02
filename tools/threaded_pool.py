import threading

class ThreadPool:
    def __init__(self, num_threads, function_to_call, arguments):
        if num_threads > len(arguments):
            num_threads = len(arguments)
        self.num_threads = num_threads
        self.function_to_call = function_to_call
        self.arguments = arguments
        self.results = []

        print(f'Starting ThreadPool with {num_threads} threads for {len(arguments)} tasks')

    def _worker(self):
        while True:
            try:
                task = self.arguments.pop(0)
            except IndexError:
                break  # No more tasks to process

            args = task.get('args', ())
            kwargs = task.get('kwargs', {})
            result = self.function_to_call(*args, **kwargs)
            self.results.append(result)

    def run(self):
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()