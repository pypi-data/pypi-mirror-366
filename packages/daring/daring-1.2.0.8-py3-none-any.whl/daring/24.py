#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import asyncio

from daring import AsyncGoogleBatchTranslator

if __name__ == "__main__":
    AsyncGoogleBatchTranslator(
        full_line_translation=False, line_segmentation='\t', line_index=0, copy_line_write=True,
        src_txt_dir=r'E:\temp\data2\data1', target_txt_dir=r'E:\temp\data2\target2',
        min_row=100, max_row=100,
        asyncio_semaphore=400, timeout_total=10, timeout_connect=2, timeout_sock_connect=15, timeout_sock_read=5,
        retries=3,
        url="https://translate-pa.googleapis.com/v1/translateHtml",
        src_lang='zh-CN',
        target_lang='en',
        proxy='http://127.0.0.1:10809').handler()
    asyncio.run()