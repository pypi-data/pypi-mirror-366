#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File     : setup
# @Author   : Raodi
# @Time     : 2024/7/24 14:19
"""  预料翻译任务 老挝 lo、缅甸 my、柬埔寨 km  100 印尼 id、马来 ms 300 """
import asyncio
import html
import json
import os
import queue
import sys
import time
import random
import threading

import aiohttp
import requests
from enum import Enum

from tornado import concurrent


class GoogleBatchTranslator():
    def __init__(
            self,
            src_lang='zh-CH',
            target_lang='lo',
            network_singleton=True,
            min_row=30,
            max_row=100,
            src_txt_dir=r'E:\temp\data2\data1',
            target_txt_dir=r'E:\temp\data2\target1',
            url="https://translate.google.com/v1/api/google/translator",
            reading_thread_number=30, processing_thread_number=30, writing_thread_number=32,
            forced_reconnection=False,   forced_reconnection_min=10, forced_reconnection_max=50, is_display_banner=True,
            if_read_memory_limit=False, max_reading_queue_size=10, read_memory_sleep_min=5, read_memory_sleep_max=30,
            handler_mode='normal', hm_threadpool_num_enable=True, hm_threadpool_num=10,
            full_line_translation=True, line_segmentation="\t", line_index=0, copy_line_write=True,
            local_vpn_model=False

    ):
        """
        GoogleBatchTranslator 参数说明
        :param src_lang: 源语种
        :param target_lang: 目标语种
        :param network_singleton: 是否网络模式（True为网络模式， False为写本地txt模式）
        :param min_row: 随机列表大小 - 最小列表个数
        :param max_row: 随机列表大小 - 最大列表个数
        :param src_txt_dir: 源txt文件目录
        :param target_txt_dir: 目标txt文件目录
        :param url: api地址
        :param reading_thread_number: 线程数量 - 批量读取txt的线程数量
        :param processing_thread_number: 线程数量 - 批量提交翻译的线程数量
        :param writing_thread_number: 线程数量 - 批量写入结果到txt的线程数量
        :param forced_reconnection: 单次网络提交失败是否重连
        :param forced_reconnection_min: 失败提交休眠最小时间
        :param forced_reconnection_max: 失败提交休眠最大时间
        :param is_display_banner: 是否显示版本信息
        :param if_read_memory_limit: 是否启用最大读内存限制 默认不启用
        :param max_reading_queue_size: 最大读队列大小 默认10
        :param read_memory_sleep_min:  读内存限制 - 最小休眠时间 默认5s
        :param read_memory_sleep_max:  读内存限制 - 最大休眠时间 默认30s
        :param handler_mode:  单个文件的网络请求处理方式，可选项有 normal正常模式 thread_pool线程池 async_thread异步线程，默认值为 正常模式
        :param hm_threadpool_num_enable:  单个文件的线程池处理方式 - 是否使用自定义的线程数量 选项 True False
        :param hm_threadpool_num:  单个文件的线程池处理方式 - 自定义的线程数量，默认值为 10
        :param full_line_translation:  是否整行翻译 True是  False例如已经有了两列取其中一列翻译
        :param line_segmentation: 列分割符号，标识
        :param line_index: 取哪一列翻译 0， 1,2
        :param copy_line_write:  是否复制原来到的行内容
        :param local_vpn_model:  是否使用本地vpn模式
        """
        self.pending_file_queue = queue.Queue()
        self.src_data_queue = queue.Queue()
        self.tra_data_queue = queue.Queue()
        self.if_read_memory_limit = if_read_memory_limit
        self.max_reading_queue_size = max_reading_queue_size-1
        self.read_memory_sleep_min = read_memory_sleep_min
        self.read_memory_sleep_max = read_memory_sleep_max
        self.src_lang = src_lang
        self.target_lang = target_lang
        self.min_row = min_row
        self.max_row = max_row
        self.src_txt_dir = src_txt_dir
        self.target_txt_dir = target_txt_dir
        self.__network_singleton = network_singleton
        self.__url = url
        self.__file_names = []
        self.__lock = threading.Lock()
        self.__reading_thread_number = reading_thread_number
        self.__processing_thread_number = processing_thread_number
        self.__writing_thread_number = writing_thread_number
        self.__forced_reconnection = forced_reconnection
        self.__forced_reconnection_min = forced_reconnection_min
        self.__forced_reconnection_max = forced_reconnection_max
        self.__handler_mode = handler_mode
        self.__hm_threadpool_num_enable = hm_threadpool_num_enable
        self.__hm_threadpool_num = hm_threadpool_num
        self.__full_line_translation = full_line_translation
        self.__line_segmentation = line_segmentation
        self.__line_index = line_index
        self.__copy_line_write = copy_line_write
        self.__local_vpn_model = local_vpn_model
        if not self.__network_singleton:
            self.read_target_file_names()
            self.extract_pending_files()
        if is_display_banner:
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

    def read_target_file_names(self):
        if os.path.exists(self.target_txt_dir):
            for root, dirs, files in os.walk(self.target_txt_dir, topdown=False):
                # print("当前目录路径:", root)
                # print("当前目录下所有子目录:", dirs)
                # print("当前路径下所有非目录子文件:", files)
                for file in files:
                    self.__file_names.append(file)

    def extract_pending_files(self):
        if os.path.exists(self.src_txt_dir):
            for root, dirs, files in os.walk(self.src_txt_dir, topdown=False):
                for file in files:
                    if not file in self.__file_names:
                        # print(root+'/'+file)
                        self.pending_file_queue.put((root + '/' + file, file))

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

    def random_data_fragmentation(self):
        while True:
            (src_file_path, src_file_name) = self.pending_file_queue.get()
            with open(src_file_path, mode='r', encoding='utf-8') as sfo:
                sfor = sfo.readlines()
                sub_lists = self.random_len_sub_list(sfor, self.min_row, self.max_row)
                data = (self.target_txt_dir + '/' + src_file_name, sub_lists, self.src_lang, self.target_lang)
                self.src_data_queue.put(data)
                print(threading.current_thread().name, "self.src_data_queue.size=", self.src_data_queue.qsize())

    def get_size(self, obj, seen=None):
        """Recursively finds size of objects"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Mark as seen
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_size(v, seen) for v in obj.values()])
            size += sum([self.get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += self.get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_size(i, seen) for i in obj])
        return size

    def random_data_fragmentation2(self):
        while True:
            (src_file_path, src_file_name) = self.pending_file_queue.get()

            # ### 智能限制文件读取到内存的大小
            if self.if_read_memory_limit:
                while True:
                    if self.src_data_queue.qsize() > self.max_reading_queue_size:
                        time.sleep(random.randint(self.read_memory_sleep_min, self.read_memory_sleep_max))
                    else:
                        break

            # ## todo 2024-07-26 读txt文件内容，内存最大缓存限制
            # self.max_read_memory_limit = 3
            # # Check the size of the src_data_queue before processing the file
            # queue_size = self.get_size(self.src_data_queue.queue)
            # max_memory_limit = self.max_read_memory_limit * 1024 * 1024 * 1024  # 单位为 GB
            # while queue_size > max_memory_limit:
            #     print(f"{threading.current_thread().name} - Queue size exceeds 3GB, sleeping...")
            #     time.sleep(random.randint(5, 30))
            #     queue_size = self.get_size(self.src_data_queue.queue)

            with open(src_file_path, mode='r', encoding='utf-8') as sfo:
                sfor = sfo.readlines()
                sub_lists = self.random_len_sub_list(sfor, self.min_row, self.max_row)
                data = (self.target_txt_dir + '/' + src_file_name, sub_lists, self.src_lang, self.target_lang)
                self.src_data_queue.put(data)
                print(threading.current_thread().name, "self.src_data_queue.size=", self.src_data_queue.qsize())

    def submit_translation(self, src_lang, src_list, target_lang):
        # url = "https://translate.google.com/v1/api/google/translator"
        # url = "https://translate.google.com/v1/api/google/translator"
        if self.__local_vpn_model:
            try:
                ifFinsh, target_list = self.google_plugin_translator_v3(src_lang, src_list, target_lang)
                if ifFinsh:
                    return True, {'data': target_list}
                else:
                    return False, ''
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
        # 是否强制重连
        if self.__forced_reconnection:
            while True:
                try:
                    response = requests.post(url=self.__url, headers=headers, data=payload, timeout=(30, 50),
                                             verify=False)
                    break
                except:
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    print("ZZzzzz...")
                    #time.sleep(random.randint(10, 50))
                    time.sleep(random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))
                    print("Was a nice sleep, now let me continue...")
                    continue
        else:
            try:
                response = requests.post(url=self.__url, headers=headers, data=payload)
            except Exception as e:
                return False, ''

        try:
            data = json.loads(response.text)
            if str(data['code']).__eq__("200"):
                return True, data
                # time.sleep(random.randint(5, 15))
            else:
                print("IP被限制，重新提交")
                return False, ''
        except Exception as e:
            print(e)
            print("解析json 错误, 正在重新开始...")
            return False, ''

    def submit_translation2(self, src_lang, src_list, target_lang, is_purified=False, is_decoded=False):
        # url = "https://translate.google.com/v1/api/google/translator"
        # url = "https://translate.google.com/v1/api/google/translator"
        payload = json.dumps({
            "src_lang": src_lang,
            "q": src_list,
            "target_lang": target_lang
        })
        headers = {
            'Content-Type': 'application/json'
        }
        # 是否强制重连
        if self.__forced_reconnection:
            while True:
                try:
                    response = requests.post(url=self.__url, headers=headers, data=payload, timeout=(30, 50),
                                             verify=False)
                    break
                except:
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    print("ZZzzzz...")
                    #time.sleep(random.randint(10, 50))
                    time.sleep(random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))
                    print("Was a nice sleep, now let me continue...")
                    continue
        else:
            try:
                response = requests.post(url=self.__url, headers=headers, data=payload)
            except Exception as e:
                return False, ''
        try:
            data = json.loads(response.text)
            if str(data['code']).__eq__("200"):
                # todo 2024-07-24 新增清洗
                if is_purified:
                    data_list = data['data']
                    new_data_list = []
                    for target_list_item in data_list:
                        target_list_item = str(target_list_item)
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
                        new_data_list.append(target_list_item)
                    data['data'] = new_data_list
                if is_decoded:
                    data_list = data['data']
                    new_data_list = []
                    for target_list_item in data_list:
                        target_list_item = str(target_list_item)
                        target_list_item = html.unescape(target_list_item)
                        new_data_list.append(target_list_item)
                    data['data'] = new_data_list
                return True, data
                # time.sleep(random.randint(5, 15))
            else:
                print("IP被限制，重新提交")
                return False, ''
        except Exception as e:
            print(e)
            print("解析json 错误, 正在重新开始...")
            return False, ''

    def submit_translation_single(self, sub_list, src_lang, target_lang, file_path):
        if len(sub_list) > 0:
            new_sub_list = []
            if not self.__full_line_translation:
                for sub_line in sub_list:
                    new_sub_list.append(str(sub_line).split(self.__line_segmentation)[self.__line_index])
            while True:
                ifEnd, data = self.submit_translation(
                    src_lang=src_lang,
                    src_list=new_sub_list,
                    target_lang=target_lang
                )
                if ifEnd:
                    break
                else:
                    print("ZZzzzz...")
                    time.sleep(random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))
            target_list = data['data']
            # print(threading.current_thread().name, "self.pending_file_queue.size=", self.pending_file_queue.qsize(), "self.src_data_queue.size=", self.src_data_queue.qsize(),
            #       "self.tra_data_queue.size=", self.tra_data_queue.qsize(), "target_lists.size=",
            #       len(target_list))
            print("remaining_files: ", self.pending_file_queue.qsize(), " cache_queue_size: ",
                  self.src_data_queue.qsize(),
                  " waiting_write_queue_size: ", self.tra_data_queue.qsize(), threading.current_thread().name,
                  " translating_lists_size: ",
                  len(target_list))
            if self.__copy_line_write:
                self.tra_data_queue.put((file_path, sub_list, src_lang, target_lang, target_list))
            else:
                self.tra_data_queue.put((file_path, new_sub_list, src_lang, target_lang, target_list))
            # time.sleep(random.randint(2, 5))

    class TranslationClient:
        def __init__(self, url, forced_reconnection=False, forced_reconnection_min=10, forced_reconnection_max=50, max_concurrent_tasks=1):
            self.__url = url
            self.__forced_reconnection = forced_reconnection
            self.__forced_reconnection_min = forced_reconnection_min
            self.__forced_reconnection_max = forced_reconnection_max
            self.__max_concurrent_tasks = max_concurrent_tasks

        async def submit_translation(self, src_lang, src_list, target_lang):
            payload = json.dumps({
                "src_lang": src_lang,
                "q": src_list,
                "target_lang": target_lang
            })
            headers = {
                'Content-Type': 'application/json'
            }

            # 是否强制重连
            if self.__forced_reconnection:
                while True:
                    try:
                        timeout=aiohttp.ClientTimeout(total=600)
                        conn = aiohttp.TCPConnector(ssl=False)  # 防止ssl报错
                        policy = asyncio.WindowsSelectorEventLoopPolicy()
                        asyncio.set_event_loop_policy(policy)
                        semaphore = asyncio.Semaphore(self.__max_concurrent_tasks)
                        async with semaphore:
                            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                                async with session.post(url=self.__url, headers=headers, data=payload,
                                                        timeout=aiohttp.ClientTimeout(total=600), ssl=False) as response:
                                    if response.status == 200:
                                        data = await response.json()
                                        return data
                                    else:
                                        print("IP被限制，重新提交")
                                        await asyncio.sleep(
                                            random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))
                    except Exception as e:
                        print(f"Connection refused by the server: {e}")
                        print("Let me sleep for 5 seconds")
                        print("ZZzzzz...")
                        await asyncio.sleep(
                            random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))
                        print("Was a nice sleep, now let me continue...")
                        continue
            else:
                timeout = aiohttp.ClientTimeout(total=600)
                conn = aiohttp.TCPConnector(ssl=False)  # 防止ssl报错
                policy = asyncio.WindowsSelectorEventLoopPolicy()
                asyncio.set_event_loop_policy(policy)
                semaphore = asyncio.Semaphore(self.__max_concurrent_tasks)
                async with semaphore:
                    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                        async with session.post(url=self.__url, headers=headers, data=payload,
                                                timeout=aiohttp.ClientTimeout(total=600), ssl=False) as response:
                            if response.status == 200:
                                data = await response.json()
                                return data
                            else:
                                print("IP被限制，重新提交")
                                return await self.submit_translation(src_lang, src_list, target_lang)

            # 解析 JSON 响应
            try:
                data = await response.json()
                if str(data['code']) == "200":
                    return data
                else:
                    print("IP被限制，重新提交")
                    return await self.submit_translation(src_lang, src_list, target_lang)
            except Exception as e:
                print(e)
                print("解析json 错误, 正在重新开始...")
                return await self.submit_translation(src_lang, src_list, target_lang)

    async def post_json(self, sub_list, src_lang, target_lang, file_path):
        if len(sub_list) > 0:
            client = self.TranslationClient(
                url=self.__url,
                forced_reconnection=self.__forced_reconnection,
                forced_reconnection_min=self.__forced_reconnection_min,
                forced_reconnection_max=self.__forced_reconnection_max,
                max_concurrent_tasks=2
            )
            data = await client.submit_translation(
                src_lang=src_lang,
                src_list=sub_list,
                target_lang=target_lang
            )
            target_list = data['data']
            # print(threading.current_thread().name, "self.pending_file_queue.size=", self.pending_file_queue.qsize(), "self.src_data_queue.size=", self.src_data_queue.qsize(),
            #       "self.tra_data_queue.size=", self.tra_data_queue.qsize(), "target_lists.size=",
            #       len(target_list))
            print("remaining_files: ", self.pending_file_queue.qsize(), " cache_queue_size: ",
                  self.src_data_queue.qsize(),
                  " waiting_write_queue_size: ", self.tra_data_queue.qsize(), threading.current_thread().name,
                  " translating_lists_size: ",
                  len(target_list))
            self.tra_data_queue.put((file_path, sub_list, src_lang, target_lang, target_list))
            # time.sleep(random.randint(2, 5))

    async def send_requests(self, sub_lists, src_lang, target_lang, file_path):
        tasks = [self.post_json(sub_list, src_lang, target_lang, file_path) for sub_list in sub_lists]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def prepare_translation(self):
        while True:
            (file_path, sub_lists, src_lang, target_lang) = self.src_data_queue.get()
            # handler_mode = 'normal', hm_threadpool_num_enable = True, hm_threadpool_num = 10
            # normal thread_pool async_thread
            if self.__handler_mode.__eq__('thread_pool'):
                if self.__hm_threadpool_num_enable:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.__hm_threadpool_num) as executor:
                        futures = []
                        for sub_list in sub_lists:
                            future = executor.submit(self.submit_translation_single, sub_list, src_lang, target_lang, file_path)
                            futures.append(future)
                        for future in concurrent.futures.as_completed(futures):  # 等待所有任务完成
                            try:
                                future.result()  # 获取任务结果，如果有异常会在这里抛出
                            except Exception as e:
                                print(f"An error occurred111111: {e}")
                else:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = []
                        for sub_list in sub_lists:
                            future = executor.submit(self.submit_translation_single, sub_list, src_lang, target_lang, file_path)
                            futures.append(future)
                        for future in concurrent.futures.as_completed(futures):  # 等待所有任务完成
                            try:
                                future.result()  # 获取任务结果，如果有异常会在这里抛出
                            except Exception as e:
                                print(f"An error occurred111111: {e}")
            elif self.__handler_mode.__eq__('async_thread'):
                # loop = asyncio.new_event_loop()
                # try:
                #     results = loop.run_until_complete(self.send_requests(sub_lists, src_lang, target_lang, file_path))
                #     for i, result in enumerate(results):
                #         if isinstance(result, Exception):
                #             print(f"Request to failed: {result}")
                #         else:
                #             print(f"Response from : {result}")
                # finally:
                #     loop.close()
                print("""
   _____                                                _                 _ 
  / ____|                                              | |               | |
 | (___   ___ _ ____   _____ _ __    _____   _____ _ __| | ___   __ _  __| |
  \___ \ / _ \ '__\ \ / / _ \ '__|  / _ \ \ / / _ \ '__| |/ _ \ / _` |/ _` |
  ____) |  __/ |   \ V /  __/ |    | (_) \ V /  __/ |  | | (_) | (_| | (_| |
 |_____/ \___|_|    \_/ \___|_|     \___/ \_/ \___|_|  |_|\___/ \__,_|\__,_|                                      
                    系统已为您切换正常模式""")

                # normal 及其其他方式
                for sub_list in sub_lists:
                    self.submit_translation_single(sub_list, src_lang, target_lang, file_path)
            else:
                # normal 及其其他方式
                for sub_list in sub_lists:
                    self.submit_translation_single(sub_list, src_lang, target_lang, file_path)
            print("")

    def write_content(self):
        while True:
            (file_path, sub_list, src_lang, target_lang, target_list) = self.tra_data_queue.get()
            if len(sub_list) == len(target_list):
                for sub_list_item, target_list_item in zip(sub_list, target_list):
                    sub_list_item = str(sub_list_item).replace('\n', '').replace('\r', '')
                    target_list_item = str(target_list_item).replace('\n', '').replace('\r', '')
                    self.__lock.acquire()  # 获取锁
                    try:
                        with open(file_path, 'a', encoding="utf-8") as file_write_obj:
                            file_write_obj.writelines(sub_list_item + '\t' + target_list_item)
                            file_write_obj.write('\n')
                    finally:
                        self.__lock.release()  # 释放锁
            else:
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果\n")

    def write_content_v2(self):
        while True:
            (file_path, sub_list, src_lang, target_lang, target_list) = self.tra_data_queue.get()
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
                    self.__lock.acquire()  # 获取锁
                    try:
                        with open(file_path, 'a', encoding="utf-8") as file_write_obj:
                            file_write_obj.writelines(sub_list_item + '\t' + target_list_item)
                            file_write_obj.write('\n')
                    finally:
                        self.__lock.release()  # 释放锁
            else:
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果\n")

    def write_content_v3(self):
        while True:
            (file_path, sub_list, src_lang, target_lang, target_list) = self.tra_data_queue.get()
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
                    target_over_list.append(sub_list_item + '\t' + target_list_item + '\n')
            else:
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果")
                print("长度不一样，不被写出结果\n")
            self.__lock.acquire()  # 获取锁
            try:
                with open(file_path, 'a', encoding="utf-8") as file_write_obj:
                    file_write_obj.writelines(target_over_list)
            finally:
                self.__lock.release()  # 释放锁

    def google_plugin_translator_v3(self, src_lang, sentences, target_lang):
        try:
            request = requests.session()
            url = "https://translate-pa.googleapis.com/v1/translateHtml"
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
            response = request.post(url, headers=headers, data=json.dumps(payload).encode('utf-8'),
                                    proxies={'https': 'http://127.0.0.1:10809'})
            data24 = json.loads(response.text)[0]
            return True, data24
        except Exception as e:
            return False, ''

    def handler(self, src_lang=None, src_list=None, target_lang=None, is_purified=False, is_decoded=False):
        """
            函数入库
        :param src_lang: 源语种
        :param src_list: 被翻译的句子列表
        :param target_lang: 目标语种
        :param is_purified: 是否提纯(仅当网络模式生效)
        :param is_decoded: 是否将html字符转成标准字符(仅当网络模式生效)
        :return:
        """
        if src_lang is None:
            src_lang = self.src_lang
        if src_list is None:
            src_list = ['Chính sách trang web']
        if target_lang is None:
            target_lang = self.target_lang
        if not self.__network_singleton:
            for idx in range(self.__reading_thread_number):
                t = threading.Thread(target=self.random_data_fragmentation2, name=f">> random_data_fragmentation2 {idx}")
                t.start()
            print("")
            for idx in range(self.__processing_thread_number):
                t = threading.Thread(target=self.prepare_translation, name=f" prepare_translation {idx}")
                t.start()
            print("")
            for idx in range(self.__writing_thread_number):
                t = threading.Thread(target=self.write_content_v3, name=f">> write_content_v3 {idx}")
                t.start()
            print("")
        else:
            while True:
                isZEnd, restl = self.submit_translation2(src_lang, src_list, target_lang, is_purified, is_decoded)
                if isZEnd:
                    break
                else:
                    print("ZZzzzz...")
                    time.sleep(random.randint(self.__forced_reconnection_min, self.__forced_reconnection_max))

    def __del__(self):
        print('已退出')

    class Langs(Enum):
        af = 'af'  # 公用荷兰语
        afZA = 'af-ZA'  # 公用荷兰语-南非
        sq = 'sq'  # 阿尔巴尼亚
        sqAL = 'sq-AL'  # 阿尔巴尼亚-阿尔巴尼亚
        ar = 'ar'  # 阿拉伯语
        arDZ = 'ar-DZ'  # 阿拉伯语-阿尔及利亚
        arBH = 'ar-BH'  # 阿拉伯语-巴林
        arEG = 'ar-EG'  # 阿拉伯语-埃及
        arIQ = 'ar-IQ'  # 阿拉伯语-伊拉克
        arJO = 'ar-JO'  # 阿拉伯语-约旦
        arKW = 'ar-KW'  # 阿拉伯语-科威特
        arLB = 'ar-LB'  # 阿拉伯语-黎巴嫩
        arLY = 'ar-LY'  # 阿拉伯语-利比亚
        arMA = 'ar-MA'  # 阿拉伯语-摩洛哥
        arOM = 'ar-OM'  # 阿拉伯语-阿曼
        arQA = 'ar-QA'  # 阿拉伯语-卡塔尔
        arSA = 'ar-SA'  # 阿拉伯语-沙特阿拉伯
        arSY = 'ar-SY'  # 阿拉伯语-叙利亚共和国
        arTN = 'ar-TN'  # 阿拉伯语-北非的共和国
        arAE = 'ar-AE'  # 阿拉伯语-阿拉伯联合酋长国
        arYE = 'ar-YE'  # 阿拉伯语-也门
        hy = 'hy'  # 亚美尼亚
        hyAM = 'hy-AM'  # 亚美尼亚的-亚美尼亚
        az = 'az'  # Azeri
        azAZCyrl = 'az-AZ-Cyrl'  # Azeri-(西里尔字母的)-阿塞拜疆
        azAZLatn = 'az-AZ-Latn'  # Azeri(拉丁文)-阿塞拜疆
        eu = 'eu'  # 巴斯克
        euES = 'eu-ES'  # 巴斯克-巴斯克
        be = 'be'  # Belarusian
        beBY = 'be-BY'  # Belarusian-白俄罗斯
        bg = 'bg'  # 保加利亚
        bgBG = 'bg-BG'  # 保加利亚-保加利亚
        ca = 'ca'  # 嘉泰罗尼亚
        caES = 'ca-ES'  # 嘉泰罗尼亚-嘉泰罗尼亚
        zhHK = 'zh-HK'  # 华-香港的SAR
        zhMO = 'zh-MO'  # 华-澳门的SAR
        zhCN = 'zh-CN'  # 华-中国
        zhCHS = 'zh-CHS'  # 华(单一化)
        zhSG = 'zh-SG'  # 华-新加坡
        zhTW = 'zh-TW'  # 华-台湾
        zhCHT = 'zh-CHT'  # 华(传统的)
        hr = 'hr'  # 克罗埃西亚
        hrHR = 'hr-HR'  # 克罗埃西亚-克罗埃西亚
        cs = 'cs'  # 捷克
        csCZ = 'cs-CZ'  # 捷克-捷克
        da = 'da'  # 丹麦文
        daDK = 'da-DK'  # 丹麦文-丹麦
        div = 'div'  # Dhivehi
        divMV = 'div-MV'  # Dhivehi-马尔代夫
        nl = 'nl'  # 荷兰
        nlBE = 'nl-BE'  # 荷兰-比利时
        nlNL = 'nl-NL'  # 荷兰-荷兰
        en = 'en'  # 英国
        enAU = 'en-AU'  # 英国-澳洲
        enBZ = 'en-BZ'  # 英国-伯利兹
        enCA = 'en-CA'  # 英国-加拿大
        enCB = 'en-CB'  # 英国-加勒比海
        enIE = 'en-IE'  # 英国-爱尔兰
        enJM = 'en-JM'  # 英国-牙买加
        enNZ = 'en-NZ'  # 英国-新西兰
        enPH = 'en-PH'  # 英国-菲律宾共和国
        enZA = 'en-ZA'  # 英国-南非
        enTT = 'en-TT'  # 英国-千里达托贝哥共和国
        enGB = 'en-GB'  # 英国-英国
        enUS = 'en-US'  # 英国-美国
        enZW = 'en-ZW'  # 英国-津巴布韦
        et = 'et'  # 爱沙尼亚
        etEE = 'et-EE'  # 爱沙尼亚的-爱沙尼亚
        fo = 'fo'  # Faroese
        foFO = 'fo-FO'  # Faroese-法罗群岛
        fa = 'fa'  # 波斯语
        faIR = 'fa-IR'  # 波斯语-伊朗王国
        fi = 'fi'  # 芬兰语
        fiFI = 'fi-FI'  # 芬兰语-芬兰
        fr = 'fr'  # 法国
        frBE = 'fr-BE'  # 法国-比利时
        frCA = 'fr-CA'  # 法国-加拿大
        frFR = 'fr-FR'  # 法国-法国
        frLU = 'fr-LU'  # 法国-卢森堡
        frMC = 'fr-MC'  # 法国-摩纳哥
        frCH = 'fr-CH'  # 法国-瑞士
        gl = 'gl'  # 加利西亚
        glES = 'gl-ES'  # 加利西亚-加利西亚
        ka = 'ka'  # 格鲁吉亚州
        kaGE = 'ka-GE'  # 格鲁吉亚州-格鲁吉亚州
        de = 'de'  # 德国
        deAT = 'de-AT'  # 德国-奥地利
        deDE = 'de-DE'  # 德国-德国
        deLI = 'de-LI'  # 德国-列支敦士登
        deLU = 'de-LU'  # 德国-卢森堡
        deCH = 'de-CH'  # 德国-瑞士
        el = 'el'  # 希腊
        elGR = 'el-GR'  # 希腊-希腊
        gu = 'gu'  # Gujarati
        guIN = 'gu-IN'  # Gujarati-印度
        he = 'he'  # 希伯来
        heIL = 'he-IL'  # 希伯来-以色列
        hi = 'hi'  # 北印度语
        hiIN = 'hi-IN'  # 北印度的-印度
        hu = 'hu'  # 匈牙利
        huHU = 'hu-HU'  # 匈牙利的-匈牙利
        isIS = 'is-IS'  # 冰岛的-冰岛
        id = 'id'  # 印尼
        idID = 'id-ID'  # 印尼-印尼
        it = 'it'  # 意大利
        itIT = 'it-IT'  # 意大利-意大利
        itCH = 'it-CH'  # 意大利-瑞士
        ja = 'ja'  # 日本
        jaJP = 'ja-JP'  # 日本-日本
        kn = 'kn'  # 卡纳达语
        knIN = 'kn-IN'  # 卡纳达语-印度
        kk = 'kk'  # Kazakh
        kkKZ = 'kk-KZ'  # Kazakh-哈萨克
        kok = 'kok'  # Konkani
        kokIN = 'kok-IN'  # Konkani-印度
        ko = 'ko'  # 韩国
        koKR = 'ko-KR'  # 韩国-韩国
        ky = 'ky'  # Kyrgyz
        kyKZ = 'ky-KZ'  # Kyrgyz-哈萨克
        lo = 'lo'  # 柬埔寨
        lv = 'lv'  # 拉脱维亚
        lvLV = 'lv-LV'  # 拉脱维亚的-拉脱维亚
        lt = 'lt'  # 立陶宛
        ltLT = 'lt-LT'  # 立陶宛-立陶宛
        mk = 'mk'  # 马其顿
        mkMK = 'mk-MK'  # 马其顿-FYROM
        ms = 'ms'  # 马来
        msBN = 'ms-BN'  # 马来-汶莱
        msMY = 'ms-MY'  # 马来-马来西亚
        mr = 'mr'  # 马拉地语
        mrIN = 'mr-IN'  # 马拉地语-印度
        mn = 'mn'  # 蒙古
        mnMN = 'mn-MN'  # 蒙古-蒙古
        no = 'no'  # 挪威
        nbNO = 'nb-NO'  # 挪威(Bokmål)-挪威
        nnNO = 'nn-NO'  # 挪威(Nynorsk)-挪威
        pl = 'pl'  # 波兰
        plPL = 'pl-PL'  # 波兰-波兰
        pt = 'pt'  # 葡萄牙
        ptBR = 'pt-BR'  # 葡萄牙-巴西
        ptPT = 'pt-PT'  # 葡萄牙-葡萄牙
        pa = 'pa'  # Punjab语
        paIN = 'pa-IN'  # Punjab语-印度
        ro = 'ro'  # 罗马尼亚语
        roRO = 'ro-RO'  # 罗马尼亚语-罗马尼亚
        ru = 'ru'  # 俄国
        ruRU = 'ru-RU'  # 俄国-俄国
        sa = 'sa'  # 梵文
        saIN = 'sa-IN'  # 梵文-印度
        srSPCyrl = 'sr-SP-Cyrl'  # 塞尔维亚-(西里尔字母的)塞尔维亚共和国
        srSPLatn = 'sr-SP-Latn'  # 塞尔维亚(拉丁文)-塞尔维亚共和国
        sk = 'sk'  # 斯洛伐克
        skSK = 'sk-SK'  # 斯洛伐克-斯洛伐克
        sl = 'sl'  # 斯洛文尼亚
        slSI = 'sl-SI'  # 斯洛文尼亚-斯洛文尼亚
        es = 'es'  # 西班牙
        esAR = 'es-AR'  # 西班牙-阿根廷
        esBO = 'es-BO'  # 西班牙-玻利维亚
        esCL = 'es-CL'  # 西班牙-智利
        esCO = 'es-CO'  # 西班牙-哥伦比亚
        esCR = 'es-CR'  # 西班牙-哥斯达黎加
        esDO = 'es-DO'  # 西班牙-多米尼加共和国
        esEC = 'es-EC'  # 西班牙-厄瓜多尔
        esSV = 'es-SV'  # 西班牙-萨尔瓦多
        esGT = 'es-GT'  # 西班牙-危地马拉
        esHN = 'es-HN'  # 西班牙-洪都拉斯
        esMX = 'es-MX'  # 西班牙-墨西哥
        esNI = 'es-NI'  # 西班牙-尼加拉瓜
        esPA = 'es-PA'  # 西班牙-巴拿马
        esPY = 'es-PY'  # 西班牙-巴拉圭
        esPE = 'es-PE'  # 西班牙-秘鲁
        esPR = 'es-PR'  # 西班牙-波多黎各
        esES = 'es-ES'  # 西班牙-西班牙
        esUY = 'es-UY'  # 西班牙-乌拉圭
        esVE = 'es-VE'  # 西班牙-委内瑞拉
        sw = 'sw'  # Swahili
        swKE = 'sw-KE'  # Swahili-肯尼亚
        sv = 'sv'  # 瑞典
        svFI = 'sv-FI'  # 瑞典-芬兰
        svSE = 'sv-SE'  # 瑞典-瑞典
        syr = 'syr'  # Syriac
        syrSY = 'syr-SY'  # Syriac-叙利亚共和国
        ta = 'ta'  # 坦米尔
        taIN = 'ta-IN'  # 坦米尔-印度
        tt = 'tt'  # Tatar
        ttRU = 'tt-RU'  # Tatar-俄国
        te = 'te'  # Telugu
        teIN = 'te-IN'  # Telugu-印度
        th = 'th'  # 泰国
        thTH = 'th-TH'  # 泰国-泰国
        tr = 'tr'  # 土耳其语
        trTR = 'tr-TR'  # 土耳其语-土耳其
        uk = 'uk'  # 乌克兰
        ukUA = 'uk-UA'  # 乌克兰-乌克兰
        ur = 'ur'  # Urdu
        urPK = 'ur-PK'  # Urdu-巴基斯坦
        uz = 'uz'  # Uzbek
        uzUZCyrl = 'uz-UZ-Cyrl'  # Uzbek-(西里尔字母的)乌兹别克斯坦
        uzUZLatn = 'uz-UZ-Latn'  # Uzbek(拉丁文)-乌兹别克斯坦
        vi = 'vi'  # 越南
        viVN = 'vi-VN'  # 越南-越南

    class RToolBox():
        class TxtFilesMerger():
            def __init__(self):
                print("已就绪")

            def __del__(self):
                print('操作完成')

            def merge_txt_files(self, input_folder, output_file_path):
                # 确保输出文件的父目录存在
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    for filename in os.listdir(input_folder):
                        if filename.endswith('.txt'):
                            input_file_path = os.path.join(input_folder, filename)
                            print("文件合并中，input_file_path =", input_file_path)
                            with open(input_file_path, 'r', encoding='utf-8') as infile:
                                # 为了清晰区分每个文件的内容，可以在每个文件内容之间添加分隔符
                                outfile.writelines(infile.readlines())
                print("文件合并完成！")

        class BatchFileOperationTool():
            def __init__(self):
                print("已就绪")

            def __ensure_directory_exists__(self, directory_path):
                """
                确保指定的目录存在，如果不存在则创建该目录。
                :param directory_path: str, 要检查或创建的目录路径。
                """
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)
                    print(f"目录 '{directory_path}' 已创建。")
                else:
                    print(f"目录 '{directory_path}' 已存在。")

            def move_files2_new_directory(self, source_dir, fomt, target_dir):
                """
                递归地查找源目录中的所有txt文件，并将它们移动到目标目录。
                :param source_dir: str, 原始目录路径。
                :param target_dir: str, 目标目录路径。
                """
                # 确保目标目录存在
                self.__ensure_directory_exists__(target_dir)
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(fomt):
                            # 构建源文件和目标文件的完整路径
                            src_file_path = os.path.join(root, file)
                            dst_file_path = os.path.join(target_dir, file)

                            # 移动文件并处理可能出现的错误
                            try:
                                os.replace(src_file_path, dst_file_path)

                                print(f"文件 '{src_file_path}' 已移动到 '{dst_file_path}'")
                            except Exception as e:
                                print(f"移动文件 '{src_file_path}' 时出错: {str(e)}")

            def __del__(self):
                print('操作完成')

        class LargeTxtFileCutter():
            def __init__(self):
                print("已就绪")

            def __del__(self):
                print('操作完成')

            def __split_txt_file__(self, input_file, output_folder, lines_per_file=200000):
                """
                将大txt文件按照每20万行切割为多个小文件，并保存到指定文件夹中。

                :param input_file: str, 输入的txt文件路径。
                :param output_folder: str, 输出文件夹路径。
                :param lines_per_file: int, 每个新文件包含的行数，默认为200000。
                """
                # 确保输出文件夹存在
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                # 打开大文件读取内容
                with open(input_file, 'r', encoding='utf-8') as infile:
                    # 初始化计数器和起始行号
                    count = 0
                    start_line = 1

                    # 用于构建新文件名的变量
                    file_base_name = os.path.splitext(os.path.basename(input_file))[0]

                    for line in infile:
                        # 写入当前文件
                        if count % lines_per_file == 0:
                            # 如果是新的批次开始，关闭上一个文件（如果存在）
                            if start_line != 1:
                                outfile.close()

                            # 构建新文件名
                            end_line = start_line + lines_per_file - 1
                            new_file_name = f"{file_base_name}_{start_line}_{end_line}.txt"
                            new_file_path = os.path.join(output_folder, new_file_name)

                            # 打开新文件
                            outfile = open(new_file_path, 'w', encoding='utf-8')
                            start_line += lines_per_file

                        # 写入当前行到文件
                        outfile.write(line)
                        count += 1

                    # 处理最后一部分不足20万行的情况
                    if count % lines_per_file != 0:
                        end_line = start_line + lines_per_file - 1
                        if count < end_line:
                            end_line = count
                        outfile.close()

                    print(f"{os.path.basename(input_file)} 切割完成")

            def __get_src_file_paths__(self, target_txt_dir):
                __file_names = []
                if os.path.exists(target_txt_dir):
                    for root, dirs, files in os.walk(target_txt_dir, topdown=False):
                        # print("当前目录路径:", root)
                        # print("当前目录下所有子目录:", dirs)
                        # print("当前路径下所有非目录子文件:", files)
                        for file in files:
                            __file_names.append(target_txt_dir + "\\" + file)
                return __file_names

            def handler(self, input_folder, output_folder, lines_per_file: int = 200000):
                # 示例调用
                # split_txt_file(r'E:\temp\txt_translation_task\data_txt\7717881--20230302all.txt', r'E:\temp\txt_translation_task\data_txt\7717881--20230302all')
                file_paths = self.__get_src_file_paths__(input_folder)
                for file_path in file_paths:
                    self.__split_txt_file__(file_path, output_folder, lines_per_file)
                print("执行完毕")


if __name__ == "__main__":
    ## 使用方法1： 目录下txt文件批量行处理
    logic = GoogleBatchTranslator(src_lang='zh-CH', target_lang='vi', network_singleton=False, min_row=130, max_row=180,
                                  src_txt_dir=r'H:\translation_tasks\data',
                                  target_txt_dir=r'H:\translation_tasks\target',
                                  url="https://translate.google.com/v1/api/google/translator",
                                  reading_thread_number=1, processing_thread_number=30, writing_thread_number=30,
                                  forced_reconnection=True, forced_reconnection_min=2, forced_reconnection_max=5,
                                  full_line_translation=False, line_segmentation="\t", line_index=1, copy_line_write=True,
                                  if_read_memory_limit=True, max_reading_queue_size=2, read_memory_sleep_min=5,
                                  read_memory_sleep_max=30,
                                  handler_mode='thread_pool', hm_threadpool_num_enable=False, hm_threadpool_num=10,  # normal thread_pool async_thread
                                  local_vpn_model=True
                                )
    logic.handler()

    # # # ## 使用方法2： 仅进行网络请求 -- 完整写法
    # logic = GoogleBatchTranslator(src_lang='zh-CH', target_lang='id', network_singleton=True, url="https://translate.google.com/v1/api/google/translator")
    # result = logic.handler(src_list=['脚本'])
    # print(result)
    # result = logic.handler(
    #     src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
    #     is_purified=True,
    #     is_decoded=True)
    # print(result)
    # result = logic.handler(
    #     src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
    #     is_purified=True)
    # print(result)
    # result = logic.handler(src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"])
    # print(result)
    # result = logic.handler(src_lang='auto', src_list=['ဟယ်လို'], target_lang='zh-TW')
    # print(result)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'])
    # print(result)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_decoded=True)
    # print(result)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_purified=True, is_decoded=True)
    # print(result)
    #
    # # ## 使用方法3： 仅进行网络请求 -- 简写
    # logic = GoogleBatchTranslator(is_display_banner=False)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据'])
    # print(result)
    # result = logic.handler(src_lang='zh-CH', src_list=['二分法递归处理丢失的数据'], target_lang='zh-TW')
    # print(result)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据'])
    # print(result)
    #
    # ## 使用方法4： 仅进行网络请求 -- 枚举语言+简写
    # logic = GoogleBatchTranslator()
    # result = logic.handler(src_list=['二分法递归处理丢失的数据'])
    # print(result)
    # result = logic.handler(src_lang=logic.Langs.zhCN.value, src_list=['二分法递归处理丢失的数据'], target_lang=logic.Langs.en.value)
    # print(result)
    # result = logic.handler(src_lang=logic.Langs.zhCN.value, src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"], target_lang=logic.Langs.vi.value)
    # print(result)
    # result = logic.handler(src_list=['二分法递归处理丢失的数据'])
    # print(result)


    # ###### 工具测试
    # rToolBox = GoogleBatchTranslator().RToolBox()
    # ## 1. 批量 txt 文件合并到一个 txt
    # rToolBox.TxtFilesMerger().merge_txt_files(
    #     input_folder=r'E:\temp\txt_translation_task\data_txt\data3',
    #     output_file_path=r'E:\temp\txt_translation_task\data_txt\target_en2zh_total1.txt'
    # )
    # ## 2.批量txt文件移动到一个新的文件
    # rToolBox.BatchFileOperationTool().move_files2_new_directory(
    #     source_dir=r'E:\temp\txt_translation_task\data_txt\data2',
    #     fomt='.txt',
    #     target_dir=r'E:\temp\txt_translation_task\data_txt\data'
    # )
    # ## 3.切割大 txt 文件成小txt文件
    # rToolBox.LargeTxtFileCutter().handler(
    #     input_folder=r'E:\temp\txt_translation_task\data_txt\data',
    #     output_folder=r'E:\temp\txt_translation_task\data_txt\data3',
    #     lines_per_file=1000
    # )



































