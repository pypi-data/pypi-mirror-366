#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import asyncio
import json
import os
import random
import time

import aiofiles
import aiohttp
from aiohttp import ClientTimeout, ClientSession, TCPConnector, client_exceptions
from datetime import datetime
import aiohttp
import json
import asyncio


class AsyncGoogleBatchTranslator():
    def __init__(self,
                 full_line_translation=False,
                 line_segmentation='\t',
                 line_index=0,
                 copy_line_write=True,
                 src_txt_dir=r'E:\temp\data2\data1',
                 target_txt_dir=r'E:\temp\data2\target2',
                 min_row=100,
                 max_row=100,
                 asyncio_semaphore=400,
                 timeout_total=10,
                 timeout_connect=2,
                 timeout_sock_connect=15,
                 timeout_sock_read=5,
                 retries=3,
                 url="https://translate.google.com/v1/api/google/translator",
                 src_lang='zh-CN',
                 target_lang='en',
                 proxy='http://127.0.0.1:10809',
                 ):
        """
        :param full_line_translation:  是否整行翻译， 通常为False，代表不是整行翻译
        :param line_segmentation: 当full_line_translation=False的时候，该参数生效，行内列分割符号
        :param line_index: 当full_line_translation=False的时候，该参数生效，使用哪一列进行翻译，0,1，2,3
        :param copy_line_write: 当full_line_translation=False的时候，该参数生效，写出的时候是True否False需要复制原来的整行，
        :param src_txt_dir: 原始文件目录
        :param target_txt_dir: 目标存储文件目录
        :param min_row: 随机列表大小 - 最小列表个数
        :param max_row: 随机列表大小 - 最大列表个数
        :param asyncio_semaphore: 异步并发个数
        :param timeout_total: 异步过程，全部请求最终完成时间
        :param timeout_connect:  aiohttp从本机连接池里取出一个将要进行的请求的时间
        :param timeout_sock_connect: 单个请求连接到服务器的时间
        :param timeout_sock_read: 单个请求从服务器返回的时间
        :param retries: 失败重试次数
        :param url: url地址
        :param src_lang: 源语种
        :param target_lang: 目标语种
        :param proxy: 代理
        """
        self.__full_line_translation = full_line_translation
        self.__line_segmentation = line_segmentation
        self.__line_index = line_index
        self.__copy_line_write = copy_line_write
        self.__src_txt_dir = src_txt_dir
        self.__target_txt_dir = target_txt_dir
        self.__file_names = []
        self.__pending_file_queue = []
        self.__min_row = min_row
        self.__max_row = max_row
        self.__asyncio_semaphore = asyncio_semaphore
        self.__timeout_total = timeout_total
        self.__timeout_connect = timeout_connect
        self.__timeout_sock_connect = timeout_sock_connect
        self.__timeout_sock_read = timeout_sock_read
        self.__retries = retries
        self.__url = url
        self.__src_lang = src_lang
        self.__target_lang = target_lang
        self.__proxy = proxy
        print("""
           _____                   _   _______                  _       _             
          / ____|                 | | |__   __|                | |     | |            
         | |  __  ___   ___   __ _| | ___| |_ __ __ _ _ __  ___| | __ _| |_ ___  _ __ 
         | | |_ |/ _ \ / _ \ / _` | |/ _ \ | '__/ _` | '_ \/ __| |/ _` | __/ _ \| '__|
         | |__| | (_) | (_) | (_| | |  __/ | | | (_| | | | \__ \ | (_| | || (_) | |   
          \_____|\___/ \___/ \__, |_|\___|_|_|  \__,_|_| |_|___/_|\__,_|\__\___/|_|   
                              __/ |                                                   
                             |___/    欢迎使用google translator v1.1.12.1 © 202x Raod.                                               
        """)

    print("已就绪")

    async def fetch(self, session, n, sub_list):
        retry_count = 0
        while retry_count < self.__retries:
            try:
                payload = [
                    [
                        sub_list,
                        self.__src_lang,
                        self.__target_lang
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
                        self.__url,
                        headers=headers,
                        data=json.dumps(payload).encode('utf-8'),
                        ssl=True,
                        proxy=self.__proxy
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        data24 = json.loads(text)[0]
                        return True, data24
                    else:
                        # print(f"HTTP Error: {response.status}")
                        # return False, ''
                        retry_count += 1
                        await asyncio.sleep(2 ** retry_count)  # 指数退避策略
            except client_exceptions.ServerTimeoutError as timeout_error:
                # print("request timeout error: {}, url: {}".format(timeout_error, url))
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # 指数退避策略
            except Exception:
                # print('111')
                # return False, ''
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # 指数退避策略
        print("Max retries reached, giving up.")
        return False, ''

    async def write_content_v3(self, file_path, sub_list, target_list):
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

    async def chunks(self, sem, session, i, sub_list, file_target_path):
        """
        限制并发数
        """
        async with sem:
            while True:
                success, data = await self.fetch(session, i, sub_list)
                if success:
                    return data
                else:
                    print(f"Failed to retrieve data for chunk ZZzz...")

    def random_len_sub_list(self, sfor, min_row, max_row):
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

    async def read_file_async(self, src_file_path, min_row, max_row):
        async with aiofiles.open(src_file_path, mode='r', encoding='utf-8') as sfo:
            sfor = await sfo.readlines()
            sub_lists = self.random_len_sub_list(sfor, min_row, max_row)
            return sub_lists

    async def submit_translation_single(self, sub_list, src_lang, target_lang, file_target_path,
                                        __forced_reconnection_min,
                                        __forced_reconnection_max):
        if len(sub_list) > 0:
            new_sub_list = []
            if not self.__full_line_translation:
                for sub_line in sub_list:
                    new_sub_list.append(str(sub_line).split(self.__line_segmentation)[self.__line_index])
            while True:
                try:
                    ifEnd, data = await self.submit_translation(src_lang=src_lang, src_list=new_sub_list,
                                                                target_lang=target_lang, __local_vpn_model=True,
                                                                __forced_reconnection=True, __url="",
                                                                __forced_reconnection_min=2,
                                                                __forced_reconnection_max=5)
                    if ifEnd:
                        break
                    else:
                        print("ZZzzzz...")
                        await asyncio.sleep(random.randint(__forced_reconnection_min, __forced_reconnection_max))
                except Exception as e:
                    print(f"Error during translation: {e}")
                    break
            target_list = data.get('data', [])
            if self.__copy_line_write:
                await self.write_content_v3(file_target_path, sub_list, target_list)
            else:
                await self.write_content_v3(file_target_path, new_sub_list, target_list)
            # 可选：保存或处理 target_list
            # return target_list
        # print(target_list)

    async def submit_translation(self, src_lang, src_list, target_lang, __local_vpn_model, __forced_reconnection, __url,
                                 __forced_reconnection_min, __forced_reconnection_max):
        if __local_vpn_model:
            try:
                ifFinsh, target_list = await self.google_plugin_translator_v3(src_lang, src_list, target_lang)
                return ifFinsh, {'data': target_list}
            except Exception as e:
                return False, ''
        payload = json.dumps({
            "src_lang": src_lang,
            "q": src_list,
            "target_lang": target_lang
        })
        headers = {
            'Content-Type': 'application/json'
        }
        if __forced_reconnection:
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                                url=__url,
                                headers=headers,
                                data=payload,
                                ssl=False,
                                timeout=aiohttp.ClientTimeout(total=50)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                if str(data.get('code')) == "200":
                                    return True, data
                                else:
                                    print("IP被限制，重新提交")
                                    return False, ''
                            else:
                                print("HTTP Error:", response.status)
                                return False, ''
                except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                    print(f"Connection error: {e}")
                    print("Let me sleep and retry...")
                    await asyncio.sleep(random.randint(__forced_reconnection_min, __forced_reconnection_max))
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            url=__url,
                            headers=headers,
                            data=payload,
                            ssl=False
                    ) as response:
                        data = await response.json()
                        if str(data.get('code')) == "200":
                            return True, data
                        else:
                            print("IP被限制，重新提交")
                            return False, ''
            except Exception as e:
                print(e)
                print("解析json 错误, 正在重新开始...")
                return False, ''

    async def google_plugin_translator_v3(self, src_lang, sentences, target_lang):
        url = "https://translate.google.com/v1/api/google/translator"
        payload = [
            [
                sentences,
                src_lang,
                target_lang
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
        proxy = 'http://127.0.0.1:10809'
        try:
            sem = asyncio.Semaphore(10)
            timeout = ClientTimeout(total=10, connect=2, sock_connect=15, sock_read=5)
            async with ClientSession(connector=TCPConnector(limit=400), timeout=timeout) as session:
                async with session.post(
                        url,
                        headers=headers,
                        data=json.dumps(payload).encode('utf-8'),
                        ssl=True,
                        proxy=proxy
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        data24 = json.loads(text)[0]
                        return True, data24
                    else:
                        print(f"HTTP Error: {response.status}")
                        return False, ''
        except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
            print(f"Request failed: {e}")
            return False, ''

    async def fetch0(self, session, n, sub_list):
        try:
            url = "https://translate.google.com/v1/api/google/translator"
            src_lang = 'zh-CN'
            target_lang = 'en'
            payload = [
                [
                    sub_list,
                    src_lang,
                    target_lang
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
            proxy = 'http://127.0.0.1:10809'
            async with session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload).encode('utf-8'),
                    ssl=True,
                    proxy=proxy
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    data24 = json.loads(text)[0]
                    return True, data24
                else:
                    print(f"HTTP Error: {response.status}")
                    return False, ''
        except client_exceptions.ServerTimeoutError as timeout_error:
            print("request timeout error: {}, url: {}".format(timeout_error, url))
        except Exception:
            print('111')
        return False, ''

    async def logic(self):
        if os.path.exists(self.__target_txt_dir):
            for root, dirs, files in os.walk(self.__target_txt_dir, topdown=False):
                # print("当前目录路径:", root)
                # print("当前目录下所有子目录:", dirs)
                # print("当前路径下所有非目录子文件:", files)
                for file in files:
                    self.__file_names.append(file)
        if os.path.exists(self.__src_txt_dir):
            for root, dirs, files in os.walk(self.__src_txt_dir, topdown=False):
                for file in files:
                    if not file in self.__file_names:
                        # print(root+'/'+file)
                        self.__pending_file_queue.append((root + '/' + file, file))
        for index, (src_file_path, src_file_name) in enumerate(self.__pending_file_queue):
            file_path = src_file_path
            file_target_path = self.__target_txt_dir + '/' + src_file_name
            # 记录开始时间
            start_time = time.time()
            # file_path = r"E:\temp\txt_translation_task\data_txt\9932338--20230302all.txt"  # 替换为你的实际文件路径
            # file_target_path = r"E:\temp\txt_translation_task\data_txt\9932338--20230302all.done.txt"  # 替换为你的实际文件路径
            sub_lists = await self.read_file_async(file_path, min_row=self.__min_row, max_row=self.__max_row)
            print(f'正在开始 {file_path}')
            # tasks = [self.submit_translation_single(sub_list, src_lang, target_lang, file_target_path, __full_line_translation=False, __line_segmentation='\t', __line_index=0, __forced_reconnection_min=2, __forced_reconnection_max=5, __copy_line_write=True) for sub_list in sub_lists]
            # await asyncio.gather(*tasks)
            # 将 sub_lists 和 index 同时打包进 task
            new_sub_list = []
            if not self.__full_line_translation:
                for sub_list in sub_lists:
                    temp_list = []
                    for sub_line in sub_list:
                        temp_list.append(str(sub_line).split(self.__line_segmentation)[self.__line_index])
                    new_sub_list.append(temp_list)
            else:
                new_sub_list = sub_lists
            sem = asyncio.Semaphore(self.__asyncio_semaphore)
            timeout = ClientTimeout(total=self.__timeout_total, connect=self.__timeout_connect,
                                    sock_connect=self.__timeout_sock_connect, sock_read=self.__timeout_sock_read)
            async with ClientSession(connector=TCPConnector(limit=self.__asyncio_semaphore),
                                     timeout=timeout) as session:
                # tasks = [
                #     (sub_list, asyncio.create_task(chunks(sem, session, index, sub_list, file_target_path)))
                #     for index, sub_list in enumerate(new_sub_list)
                # ]
                tasks = [
                    (original_sub_list, sub_list,
                     asyncio.create_task(self.chunks(sem, session, index, sub_list, file_target_path)))
                    for index, (sub_list, original_sub_list) in enumerate(zip(new_sub_list, sub_lists))
                ]
                for original_sub_list, sub_list, task in tasks:
                    await task  # 等待每个 task 完成
                    target_list = task.result()
                    # 获取当前时间并格式化输出
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # print(f"当前时间是：{current_time}")
                    print(
                        f"{len(self.__pending_file_queue) - index - 1}\t\t{str(index + 1)}/{str(len(self.__pending_file_queue))}\t{current_time}\t\tsub_list: {len(sub_list)}, result: {len(target_list)}")
                    # file_target_path = r"E:\temp\txt_translation_task\data_txt\9932338--20230302all.done.txt"  # 替换为你的实际文件路径
                    if self.__copy_line_write:
                        await self.write_content_v3(file_target_path, original_sub_list, target_list)
                    else:
                        await self.write_content_v3(file_target_path, sub_list, target_list)
            # 记录结束时间
            end_time = time.time()

            # 计算并打印执行时间
            execution_time = end_time - start_time
            print(f"代码片段执行耗时: {execution_time:.6f} 秒   正在开始 {file_path}")
            print(f"代码片段执行耗时: {execution_time:.6f} 秒   正在开始 {file_path}")
            print(f"代码片段执行耗时: {execution_time:.6f} 秒   正在开始 {file_path}")

    def handler(self):
        asyncio.run(self.logic())


if __name__ == "__main__":
    AsyncGoogleBatchTranslator(
        full_line_translation=False, line_segmentation='\t', line_index=0, copy_line_write=True,
                 src_txt_dir=r'E:\temp\data2\target2', target_txt_dir=r'E:\temp\data2\target3',
                 min_row=100, max_row=100,
                 asyncio_semaphore=400, timeout_total=10, timeout_connect=2, timeout_sock_connect=15, timeout_sock_read=5, retries=3,
                 url="https://translate.google.com/v1/api/google/translator",
                 src_lang='lo',
                 target_lang='zh-CN',
                 proxy='http://127.0.0.1:10809').handler()
