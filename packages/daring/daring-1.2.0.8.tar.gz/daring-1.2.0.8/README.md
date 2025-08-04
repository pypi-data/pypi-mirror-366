# daring
---
# daring 工具

[![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)
[![Build Status](https://gitee.com/mingSoft/MCMS/badge/star.svg?theme=dark)](https://gitee.com/Raodi/daring)

## 目录

- [简介](#简介)
- [功能](#功能)
- [安装](#安装)
- [示例](#示例)
- [使用](#使用)
- [SQL使用](#SQL使用)
- [贡献](#贡献)
- [许可证](#许可证)

## 简介

daring 是一套Python脚本，专为自动化翻译流程而设计。这套脚本包含了一系列的函数，用于处理从文本预处理到API调用的各种翻译相关任务。

## 功能

- **批量翻译**：支持对大量文本进行高效翻译。
- **格式转换**：自动将文本从一种格式转换为另一种，例如从HTML实体到实际字符。
- **API集成**：与多个翻译服务提供商的API集成，如Google Translate API。
- **错误处理**：内置错误处理机制，确保在出现故障时仍能优雅地运行。
- **性能优化**：利用缓存和异步处理技术提高翻译效率。

## 安装

确保你的环境中已安装Python 3.8或更高版本。

```bash
 pip install daring
    或者
 pip install daring  -i https://pypi.python.org/simple
```

## 示例
 1.直接当作翻译工具函数使用
```bash
from daring import GoogleBatchTranslator

if __name__ == "__main__":
    logic = GoogleBatchTranslator(src_lang='zh-CH', target_lang='id', network_singleton=True,
                                  url="http://0.0.0.0:1111/v1/api/google/translator")
    result = logic.handler(src_list=['脚本'])
    print(result)
    result = logic.handler(
        src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
        is_purified=True,
        is_decoded=True)
    print(result)
    result = logic.handler(
        src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
        is_purified=True)
    print(result)
    result = logic.handler(src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"])
    print(result)
    result = logic.handler(src_lang='auto', src_list=['ဟယ်လို'], target_lang='zh-TW')
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'])
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_decoded=True)
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_purified=True, is_decoded=True)
    print(result)
```
执行结果如下：
```bash
E:\rd\tool\python3.8.1\python.exe D:/PyProject/test_daring/test_daring.py

       _____                   _   _______                  _       _             
      / ____|                 | | |__   __|                | |     | |            
     | |  __  ___   ___   __ _| | ___| |_ __ __ _ _ __  ___| | __ _| |_ ___  _ __ 
     | | |_ |/ _ \ / _ \ / _` | |/ _ \ | '__/ _` | '_ \/ __| |/ _` | __/ _ \| '__|
     | |__| | (_) | (_) | (_| | |  __/ | | | (_| | | | \__ \ | (_| | || (_) | |   
      \_____|\___/ \___/ \__, |_|\___|_|_|  \__,_|_| |_|___/_|\__,_|\__\___/|_|   
                          __/ |                                                   
                         |___/    欢迎使用google translator v1.1.12.1 © 202x Raod.                                               
    
已就绪
{'code': '200', 'data': ['naskah'], 'msg': 'success', 'time': '0.22986245155334473'}
{'code': '200', 'data': ['Yang Ying kembali menimbulkan sensasi baru-baru ini. Dia telah debut selama bertahun-tahun, tetapi jika menyangkut karya representatifnya, semua orang masih belum bisa langsung mengatakannya.Bagaimanapun, dia selalu dianggap sebagai "halo" di industri hiburan.'], 'msg': 'success', 'time': '0.2324509620666504'}
{'code': '200', 'data': ['Yang Ying kembali menimbulkan sensasi baru-baru ini. Dia telah debut selama bertahun-tahun, tetapi jika menyangkut karya representatifnya, semua orang masih belum bisa langsung mengatakannya.Bagaimanapun, dia selalu dianggap sebagai &quot;halo&quot; di industri hiburan.'], 'msg': 'success', 'time': '0.2035074234008789'}
{'code': '200', 'data': ['<i>杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。</i> <b>Yang Ying kembali menimbulkan sensasi baru-baru ini. Dia telah debut selama bertahun-tahun, tetapi jika menyangkut karya representatifnya, semua orang masih belum bisa langsung mengatakannya.</b><i>毕竟在娱乐圈中，她一直被认为是个“hello”。</i> <b>Bagaimanapun, dia selalu dianggap sebagai &quot;halo&quot; di industri hiburan.</b>'], 'msg': 'success', 'time': '0.23633670806884766'}
{'code': '200', 'data': [['你好呀', 'my']], 'msg': 'success', 'time': '0.18155121803283691'}
{'code': '200', 'data': ['Dikotomi secara rekursif menangani data yang hilang, dia dianggap sebagai &quot;halo&quot;'], 'msg': 'success', 'time': '0.17732763290405273'}
{'code': '200', 'data': ['Dikotomi secara rekursif menangani data yang hilang, dia dianggap sebagai "halo"'], 'msg': 'success', 'time': '0.2064962387084961'}
{'code': '200', 'data': ['Dikotomi secara rekursif menangani data yang hilang, dia dianggap sebagai "halo"'], 'msg': 'success', 'time': '0.25403642654418945'}
已退出

Process finished with exit code 0
```

## 使用
```bash
from daring import GoogleBatchTranslator

if __name__ == "__main__":
    ## 使用方法1： 目录下txt文件批量行处理
    # logic = GoogleBatchTranslator(src_lang='zh-CH', target_lang='id', network_singleton=False, min_row=130, max_row=180,
    #                                   src_txt_dir=r'E:\temp\txt_translation_task\data_txt\data',
    #                                   target_txt_dir=r'E:\temp\txt_translation_task\data_txt\target_',
    #                                   url="http://0.0.0.0:1111/v1/api/google/translator",
    #                                   reading_thread_number=35, processing_thread_number=35, writing_thread_number=35,
    #                                   forced_reconnection=True, forced_reconnection_min=2, forced_reconnection_max=5)
    # logic.handler()


    # # ## 使用方法2： 仅进行网络请求 -- 完整写法
    logic = GoogleBatchTranslator(src_lang='zh-CH', target_lang='id', network_singleton=True, url="http://0.0.0.0:1111/v1/api/google/translator")
    result = logic.handler(src_list=['脚本'])
    print(result)
    result = logic.handler(
        src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
        is_purified=True,
        is_decoded=True)
    print(result)
    result = logic.handler(
        src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"],
        is_purified=True)
    print(result)
    result = logic.handler(src_list=["杨颖最近再次引起了轰动，她已经出道多年了，但是提到她的代表作品时，大家仍然无法立刻说出。毕竟在娱乐圈中，她一直被认为是个“hello”。"])
    print(result)
    result = logic.handler(src_lang='auto', src_list=['ဟယ်လို'], target_lang='zh-TW')
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'])
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_decoded=True)
    print(result)
    result = logic.handler(src_list=['二分法递归处理丢失的数据，她一直被认为是个“hello”'], is_purified=True, is_decoded=True)
    print(result)
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

```


## SQL使用
通过字典生成sql并操作mysql数据表
```bash
from daring import RSql

if __name__ == "__main__":
     rSql = RSql(connect=pymysql.connect(
                     user='root',
                     password='123456',
                     db='f_saas_cfg',
                     host='127.0.0.1',
                     port=3306,
                     charset='utf8mb4'
                 ))
    # 1.数据插入
    data_dic = {
        'id': '2312312',
        'name': 'lisi223',
        'del': 0
    }
    rSql.insert(table_name='test_table', dict=data_dic, fail_event=fail_)
    # 2.数据更新
    data_dic_new = {
        'id': '2312312',
        'name': 'lisi2266',
        'del': 0
    }
    rSql.update(
        table_name='test_table', dict=data_dic_new, filter_dict_key_list=[],
        fail_event=fail_, is_enabled_where=True, where_dict={
            "name": "lisi223"
        })
    # 3.数据存在查询
    is_exists = rSql.exists(table_name='test_table', dict=data_dic, filter_dict_key_list=[], is_enabled_where=True,
                        where_dict={
                            "name": "lisi2266"
                        })
    print('is_exists', is_exists)
    # 4.数据删除
    rSql.delete(table_name='test_table', is_enabled_where=True, where_dict={
        "name": "lisi2266"
    })
    # 5.查询全部数据
    result = rSql.query_all(table_name='test_table')
    print(result)
    # 6.查询全部数据
    result = rSql.query_all_field(table_name='test_table', dict=data_dic, filter_dict_key_list=["id"])
    print(result)
    # 7.条件查询
    result = rSql.query_where(table_name='test_table', dict=data_dic, filter_dict_key_list=[], is_enabled_where=True,
                              where_dict={
                                  "id": 2312312
                              })
    print(result)
    # 8.条件查询
    result = rSql.query(table_name='test_table', dict=data_dic, filter_dict_key_list=['del'], is_enabled_where=True,
                        where_dict={
                            "id": 2312312
                        })
    print(result)
```
执行结果如下：
```bash
E:\rd\tool\python3.8.1\python.exe D:/PyProject/test_daring/test_daring.py
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 插入成功！	INSERT INTO test_table(id,name,del) values('2312312','lisi223','0')
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 更新成功！	UPDATE test_table SET id='2312312' ,name='lisi2266' ,del='0'  WHERE  name = 'lisi223'
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 查询成功！	select case when EXISTS( SELECT  obj.id, obj.name, obj.del FROM test_table AS obj WHERE  obj.name = 'lisi2266' ) then True else False end as result
is_exists True
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 删除成功！	DELETE FROM test_table WHERE  name = 'lisi2266'
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 查询成功！	SELECT * FROM test_table
[{'id': '42376fc5-6301-11eb-81ae-0242ac110003', 'name': '33', 'del': '1'}, {'id': '425caff4-6301-11eb-81ae-0242ac110003', 'name': '33', 'del': '1'}, {'id': '42825c8a-6301-11eb-81ae-0242ac110003', 'name': '33', 'del': '1'}, {'id': '42a6d445-6301-11eb-81ae-0242ac110003', 'name': '33', 'del': '1'}, {'id': '42c60d8d-6301-11eb-81ae-0242ac110003', 'name': '33', 'del': '1'}, {'id': 'b83da5c2-6301-11eb-81ae-0242ac110003', 'name': '66', 'del': '1'}, {'id': 'e5f910d1-6302-11eb-81ae-0242ac110003', 'name': '88', 'del': '1'}, {'id': '2344422222222222222223434343434344', 'name': '34', 'del': '1'}, {'id': '234333333333333333333333333333333333', 'name': '433', 'del': '1'}, {'id': '1112233333333333222', 'name': '323', 'del': '1'}, {'id': '232322222222222222222222222', 'name': '323', 'del': '1'}, {'id': '2323222222222222222222222222222', 'name': '222', 'del': '1'}, {'id': '21321', 'name': '222', 'del': '1'}, {'id': '21321', 'name': '222', 'del': '1'}, {'id': '213', 'name': '111', 'del': '1'}, {'id': '123123', 'name': '2323', 'del': '1'}, {'id': '123123', 'name': '2323', 'del': '1'}, {'id': '12312321', 'name': '232', 'del': '1'}, {'id': '9999', 'name': '9999', 'del': '0'}, {'id': '9999', 'name': '9999', 'del': '0'}, {'id': '77777', 'name': '77777', 'del': '1'}, {'id': '6666', 'name': '6666', 'del': '0'}, {'id': '76767676', 'name': '76767676', 'del': '0'}, {'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '1'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '1'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}]
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 查询成功！	SELECT  obj.name, obj.del  FROM test_table AS obj
[{'name': '33', 'del': '1'}, {'name': '33', 'del': '1'}, {'name': '33', 'del': '1'}, {'name': '33', 'del': '1'}, {'name': '33', 'del': '1'}, {'name': '66', 'del': '1'}, {'name': '88', 'del': '1'}, {'name': '34', 'del': '1'}, {'name': '433', 'del': '1'}, {'name': '323', 'del': '1'}, {'name': '323', 'del': '1'}, {'name': '222', 'del': '1'}, {'name': '222', 'del': '1'}, {'name': '222', 'del': '1'}, {'name': '111', 'del': '1'}, {'name': '2323', 'del': '1'}, {'name': '2323', 'del': '1'}, {'name': '232', 'del': '1'}, {'name': '9999', 'del': '0'}, {'name': '9999', 'del': '0'}, {'name': '77777', 'del': '1'}, {'name': '6666', 'del': '0'}, {'name': '76767676', 'del': '0'}, {'name': 'lisi', 'del': '0'}, {'name': 'zhangsan', 'del': '0'}, {'name': 'zhangsan', 'del': '0'}, {'name': 'zhangsan', 'del': '0'}, {'name': 'zhangsan', 'del': '0'}, {'name': 'zhangsan', 'del': '0'}, {'name': 'zhangsan5555', 'del': '1'}, {'name': 'zhangsan5555', 'del': '1'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'zhangsan5555', 'del': '0'}, {'name': 'lisi', 'del': '0'}, {'name': 'lisi', 'del': '0'}, {'name': 'lisi222', 'del': '0'}, {'name': 'lisi222', 'del': '0'}, {'name': 'lisi222', 'del': '0'}, {'name': 'lisi222', 'del': '0'}, {'name': 'lisi222', 'del': '0'}, {'name': 'lisi222', 'del': '0'}]
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 查询成功！	SELECT  obj.id, obj.name, obj.del FROM test_table AS obj WHERE  obj.id = '2312312'
[{'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '1'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '1'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'zhangsan5555', 'del': '0'}, {'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'lisi', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}, {'id': '2312312', 'name': 'lisi222', 'del': '0'}]
2024-07-25 16:53:09 INFO  ☠ 数据库操作 ： 查询成功！	SELECT  obj.id, obj.name FROM test_table AS obj WHERE  obj.id = '2312312'
[{'id': '2312312', 'name': 'lisi'}, {'id': '2312312', 'name': 'zhangsan'}, {'id': '2312312', 'name': 'zhangsan'}, {'id': '2312312', 'name': 'zhangsan'}, {'id': '2312312', 'name': 'zhangsan'}, {'id': '2312312', 'name': 'zhangsan'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'zhangsan5555'}, {'id': '2312312', 'name': 'lisi'}, {'id': '2312312', 'name': 'lisi'}, {'id': '2312312', 'name': 'lisi222'}, {'id': '2312312', 'name': 'lisi222'}, {'id': '2312312', 'name': 'lisi222'}, {'id': '2312312', 'name': 'lisi222'}, {'id': '2312312', 'name': 'lisi222'}, {'id': '2312312', 'name': 'lisi222'}]

Process finished with exit code 0
```

## 贡献
欢迎任何贡献！无论是修复bug、添加新功能还是改进现有代码，我们都乐于接受。请遵循我们的贡献指南提交pull request。

## 许可证
本项目使用Apache-2.0 + 自定义许可，详情参见LICENSE文件。