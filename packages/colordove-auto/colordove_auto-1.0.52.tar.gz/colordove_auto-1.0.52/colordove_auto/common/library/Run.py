import threading
import time
from common.Common import Common
from common.request.common.TaskRequest import TaskRequest
from exceptions import TaskParamsException
from common.library.Task import Task

common = Common()
taskRequest = TaskRequest()

class Run:
    def __init__(self):
        super().__init__()

        # 运行
        self.run()

    def run(self):
        '''
        @Desc    : 循环连接 RabbitMQ
        @Author  : 钟水洲
        @Time    : 2025/05/29 14:42:03
        '''
        res = taskRequest.getTaskList()
        if res['status'] != 1:
            raise TaskParamsException(res['message'])
        task_list = res['data']

        threads = []

        for index, item in enumerate(task_list):
            print(f"任务 {index}: {item}")

            def run_task(task_item):
                task = Task()
                task.run(task_item)

            thread = threading.Thread(target=run_task, args=(item,))
            threads.append(thread)
            thread.start()

            time.sleep(1)

        # 等待所有线程完成
        for thread in threads:
            thread.join()