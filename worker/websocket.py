import asyncio
import json
from multiprocessing import JoinableQueue
import websockets


class WebsocketWorker:
    def __init__(self, queue: JoinableQueue, url: str = '', platform: str = '', init_send_data: dict = {},
                 filter_str: str = ''):
        """

        :param url:
        :param platform:
        :param init_send_data:
        :param filter_str:
        """

        self.back_queue = queue
        self.url = url
        self.platform = platform
        self.init_send_data = init_send_data
        self.filter_str = filter_str

        if filter_str:
            self.save_method = self.map_data_filtered
        else:
            self.save_method = self.map_data

    def map_data(self, data) -> None:
        """

        :param data:
        :return:
        """

        # will add platform str to data
        data_object = json.loads(data)
        if isinstance(data_object, dict):
            data_object['platform'] = self.platform
        else:
            data_object.append({'plaform': self.platform})

        self.back_queue.put(json.dumps(data_object))

    def map_data_filtered(self, data):
        """

        :param data:
        :return:
        """

        if self.filter_str in data:
            self.map_data(data=data)

    async def connect(self) -> None:
        """

        :return:
        """

        while True:
            try:
                async with websockets.connect(uri=self.url) as client:
                    await client.send(message=json.dumps(self.init_send_data))
                    while True:
                        res = await client.recv()
                        if 'error' not in res and res:
                            self.save_method(str(res))
                        else:
                            raise Exception(res)

            except Exception as ex:
                print('error on {} websocket -> {}'.format(self.platform, ex))
                pass

    def start(self) -> None:
        """

        :return:
        """

        asyncio.get_event_loop().run_until_complete(self.connect())