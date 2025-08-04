from tqdm import tqdm


class TqdmProgressCallback(tqdm):
    def __init__(self, *args, TaskInstance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.TaskInstance = TaskInstance
        self.finished_count = 0

    def update(self, n: int = 1):
        super().update(n)
        self.finished_count += n
        if self.TaskInstance:
            self.TaskInstance.progress = 100.0 * (self.finished_count / self.total)
