import threading
import time

class ThreadPool:
    def __init__(self, num_threads, function_to_call, arguments, delay_between_tasks=0.1):
        if num_threads > len(arguments):
            num_threads = len(arguments)
        self.num_threads = num_threads
        self.function_to_call = function_to_call
        self.arguments = arguments
        self.results = []
        self.errors = []
        self.delay_between_tasks = delay_between_tasks

        print(f'Starting ThreadPool with {num_threads} threads for {len(arguments)} tasks')

    def _worker(self):
        while True:
            try:
                task = self.arguments.pop(0)
            except IndexError:
                break  # No more tasks to process
            args = task.get('args', ())
            kwargs = task.get('kwargs', {})
            try:
                result = self.function_to_call(*args, **kwargs)
            except Exception as e:
                print(f'Error: {e}')
                result = {'error': f'{e}'}
                self.errors.append({'task': task, 'error': result})
            time.sleep(self.delay_between_tasks)
            self.results.append(result)

    def run(self):
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()