from multiprocessing import Process, JoinableQueue
from time import sleep
from worker.file_writer import FileWriterWorker
from worker.websocket import WebsocketWorker


class SaveManager:
    def __init__(self):
        self.save_queue = JoinableQueue()

    def start_websocket_process(self, name: str, platform_settings: dict) -> None:
        """

        :param name:
        :param platform_settings:
        :return:
        """

        url: str = platform_settings.get('websocket_url')
        init_send_data: dict = platform_settings.get('websocket_init_data')
        filter_str: str = platform_settings.get('websocket_filter_str')
        platform_websocket = WebsocketWorker(
            queue=self.save_queue, platform=name, url=url, init_send_data=init_send_data, filter_str=filter_str
        )
        platform_websocket_process = Process(target=platform_websocket.start, args=())
        platform_websocket_process.daemon = True
        platform_websocket_process.start()

        print('background websocket reader for platform {} started'.format(name))

    def start_saver_processes(self, process_count: int = 1, save_cache_size: int = 100) -> None:
        """

        :param process_count:
        :param save_cache_size:
        :return:
        """

        for x in range(process_count):
            x_count = x + 1
            saver = FileWriterWorker(queue=self.save_queue, limit=save_cache_size, part=x_count)
            saver_process = Process(target=saver.start, args=())
            saver_process.daemon = True
            saver_process.start()

            print('background saver {} process started'.format(x_count))

    def run(self, config: dict, saver_process_count: int = 1, save_cache_size: int = 100) -> None:
        """

        :param config:
        :param saver_process_count:
        :param save_cache_size:
        :return:
        """

        for platform_name in config.keys():
            platform_settings = config.get(platform_name)
            if platform_settings:
                self.start_websocket_process(name=platform_name, platform_settings=platform_settings)

        self.start_saver_processes(
            process_count=saver_process_count, save_cache_size=save_cache_size
        )

        while True:
            sleep(60)
