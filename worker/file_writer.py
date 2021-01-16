from datetime import datetime
from multiprocessing import JoinableQueue
from os.path import exists


class FileWriterWorker:
    def __init__(self, queue: JoinableQueue, limit: int = 100, part: int = 1):
        """

        :param queue:
        :param limit:
        :param part: only required for multi processing saving
        """

        self.data_queue = queue
        self.limit = limit
        self.commit_cache = []
        self.part = part

    def save_data_file(self) -> None:
        """

        :return:
        """

        if self.commit_cache:
            file_name = '{0:%Y_%m_%d}_{1}.txt'.format(datetime.now(), self.part)
            appending = ''
            if exists(file_name):
                appending = ','

            with open(file_name, 'a+') as file:
                # will create comma separated json_data sets
                file.write(','.join(self.commit_cache) + appending)

        self.commit_cache = []

    def save_data(self, data: str) -> None:
        """
        :param data:
        :return:
        """

        self.commit_cache.append(data)
        if len(self.commit_cache) >= self.limit:
            self.save_data_file()

    def start(self):
        """

        :return:
        """

        while True:
            try:
                data = self.data_queue.get()
                self.data_queue.task_done()
                self.save_data(data=data)
            except Exception as ex:
                print('error while saving data {}'.format(ex))
                pass