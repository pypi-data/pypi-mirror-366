#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import asyncio
import csv
import re
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

import pandas as pd
# 设置Pandas显示选项 - 确保完整打印不省略
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度
pd.set_option('display.max_colwidth', None)  # 显示完整列内容
if sys.platform == 'win32':
    # 设置事件循环策略为 WindowsSelectorEventLoop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 配置日志
from aiohttp import ClientTimeout, ClientSession, TCPConnector, client_exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncGoogleBatchBackTranslatorFaster():
    def __init__(self,
        input_dir=r"E:\temp\data2\data1-1",
        output_dir = r"E:\temp\data2\end",
        over_file='./over',
                 enable_translator=True,
        translate_tasks = [
            {
                "src_lang": 'zh-CN',
                "target_lang": 'vi',
                "url": "https://translate-pa.googleapis.com/v1/translateHtml",
                "proxy": 'http://127.0.0.1:10809',
                "min_row": 80,
                "max_row": 150,
                "full_line_translation": False,
                "line_segmentation": '\t',
                "line_index": 0,
                "copy_line_write": True,
                "over_file": './over',
                "asyncio_semaphore": 150,
                "timeout_total": 1000000,
                "timeout_connect": 2,
                "timeout_sock_connect": 15,
                "timeout_sock_read": 10,
                "translate_model": 'direct',  # 翻译方式   direc直译   back回译  extract不翻译直接提取提取
            }
        ],
                 enable_write_layer=False,
                 write_layer=[0, 2],
                 write_config={
                     "sep": '\t',
                     "index": False,
                     "header": None,  # 自定义列名
                     "na_rep": ' ',  # 缺失值占位符
                     "float_format": '%.2f',  # 浮点数格式化
                     "encoding": 'utf-8-sig'
                 },
                 is_display_banner=True
   ):
        self.__input_dir = input_dir
        self.__output_dir = output_dir
        self.__translate_tasks = translate_tasks
        self.__over_file = over_file
        self.__enable_write_layer = enable_write_layer
        self.__write_layer = write_layer
        self.__write_config = write_config
        self.__enable_translator = enable_translator
        if is_display_banner:
            print("""
           _____                   _   _______                  _       _             
          / ____|                 | | |__   __|                | |     | |            
         | |  __  ___   ___   __ _| | ___| |_ __ __ _ _ __  ___| | __ _| |_ ___  _ __ 
         | | |_ |/ _ \ / _ \ / _` | |/ _ \ | '__/ _` | '_ \/ __| |/ _` | __/ _ \| '__|
         | |__| | (_) | (_) | (_| | |  __/ | | | (_| | | | \__ \ | (_| | || (_) | |   
          \_____|\___/ \___/ \__, |_|\___|_|_|  \__,_|_| |_|___/_|\__,_|\__\___/|_|   
                              __/ |                                                   
                             |___/    欢迎使用google translator v1.2.0.2 © 202x Raodi.                                               
        """)
        print("已就绪")

    async def fetch(self, session, sub_list, src_lang, target_lang, url, proxy):
        # __src_lang = 'zh-CN'
        # __target_lang = 'vi'
        # __url = "https://translate.google.com/v1/api/google/translator"
        # __proxy = 'http://127.0.0.1:10809'
        try:
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
        except client_exceptions.ServerTimeoutError as timeout_error:
            print(f'发生异常 {timeout_error}')
        except Exception as e:
            print(f'发生异常 {e}')
        return False, ''

    async def read_file_async(self, src_file_path, min_row, max_row):
        async with aiofiles.open(src_file_path, mode='r', encoding='utf-8') as sfo:
            sfor = await sfo.readlines()
            sub_lists = self.random_len_sub_list(sfor, min_row, max_row)
            return sub_lists

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

    async def chunks(self, sem, session, sub_list, src_lang, target_lang, url, proxy):
        async with sem:
            success, data = await self.fetch(session, sub_list, src_lang, target_lang, url, proxy)
            return (success, data)

    def analyze_file(self, input_file_path):
        total_lines = 0
        empty_lines = 0
        bad_lines = 0
        with open(input_file_path, 'r', encoding='utf-8') as f:
            # 统计总行数和空行
            lines = f.readlines()
            total_lines = len(lines)
            empty_lines = sum(1 for line in lines if line.strip() == '')

            # 重置文件指针
            f.seek(0)
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                # 统计列数不等于1的行（格式错误）
                if len(row) != 1:
                    bad_lines += 1
        print(f"总行数: {total_lines}")
        print(f"空行数: {empty_lines}")
        print(f"格式错误行数: {bad_lines}")
        print(f"Pandas有效行数: {total_lines - empty_lines - bad_lines}")

    async def thread__retrieve_files(self, input_dir: str, output_dir: str, queue_pending: asyncio.Queue):
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

    def process_col2(self, target_list_item):
        # 去除换行符
        target_list_item = str(target_list_item).replace('\n', '').replace('\r', '')
        sglkd45d = ''

        if '<b>' in target_list_item:
            splists45ds = target_list_item.split('</b>')
            for i54s in range(len(splists45ds)):
                try:
                    if len(splists45ds[i54s].split("<b>")) > 1:
                        sglkd45d += splists45ds[i54s].split("<b>")[1]
                except Exception as e:
                    print(f"处理错误: {e}")
        else:
            sglkd45d = target_list_item

        return sglkd45d


    async def thread_read_files(self, queue_pending: asyncio.Queue):
        while True:
            # 记录开始时间
            start_time = time.time()
            input_file_path, input_file_name = await queue_pending.get()
            if input_file_path is None:
                logger.info("thread_read_files: 收到结束信号并传递")
                __over_list = []
                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                __over_list.append(now_time)
                async with aiofiles.open(self.__over_file, 'a', encoding='utf-8') as file_write_obj:
                    await file_write_obj.writelines(__over_list)
                break
            self.analyze_file( input_file_path)
            # 先读取为字符串列表
            with open(input_file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() != '']  # 跳过空行
            cleaned_data = [re.split(r'\t+', line, maxsplit=1)[0] for line in lines] # 用正则分割只保留第一列
            df = pd.DataFrame(cleaned_data)# 转换为DataFrame
            # df = pd.read_csv(
            #     input_file_path,
            #     sep='\t',
            #     header=None,
            #     skip_blank_lines=True,  # 保留空行
            #     on_bad_lines=lambda x: x,  # 保留格式错误行（Pandas ≥ 1.3.0）
            #     engine='python'            # 确保lambda支持
            # )  # 无表头时指定列名
            df_src_shape = df.shape
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            logger.info(f"（df_src_shape）: {df_src_shape}  ")
            if self.__enable_translator:
                # print("原始数据:")
                # print(df)
                # pd知识点应用 1.use this form to create a new column
                # 2. 在第一列前插入序号列（从1开始）
                #df.insert(0, -1, range(0, len(df)))
                # print("原始数据2:")
                # print(df)
                for translate_task_i, translate_task in enumerate(self.__translate_tasks):
                    #sub_lists = await self.read_file_async(input_file_path, translate_task["min_row"], translate_task["max_row"])
                    #new_col_name = "".join(translate_task["target_lang"])+"_"+str(translate_task_i)
                    #new_col_name = new_col_name.join("_").join(str(translate_task_i))
                    new_col_name = translate_task["target_line_index"]
                    df[new_col_name] = ""  # 初始化为空字符串
                    #df[len(df.columns) - 1] = ""  # 初始化为空字符串
                    # print("原始数据2-1:")
                    # print(df)
                    while True:
                        # pd知识点应用 1.1 根据某列的值为空复制出一个子表
                            # 筛选条件：cc列为空字符串的行
                        condition = df[new_col_name] == ""  # 精确匹配空字符串
                            # 创建子表（复制满足条件的行）
                        sub_df = df[condition].copy()  # 使用copy()避免SettingWithCopyWarning
                            # 打印结果
                        # print("子表（cc列为空的行）:")
                        # print(sub_df)
                        if not sub_df.empty:
                            # 子表有数据
                            sub_lists = self.random_len_sub_list(sub_df, translate_task["min_row"], translate_task["max_row"])
                            # print("原始数据3:")
                            # print(sub_lists)

                            sem = asyncio.Semaphore(translate_task["asyncio_semaphore"])
                            timeout = ClientTimeout(total=translate_task["timeout_total"],
                                                    connect=translate_task["timeout_connect"],
                                                    sock_connect=translate_task["timeout_sock_connect"],
                                                    sock_read=translate_task["timeout_sock_read"])
                            async with ClientSession(connector=TCPConnector(limit=translate_task["asyncio_semaphore"]),
                                                     timeout=timeout) as session:
                                #  pd知识点应用 2. 某列的数据转成字符串列表 sub_pd_list.iloc[:, translate_task["line_index"]+1].astype(str).tolist()
                                tasks = [
                                    (index, sub_pd_list, asyncio.create_task(self.chunks(sem, session, sub_pd_list.iloc[:,
                                                                                                       translate_task["line_index"]].astype(
                                        str).tolist(), translate_task["src_lang"],
                                                                                         translate_task["target_lang"],
                                                                                         translate_task["url"],
                                                                                         translate_task["proxy"])))
                                    for index, sub_pd_list in
                                    enumerate(sub_lists)
                                ]
                                for index, sub_pd_list, task in tasks:
                                    await task
                                    success, target_list3 = task.result()
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    try:
                                        if success:
                                            print(f"{current_time}\t\tsub_list: {len(sub_pd_list)}, result: {len(target_list3)}")
                                            # print(f"{current_time}\t\tsub_list: \n{sub_pd_list}, \n\nresult: {target_list3}")
                                            #  pd知识点应用 3. 获取索引列
                                            sub_psindex = sub_pd_list.index.astype(str).tolist()
                                            # print(f"{current_time}\t\tsub_psindex: \n{sub_psindex}\n\n")
                                            for sub_pd_row_i, target_text_content in zip(sub_psindex, target_list3):
                                                # print(
                                                #     f"{current_time}\t\tsub_pd_row_i: \n{sub_pd_row_i}, \n\ntarget_text_content: {target_text_content}")
                                                # 通过序号和列名修改
                                                df.at[int(sub_pd_row_i), new_col_name] = target_text_content
                                    except Exception as e:
                                        print(f'异常 {e}')
                            # print("原始数据5:")
                            # print(df)
                        else:
                            # 子表为空
                            break
                print('')
                # print(f"{translate_task['src_lang']},{translate_task['target_lang']}")
                # print("原始数据5:")
                # print(df)
                # print('')
                #### 写出前数据预处理
                for pd_index in range(df.columns.size):
                    df[pd_index] = df[pd_index].apply(self.process_col2)
                    #print(f'pd_index: {pd_index}')
            if self.__enable_write_layer:
                # 写出层过滤
                # 选择第0列和第2列（id和age）
                sub_df1 = df.iloc[:, self.__write_layer].copy()  # 使用copy()创建独立副本
                #print(f'sub_df1: {sub_df1}')
                print(self.__output_dir + '/' + input_file_name)
                sub_df1.to_csv(self.__output_dir + '/' + input_file_name,
                               sep=self.__write_config["sep"],
                               index=self.__write_config["index"],
                               header=self.__write_config["header"],  # 自定义列名
                               na_rep=self.__write_config["na_rep"],  # 缺失值占位符
                               float_format=self.__write_config["float_format"],  # 浮点数格式化
                               encoding=self.__write_config["encoding"])  # 带BOM的UTF-8（兼容Excel）
                # 记录结束时间
                end_time = time.time()
                # 计算执行时间（秒）
                elapsed_time = end_time - start_time
                df_new_shape = df.shape
                logger.info(f"（df_src_shape）: {df_src_shape}  -（df_new_shape）: {df_new_shape} ")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")
            else:
                # 完整写出
                #### 写出文件1
                # sub_list5 = df.iloc[:, 0].astype(str).tolist()
                # target_list5 = df.iloc[:, 1].astype(str).tolist()
                # await queue_write.put((self.__output_dir + '/' + input_file_name, sub_list5, target_list5))
                #### 写出文件2
                # 完整写出
                print(self.__output_dir + '/' + input_file_name)
                df.to_csv(self.__output_dir + '/' + input_file_name,
                          sep=self.__write_config["sep"],
                          index=self.__write_config["index"],
                          header=self.__write_config["header"],  # 自定义列名
                          na_rep=self.__write_config["na_rep"],  # 缺失值占位符
                          float_format=self.__write_config["float_format"],  # 浮点数格式化
                          encoding=self.__write_config["encoding"])  # 带BOM的UTF-8（兼容Excel）
                # 记录结束时间
                end_time = time.time()
                # 计算执行时间（秒）
                elapsed_time = end_time - start_time
                df_new_shape = df.shape
                logger.info(f"（df_src_shape）: {df_src_shape}  -（df_new_shape）: {df_new_shape} ")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")
                logger.info(f"执行耗时: {elapsed_time:.6f} 秒")






            # 通过序号和列名修改
            # df.at[70467, 1] = "new_value"
            # print("原始数据1:")
            # print(df)

            # print("原始数据2:")
            # print(sub_lists)
            # print("原始数据3:")
            # print(df)
                # print("原始数据4:")
                # for index, row in df.iterrows():
                #     # 使用列位置索引获取值
                #     value1 = row.iloc[0]
                #     value2 = row.iloc[1]
                #     print(f"原始数据5:{value1},{value2} ")

















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

    async def thread_write_files(self, queue_write: asyncio.Queue):
        while True:
            target_file4, sub_list4, target_list4 = await queue_write.get()
            await self.write_content_v3(target_file4, sub_list4, target_list4)
            logger.info(f"thread_write_files: 已写入数据 -> {target_file4}")
            queue_write.task_done()

    async def logic(self):
        """主协程：初始化队列并启动三个线程"""
        queue_pending = asyncio.Queue()
        queue_write = asyncio.Queue()

        # 创建并运行任务
        tasks = [
            asyncio.create_task(self.thread__retrieve_files(self.__input_dir, self.__output_dir, queue_pending)),
            asyncio.create_task(self.thread_read_files(queue_pending)),
            #asyncio.create_task(self.thread_write_files(queue_write))
        ]
        await asyncio.gather(*tasks)
        logger.info("所有线程已完成")

    def handler(self):
        asyncio.run(self.logic())


if __name__ == "__main__":
    AsyncGoogleBatchBackTranslatorFaster(
        input_dir=r"Z:\src_zh",
        output_dir=r"Z:\zh2vi",
        over_file='./over',
        enable_translator=True,
        translate_tasks=[
            {
                "src_lang": 'zh-CN',
                "target_lang": 'vi',
                "url": "https://translate.google.com/v1/api/google/translator",
                "proxy": 'http://127.0.0.1:10809',
                "min_row": 80,
                "max_row": 150,
                "full_line_translation": False,
                "line_segmentation": '\t',
                "line_index": 0,
                "target_line_index": 1,
                "copy_line_write": True,
                "asyncio_semaphore": 100,
                "timeout_total": 1000000,
                "timeout_connect": 20,
                "timeout_sock_connect": 12,
                "timeout_sock_read": 8,
            },{
                "src_lang": 'vi',
                "target_lang": 'zh-CN',
                "url": "https://translate.google.com/v1/api/google/translator",
                "proxy": 'http://127.0.0.1:10809',
                "min_row": 80,
                "max_row": 150,
                "full_line_translation": False,
                "line_segmentation": '\t',
                "line_index": 1,
                "target_line_index": 2,
                "copy_line_write": True,
                "asyncio_semaphore": 100,
                "timeout_total": 1000000,
                "timeout_connect": 20,
                "timeout_sock_connect": 12,
                "timeout_sock_read": 8,
            }
        ],
        enable_write_layer=False,
        write_layer=[1,2],
        write_config={
            "sep": '\t',
            "index": False,
            "header": None,  # 自定义列名
            "na_rep": ' ',  # 缺失值占位符
            "float_format": '%.2f',  # 浮点数格式化
            "encoding": 'utf-8-sig'
        }
    ).handler()



