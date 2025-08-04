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

import execjs
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
                             |___/    欢迎使用google translator v1.2.0.4 © 202x Raodi.                                               
        """)
        print("已就绪")

    class AsyncGoogleChunksTranslator():
        def __init__(self):
            self.v1 = self.V1()
            self.v2 = self.V2()

        class V2():
            def __init__(self):
                print('')

            async def translator(self, session, sub_list, src_lang, target_lang, url, proxy):
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

        class V1():
            def __init__(self):
                ########################### 20250801 s 旧版本Google翻译接口
                self.__ctkk_text = ''
                self.__ip_function_text = ''

            async def get_ctkk(self, session, proxy):
                if not self.__ctkk_text.__eq__(''):
                    # print('实时解析 ctkk 缓存', 'ctkk_text')
                    return self.__ctkk_text
                # else:
                #     print('实时解析 ctkk 正在解析', 'ctkk_text')
                text = ''
                for index in range(0, 100, 1):
                    try:
                        url = "https://translate.googleapis.com/translate_a/element.js?cb=cr.googleTranslate.onTranslateElementLoad&aus=true&clc=cr.googleTranslate.onLoadCSS&jlc=cr.googleTranslate.onLoadJavascript&hl=zh-CN&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
                        headers = {
                            'Host': 'translate.googleapis.com',
                            'google-translate-element-mode': 'library',
                            'sec-fetch-site': 'none',
                            'sec-fetch-mode': 'no-cors',
                            'sec-fetch-dest': 'empty',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
                        }
                        async with session.get(
                                url,
                                headers=headers,
                                ssl=True,
                                proxy=proxy
                        ) as response:
                            if response.status == 200:
                                text = await response.text()
                                self.__ctkk_text = text
                                break
                    except client_exceptions.ServerTimeoutError as timeout_error:
                        print(f'发生异常 {timeout_error}')
                    except Exception as e:
                        print(f'发生异常 {e}')
                return text

            async def get_Ip_function(self, session, proxy):
                if not self.__ip_function_text.__eq__(""):
                    # print('实时解析 ip_function_text 缓存', 'ip_function_text')
                    return self.__ip_function_text
                # else:
                #     print('实时解析2 ip_function_text 正在解析', 'ip_function_text')
                text = ''
                for index in range(0, 100, 1):
                    try:
                        url = "https://translate.googleapis.com/_/translate_http/_/js/k=translate_http.tr.zh_CN.tkO0SjOXurA.O/d=1/exm=el_conf/ed=1/rs=AN8SPfr4R06bzWa8J9Q9Jn0yl57_-Ifg0w/m=el_main"
                        payload = {}
                        headers = {
                            'authority': 'translate.googleapis.com',
                            'accept': '*/*',
                            'accept-language': 'zh-CN,zh;q=0.9',
                            'origin': 'https://www.google.com',
                            'referer': 'https://www.google.com/',
                            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'cross-site',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                            'x-client-data': 'CJa2yQEIprbJAQipncoBCM/rygEIkqHLAQiFoM0BCOuxzQEI3L3NAQiRys0BCLnKzQEIy9bNAQin2M0BCIXazQEI4drNAQim3M0BCOzdzQEIl97NAQi23s0BCKvfzQEI+cDUFRj2yc0B'
                        }
                        async with session.get(
                                url,
                                headers=headers,
                                ssl=True,
                                proxy=proxy
                        ) as response:
                            if response.status == 200:
                                text = await response.text()
                                # print(f'text1-2: {text}')
                                self.__ip_function_text = text
                                break
                    except client_exceptions.ServerTimeoutError as timeout_error:
                        print(f'发生异常1 {timeout_error}')
                    except Exception as e:
                        print(f'发生异常2 {e}')
                # print(f'text1-2:{text}')
                return text

            async def get_compile_str(self, session, proxy):
                jdndfd = await self.parse_ctkk('', session, proxy)
                uhfnm = await self.get_Ip_function(session=session, proxy=proxy)
                ihd = await self.parse_Ip_function(text=uhfnm, session=session, proxy=proxy)
                return """
                  function dr(a) {
                      return function() {
                          return a
                      }
                  }
                  function er(a, b) {
                      for (var c = 0; c < b.length - 2; c += 3) {
                          var d = b.charAt(c + 2);
                          d = "a" <= d ? d.charCodeAt(0) - 87 : Number(d);
                          d = "+" == b.charAt(c + 1) ? a >>> d : a << d;
                          a = "+" == b.charAt(c) ? a + d & 4294967295 : a ^ d
                      }
                      return a
                  }
                  """ + ihd + """
                  function gr(a) {
                      var b = '""" + jdndfd + """'.split(".")
                        , c = Number(b[0]) || 0;
                      a = Ip(a);
                      for (var d = c, e = 0; e < a.length; e++)
                          d += a[e],
                          d = er(d, "+-a^+6");
                      d = er(d, "+-3^+b+-f");
                      d ^= Number(b[1]) || 0;
                      0 > d && (d = (d & 2147483647) + 2147483648);
                      b = d % 1E6;
                      return b.toString() + "." + (b ^ c)
                  }
                  """

            async def parse_Ip_function(self, text, session, proxy):
                text = await self.get_Ip_function(session=session, proxy=proxy)
                ip_function = ''
                ip_function_iter = re.compile(r'Ip\=function.*?};', re.S).findall(text)
                if ip_function_iter.__len__() > 0:
                    ip_function = ip_function_iter[0]
                if not ip_function.__eq__(""):
                    ip_function = ip_function.replace('Ip=function(a)', 'function Ip(a)')
                    return ip_function
                else:
                    yugifj = await self.get_Ip_function(session=session, proxy=proxy)
                    return self.parse_Ip_function(text=yugifj, session=session, proxy=proxy)

            async def parse_ctkk(self, text, session, proxy):
                text = await self.get_ctkk(session, proxy)
                ctkk = ''
                ctkk_iter = re.compile(r'c\._ctkk\=\'(?P<ctkk>.*?)\'\;', re.S).findall(text)
                if ctkk_iter.__len__() > 0:
                    ctkk = ctkk_iter[0]
                if not ctkk.__eq__(""):
                    return ctkk
                else:
                    tyu = await self.parse_ctkk(text=self.get_ctkk(session, proxy), session=session, proxy=proxy)
                    return tyu

            async def google_plugin_translator_v1(self, src_lang, words, target_lang, session, url, proxy):
                ctx = execjs.compile("""
                function dr(a) {
                    return function() {
                        return a
                    }
                }
                function er(a, b) {
                    for (var c = 0; c < b.length - 2; c += 3) {
                        var d = b.charAt(c + 2);
                        d = "a" <= d ? d.charCodeAt(0) - 87 : Number(d);
                        d = "+" == b.charAt(c + 1) ? a >>> d : a << d;
                        a = "+" == b.charAt(c) ? a + d & 4294967295 : a ^ d
                    }
                    return a
                }
                function Ip(a) {
                   for (var b = [], c = 0, d = 0; d < a.length; d++) {
                        var e = a.charCodeAt(d);
                        128 > e ? b[c++] = e : (2048 > e ? b[c++] = e >> 6 | 192 : (55296 == (e & 64512) && d + 1 < a.length && 56320 == (a.charCodeAt(d + 1) & 64512) ? (e = 65536 + ((e & 1023) << 10) + (a.charCodeAt(++d) & 1023),
                        b[c++] = e >> 18 | 240,
                        b[c++] = e >> 12 & 63 | 128) : b[c++] = e >> 12 | 224,
                        b[c++] = e >> 6 & 63 | 128),
                        b[c++] = e & 63 | 128)
                    }
                    return b
                }
                function gr(a) {
                    var b = '471841.3618545003'.split(".")
                      , c = Number(b[0]) || 0;
                    a = Ip(a);
                    for (var d = c, e = 0; e < a.length; e++)
                        d += a[e],
                        d = er(d, "+-a^+6");
                    d = er(d, "+-3^+b+-f");
                    d ^= Number(b[1]) || 0;
                    0 > d && (d = (d & 2147483647) + 2147483648);
                    b = d % 1E6;
                    return b.toString() + "." + (b ^ c)
                }


                """)
                # words = ["Chính sách trang web", "Điều khoản dịch vụ API của Google"]
                tk = ctx.call('gr', "".join(words))

                try:
                    payload = {"q": words}
                    headers = {
                        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-ch-ua-mobile': '?0',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                        'content-type': 'application/x-www-form-urlencoded',
                        'origin': 'https://developers.google.cn',
                        'x-client-data': 'CJa2yQEIprbJAQipncoBCM/rygEIlKHLAQiFoM0BCOuxzQEI3L3NAQiRys0BCLnKzQEIy9bNAQin2M0BCIXazQEI4drNAQim3M0BCOzdzQEI+cDUFRj2yc0B',
                        'sec-fetch-site': 'cross-site',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-dest': 'empty',
                        'referer': 'https://developers.google.cn/',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9'
                    }
                    url = "https://translate.googleapis.com/translate_a/t?anno=3&client=te_lib&format=html&v=1.0&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw&logld=vTE_20231023&sl=" + src_lang + "&tl=" + target_lang + "&tc=0&tk=" + tk
                    async with session.post(
                            url,
                            headers=headers,
                            data=payload,
                            ssl=True,
                            proxy=proxy
                    ) as response:
                        if response.status == 200:
                            text = await response.text()
                            # print(f'text0-0: {text}')
                            return True, text
                except client_exceptions.ServerTimeoutError as timeout_error:
                    print(f'发生异常 {timeout_error}')
                except Exception as e:
                    print(f'发生异常 {e}')
                # print(f'text0-1: {text}')
                return False, ''

            async def google_plugin_translator_v2(self, src_lang, words, target_lang, session, url, proxy):
                try:
                    ghdjf = await self.get_compile_str(session, proxy)
                    ctx = execjs.compile(ghdjf)
                    # words = ["Chính sách trang web", "Điều khoản dịch vụ API của Google"]
                    tk = ctx.call('gr', "".join(words))
                    payload = {"q": words}
                    url = "https://translate.googleapis.com/translate_a/t?anno=3&client=te_lib&format=html&v=1.0&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw&logld=vTE_20231023&sl=" + src_lang + "&tl=" + target_lang + "&tc=0&tk=" + tk
                    headers = {
                        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-ch-ua-mobile': '?0',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                        'content-type': 'application/x-www-form-urlencoded',
                        'origin': 'https://developers.google.cn',
                        'x-client-data': 'CJa2yQEIprbJAQipncoBCM/rygEIlKHLAQiFoM0BCOuxzQEI3L3NAQiRys0BCLnKzQEIy9bNAQin2M0BCIXazQEI4drNAQim3M0BCOzdzQEI+cDUFRj2yc0B',
                        'sec-fetch-site': 'cross-site',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-dest': 'empty',
                        'referer': 'https://developers.google.cn/',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9'
                    }
                    async with session.post(
                            url,
                            headers=headers,
                            data=payload,
                            ssl=True,
                            proxy=proxy
                    ) as response:
                        if response.status == 200:
                            text = await response.text()
                            return True, text
                except client_exceptions.ServerTimeoutError as timeout_error:
                    print(f'发生异常 {timeout_error}')
                except Exception as e:
                    print(f'发生异常 {e}')
                    self.__ip_function_text = ''
                    self.__ctkk_text = ''
                return False, ''

            async def translator(self, session, sub_list, src_lang, target_lang, url, proxy):
                text = ''
                for index in range(0, 3, 1):
                    try:
                        isFinsh, text = await self.google_plugin_translator_v1(src_lang, sub_list, target_lang, session,
                                                                               url, proxy)
                        # print(f'text0: {text}')
                    except Exception as e:
                        text = ''
                    if not text is None and not text.__eq__(""):
                        # print('翻译结果：', '谷歌接口', '静态解析', text)
                        break
                if text.__eq__(""):
                    text = ''
                    for index in range(0, 100, 1):
                        try:
                            isFinsh1, text = await self.google_plugin_translator_v2(src_lang, sub_list, target_lang,
                                                                                    session, url, proxy)
                            # print(f'text1: {text}')
                        except Exception as e:
                            text = ''
                        if not text is None and not text.__eq__(""):
                            # print('翻译结果：', '谷歌接口', '实时解析', text)
                            break
                # print(f'text: {text}')
                if not text.__eq__(""):
                    result1 = json.loads(text)
                    return True, result1
                else:
                    return False, []

            ########################### 20250801 e


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

    async def chunks(self, sem, session, sub_list, src_lang, target_lang, url, proxy, api_version):
        async with sem:
            AGCTranslator = self.AsyncGoogleChunksTranslator()
            if api_version == 1:
                success, data = await AGCTranslator.v1.translator(session, sub_list, src_lang, target_lang, url, proxy)
            elif api_version == 2:
                success, data = await AGCTranslator.v2.translator(session, sub_list, src_lang, target_lang, url, proxy)
            else:
                success, data = await AGCTranslator.v2.translator(session, sub_list, src_lang, target_lang, url, proxy)
            #success, data = await self.fetch(session, sub_list, src_lang, target_lang, url, proxy)
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
            #self.analyze_file( input_file_path)
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
                                                                                         translate_task["proxy"],
                                                                                         translate_task["api_version"])))
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
                "api_version": 1,
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
                "api_version": 1,
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



