#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import asyncio
import sys
from datetime import datetime
import json
import os
import random
from datetime import datetime, timedelta
import time
import aiohttp
import aiofiles
import logging

if sys.platform == 'win32':
    # 设置事件循环策略为 WindowsSelectorEventLoop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 配置日志
from aiohttp import ClientTimeout, ClientSession, TCPConnector, client_exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def thread__retrieve_files(input_dir: str, output_dir: str, queue_pending: asyncio.Queue):
    __file_names = []
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for file in files:
                __file_names.append(file)
    if os.path.exists(input_dir):
        for root, dirs, files in os.walk(input_dir, topdown=False):
            for file in files:
                if not file in __file_names:
                    await queue_pending.put((root + '/' + file, file))
    await queue_pending.put((None, None))


def random_len_sub_list(sfor, min_row, max_row):
    sub_lists = []
    sum_row = 0
    while True:
        frn = random.randint(min_row, max_row)
        sub_list = sfor[sum_row:sum_row + frn]
        sum_row = sum_row + frn
        if len(sub_list) < 1:
            break
        sub_lists.append(sub_list)
    return sub_lists


async def read_file_async(src_file_path, min_row, max_row):
    async with aiofiles.open(src_file_path, mode='r', encoding='utf-8') as sfo:
        sfor = await sfo.readlines()
        sub_lists = random_len_sub_list(sfor, min_row, max_row)
        return sub_lists


async def thread_read_files(queue_pending: asyncio.Queue, queue_write: asyncio.Queue):
    # __min_row = 100
    # __max_row = 100
    # __full_line_translation = False
    # __line_segmentation = '\t'
    # __line_index = 0
    # __over_file = './over'
    while True:
        input_file_path, input_file_name = await queue_pending.get()
        if input_file_path is None:
            logger.info("thread_read_files: 收到结束信号并传递")
            __over_list = []
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            __over_list.append(now_time)
            async with aiofiles.open(__over_file, 'a', encoding='utf-8') as file_write_obj:
                await file_write_obj.writelines(__over_list)
            break
        sub_lists = await read_file_async(input_file_path, __min_row, __max_row)
        new_sub_list = []
        if not __full_line_translation:
            for sub_list in sub_lists:
                temp_list = []
                for sub_line in sub_list:
                    temp_list.append(str(sub_line).split(__line_segmentation)[__line_index])
                new_sub_list.append(temp_list)
        else:
            new_sub_list = sub_lists
        task_pres = []
        result_tasks = []
        for index, (sub_list, original_sub_list) in enumerate(zip(new_sub_list, sub_lists)):
            task_pres.append((input_file_path, input_file_name, sub_list, original_sub_list))
        while task_pres.__len__()>0:
            task_fairs = []
            # __asyncio_semaphore = 150
            # __timeout_total = 1000000
            # __timeout_connect = 2
            # __timeout_sock_connect = 15
            # __timeout_sock_read = 10
            # __copy_line_write = True
            sem = asyncio.Semaphore(__asyncio_semaphore)
            timeout = ClientTimeout(total=__timeout_total, connect=__timeout_connect, sock_connect=__timeout_sock_connect,
                                    sock_read=__timeout_sock_read)
            async with ClientSession(connector=TCPConnector(limit=__asyncio_semaphore), timeout=timeout) as session:
                tasks = [
                    (original_sub_list, sub_list, output_dir + '/' + input_file_name, input_file_name, input_file_path,
                     asyncio.create_task(chunks(sem, session, sub_list)))
                    for index, (input_file_path, input_file_name, sub_list, original_sub_list) in enumerate(task_pres)
                ]
                task_pres = []
                for original_sub_list2, sub_list2, target_file2, input_file_name2, input_file_path2, task in tasks:
                    await task
                    success, target_list3 = task.result()
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        print(f"{current_time}\t\tsub_list: {len(sub_list2)}, result: {len(target_list3)}")
                        if success:
                            if __copy_line_write:
                                #await queue_write.put((target_file2, original_sub_list2, target_list3))
                                result_tasks.append((target_file2, original_sub_list2, target_list3))
                            else:
                                #await queue_write.put((target_file2, sub_list2, target_list3))
                                result_tasks.append((target_file2, sub_list2, target_list3))
                        else:
                            task_fairs.append((input_file_path2, input_file_name2, sub_list2, original_sub_list2))
                    except Exception as e:
                        print(f'异常 {e}')
                        task_fairs.append((input_file_path2, input_file_name2, sub_list2, original_sub_list2))
            if task_fairs.__len__()>0:
                task_pres = task_fairs
        print('')
        for target_file5, sub_list5, target_list5 in result_tasks:
            await queue_write.put((target_file5, sub_list5, target_list5))


async def fetch(session, sub_list):
    # __src_lang = 'zh-CN'
    # __target_lang = 'vi'
    # __url = "https://translate.google.com/v1/api/google/translator"
    # __proxy = 'http://127.0.0.1:10809'
    try:
        payload = [
            [
                sub_list,
                __src_lang,
                __target_lang
            ], "te_lib"
        ]
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json+protobuf',
            'origin': 'https://baotintuc.vn',
            'priority': 'u=1, i',
            'referer': 'https://baotintuc.vn/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'x-client-data': 'CJa2yQEIprbJAQipncoBCM/rygEIlKHLAQiJo8sBCIWgzQEI/aXOAQjh484BCK7kzgEIyOTOAQjp5M4BCIzlzgE=',
            'x-goog-api-key': 'AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520'
        }
        async with session.post(
                __url,
                headers=headers,
                data=json.dumps(payload).encode('utf-8'),
                ssl=True,
                proxy=__proxy
        ) as response:
            if response.status == 200:
                text = await response.text()
                data24 = json.loads(text)[0]
                return True, data24
    except client_exceptions.ServerTimeoutError as timeout_error:
        print(f'发生异常 {timeout_error}')
    except Exception as e:
        print(f'发生异常 {e}')
    return False, ''


async def chunks(sem, session, sub_list):
    async with sem:
        success, data = await fetch(session, sub_list)
        return (success, data)


async def write_content_v3(file_path, sub_list, target_list):
    target_over_list = []
    if len(sub_list) == len(target_list):
        for sub_list_item, target_list_item in zip(sub_list, target_list):
            sub_list_item = str(sub_list_item).replace('\n', '').replace('\r', '')
            target_list_item = str(target_list_item).replace('\n', '').replace('\r', '')
            sglkd45d = ''
            if '<b>' in str(target_list_item):
                splists45ds = str(target_list_item).split('</b>')
                for i54s in range(len(splists45ds)):
                    try:
                        if len(splists45ds[i54s].split("<b>")) > 1:
                            sglkd45d += splists45ds[i54s].split("<b>")[1]
                    except Exception as e:
                        print(e)
            else:
                sglkd45d = str(target_list_item)
            target_list_item = sglkd45d
            target_over_list.append(f"{sub_list_item}\t{target_list_item}\n")
    else:
        print("长度不一样，不被写出结果\n" * 6)
    async with aiofiles.open(file_path, 'a', encoding='utf-8') as file_write_obj:
        await file_write_obj.writelines(target_over_list)


async def thread_write_files(queue_write: asyncio.Queue):
    while True:
        target_file4, sub_list4, target_list4 = await queue_write.get()
        await write_content_v3(target_file4, sub_list4, target_list4)
        logger.info(f"thread_write_files: 已写入数据 -> {target_file4}")
        queue_write.task_done()



async def main(input_dir, output_dir):
    """主协程：初始化队列并启动三个线程"""
    queue_pending = asyncio.Queue()
    queue_write = asyncio.Queue()

    # 创建并运行任务
    tasks = [
        asyncio.create_task(thread__retrieve_files(input_dir, output_dir, queue_pending)),
        asyncio.create_task(thread_read_files(queue_pending, queue_write)),
        asyncio.create_task(thread_write_files(queue_write))
    ]

    await asyncio.gather(*tasks)
    logger.info("所有线程已完成")


if __name__ == "__main__":
    # 必须配置
    input_dir = r"E:\temp\data2\data1-1"
    output_dir = r"E:\temp\data2\end"
    # 其它参数
    __src_lang = 'zh-CN'
    __target_lang = 'vi'
    __url =  "https://translate.google.com/v1/api/google/translator",
    __proxy = 'http://127.0.0.1:10809'
    __min_row = 100
    __max_row = 100
    __full_line_translation = False
    __line_segmentation = '\t'
    __line_index = 0
    __copy_line_write = True
    __over_file = './over'
    __asyncio_semaphore = 150
    __timeout_total = 1000000
    __timeout_connect = 2
    __timeout_sock_connect = 15
    __timeout_sock_read = 10
    # 运行事件循环
    asyncio.run(main(input_dir, output_dir))


