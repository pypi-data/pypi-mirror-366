import csv
import re
import time

import pymysql


class RSql():
    def __init__(self,
                 connect=None,
                 transcribe_failed='./transcribe_failed.csv'):
        """
        :param connect: MySQL连接，示例用法 pymysql.connect(
                     user='root',
                     password='123456',
                     db='f_saas_cfg',
                     host='127.0.0.1',
                     port=3308,
                     charset='utf8mb4'
                 )
        :param transcribe_failed:
        """
        self.sQLActuator = self.SQLActuator()
        self.sQLActuatorCore = self.SQLActuatorCore(transcribe_failed=transcribe_failed)
        self.sQLActuatorResult = self.SQLActuatorResult()
        self.sQLGenerator = self.SQLGenerator()
        self.connect = connect

    def insert(self, table_name, dict, fail_event):
        """
         数据插入 -- 用法： rSql.insert(table_name='test_table', dict=data_dic, fail_event=fail_)
        :param table_name: 表名
        :param dict: 字典数据，只取key
        :param fail_event:   函数为 def fail_(e): print('失败了 '+e)
        :return:
        """
        self.sQLActuator.Insert(
            sql=self.sQLGenerator.generater_sql(
                sql_type='insert',
                table_name=table_name,
                data_dic=dict
            ),
           Query_connect=self.connect,
           Event=self.sQLActuatorCore.insert,
           Fail_Event=fail_event
        )

    def update(self, table_name, dict, filter_dict_key_list, fail_event, is_enabled_where=True, where_dict=None):
        """
        数据更新 -- 用法：
            rSql.update(
                table_name='test_table', dict=data_dic_new, filter_dict_key_list=[],
                fail_event=fail_, is_enabled_where=True, where_dict={
                    "name": "zhangsan1"
                })
        :param table_name: 表名
        :param dict: 字典数据,只取key
        :param filter_dict_key_list: 过滤dict中的key，值为dict中的key名字列表
        :param fail_event: 更新失败事件
        :param is_enabled_where: 是否启用where条件
        :param where_dict: where条件字典
        :return:
        """
        if where_dict is None:
            where_dict = {}
        self.sQLActuator.Update(
            sql=self.sQLGenerator.generater_sql(
                sql_type='update',
                table_name=table_name,
                data_dic=dict,
                fir_arr=filter_dict_key_list,
                is_where=is_enabled_where,
                where_variables=where_dict
            ),
            update_connect=self.connect,
            Event=self.sQLActuatorCore.update,
            Fail_Event=fail_event
        )

    def exists(self, table_name, dict, filter_dict_key_list, is_enabled_where=True, where_dict=None):
        """
        查询数据是否存在 -- 用法：
         resss = rSql.exists(table_name='test_table', dict=data_dic, filter_dict_key_list=[], is_enabled_where=True, where_dict={
            "name": "zhangsan1"
        })
        :param table_name: 表名
        :param dict: 字典数据，只取key作为表字段
        :param filter_dict_key_list:  过滤dict中的key，值为dict中的key名字列表
        :param is_enabled_where: 是否启用where条件
        :param where_dict: where条件字典
        :return: True存在 或者 False 不存在
        """
        if where_dict is None:
            where_dict = {}
        return self.sQLActuator.Query_Exist(
            sql=self.sQLGenerator.generater_sql(
                sql_type='select_exists',
                table_name=table_name,
                data_dic=dict,
                fir_arr=filter_dict_key_list,
                is_where=is_enabled_where,
                where_variables=where_dict
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.query,
            Event_Assert=self.sQLActuatorResult.record_exist
        )

    def delete(self, table_name, is_enabled_where=True, where_dict=None):
        """
         删除表中数据 -- 用法：
           rSql.delete(table_name='test_table', is_enabled_where=True, where_dict={
                "name": "zhangsan1"
            })
        :param table_name: 表名
        :param is_enabled_where: where条件字典
        :param where_dict: True存在 或者 False 不存在
        :return:
        """
        if where_dict is None:
            where_dict = {}
        self.sQLActuator.Delete(
            sql=self.sQLGenerator.generater_sql(
                sql_type='delete',
                table_name=table_name,
                is_where=is_enabled_where,
                where_variables=where_dict
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.delete)

    def query_all(self, table_name):
        """
        查询表中全部数据 -- 用法：
               result = rSql.query_all(table_name='test_table')
        :param table_name: 表名
        :return: 字典数据列表
        """
        return self.sQLActuator.Query(
                sql=self.sQLGenerator.generater_sql(
                sql_type='select_all',
                table_name=table_name
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.query_all
        )

    def query_all_field(self, table_name, dict, filter_dict_key_list):
        """
        查询表中全部数据 -- 用法：
            result = rSql.query_all_field(table_name='test_table', dict=data_dic, filter_dict_key_list=["id"])
        :param table_name: 表名
        :param dict: 字典数据，只取key作为表字段
        :param filter_dict_key_list: 过滤dict中的key，值为dict中的key名字列表
        :return: 字典数据列表
        """
        return self.sQLActuator.Query(
            sql=self.sQLGenerator.generater_sql(
                sql_type='select_def',
                table_name=table_name,
                data_dic=dict,
                fir_arr=filter_dict_key_list
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.query_all
        )

    def query_where(self, table_name, dict, filter_dict_key_list, is_enabled_where=True, where_dict=None):
        """
         条件查询 -- 用法：
         result = rSql.query_where(table_name='test_table', dict=data_dic, filter_dict_key_list=[], is_enabled_where=True, where_dict={
            "id": 2312312
            })
        :param table_name: 表名
        :param dict: 字典数据，只取key作为表字段
        :param filter_dict_key_list: 过滤dict中的key，值为dict中的key名字列表
        :param is_enabled_where: 是否启用where条件
        :param where_dict: where条件字典数据
        :return: 字典数据列表
        """
        if where_dict is None:
            where_dict = {}
        return self.sQLActuator.Query(
                sql=self.sQLGenerator.generater_sql(
                sql_type='select_dei_where',
                table_name=table_name,
                data_dic=dict,
                fir_arr=filter_dict_key_list,
                is_where=is_enabled_where,
                where_variables=where_dict
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.query_all
        )

    def query(self, table_name, dict, filter_dict_key_list, is_enabled_where=True, where_dict=None):
        """
            条件查询 -- 用法：
                 result = rSql.query(table_name='test_table', dict=data_dic, filter_dict_key_list=[], is_enabled_where=True, where_dict={
                    "id": 2312312
                    })
                :param table_name: 表名
                :param dict: 字典数据，只取key作为表字段
                :param filter_dict_key_list: 过滤dict中的key，值为dict中的key名字列表
                :param is_enabled_where: 是否启用where条件
                :param where_dict: where条件字典数据
                :return: 字典数据列表
                """
        if where_dict is None:
            where_dict = {}
        return self.sQLActuator.Query(
                sql=self.sQLGenerator.generater_sql(
                sql_type='select_def_where',
                table_name=table_name,
                data_dic=dict,
                fir_arr=filter_dict_key_list,
                is_where=is_enabled_where,
                where_variables=where_dict
            ),
            Query_connect=self.connect,
            Event=self.sQLActuatorCore.query_all
        )



    class SQLActuator():
        def __init__(self):
            self.name = ''

        def Query_Exist(self, sql, Query_connect, Event, Event_Assert):
            """
                查询数据表中是否存在某一条数据
            :param sql: sql语句
            :param Query_Users_connect: 数据连接配置
            :param Event: 查询方法
            :param Event1: 查询结果的返回函数
            :return:
            """
            results = Event(sql, Query_connect)
            return Event_Assert(results)

        def Query(self, sql, Query_connect, Event):
            """
                查询数据表中是否存在某一条数据
            :param sql: sql语句
            :param Query_Users_connect: 数据连接配置
            :param Event: 查询方法
            :param Event1: 查询结果的返回函数
            :return:
            """
            return Event(sql, Query_connect)

        def Update(self, sql, update_connect, Event, Fail_Event):
            """
                 数据表更新操作
            :param sql: SQL更新语句
            :param update_connect:  数据库连接配置
            :param Event: 更新方法
            :param Event1: 异常处理处理方法
            :param fail_logs: 异常日志文件写出路径
            :param except_data: 异常保存内容
            :return:
            """
            return Event(sql, update_connect, Fail_Event)

        def Insert(self, sql, Query_connect, Event, Fail_Event):
            """
                向数据表中插入某一项
            :param sql: sql语句
            :param Query_Users_connect: 数据连接配置
            :param Event: 查询方法
            :param Event1: 查询结果的返回函数
            :return:
            """
            return Event(sql, Query_connect, Fail_Event)

        def Delete(self, sql, Query_connect, Event):
            """
                删除数据表中某一项
            :param sql: sql语句
            :param Query_Users_connect: 数据连接配置
            :param Event: 查询方法
            :return:
            """
            return Event(sql, Query_connect)

    class SQLActuatorCore():
        def __init__(self, transcribe_failed):
            self.name = ''
            # self.page_internal_spider_transcribe_failed = '../temp/Inserter/_page_internal_spider_transcribe_failed.csv'
            self.page_internal_spider_transcribe_failed = transcribe_failed

        def query(self, sql_str, query_connect):
            """
                数据库的通用查询方法
            :param sql_str:
            :param query_connect:
            :return:
            """
            query_connect.ping()  # 放开上一次的链接，重新打开
            cursors = query_connect.cursor()
            try:
                cursors.execute(sql_str)
                query_connect.commit()
                results = cursors.fetchall()
                print("\033[36m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' INFO ' + ' ☠ 数据库操作 ： 查询成功！\t' + str(
                    sql_str) + "\033[0m")
                return results
            except Exception as e:
                print("\033[33m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' Error ' + ' ☠ 数据库操作 ： 查询失败！\t' + str(
                    sql_str) + "\033[0m")
            finally:
                cursors.close()

        def query_all(self, sql_str, query_connect):
            """
                数据库的通用查询方法
            :param sql_str:
            :param query_connect:
            :return:
            """
            # query_connect.ping()  # 放开上一次的链接，重新打开
            cursors = query_connect.cursor()
            try:
                cursors.execute(sql_str)
                query_connect.commit()
                # 获取所有列的名称
                column_names = [desc[0] for desc in cursors.description]
                # 使用字典推导式和fetchall()方法获取所有行，并形成字典列表
                results = [dict(zip(column_names, row)) for row in cursors.fetchall()]
                print("\033[36m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' INFO ' + ' ☠ 数据库操作 ： 查询成功！\t' + str(sql_str) + "\033[0m")
                return results
            except Exception as e:
                print("\033[33m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' Error ' + ' ☠ 数据库操作 ： 查询失败！\t' + str(sql_str) + "\033[0m")
            finally:
                cursors.close()

        def update(self, sql, update_connect, Event):
            update_cursor = update_connect.cursor()  # 更新数据表
            # print(sql)
            try:
                update_cursor.execute(sql)
                update_connect.commit()
                print("\033[36m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' INFO ' + ' ☠ 数据库操作 ： 更新成功！\t' + str(
                    sql) + "\033[0m")
            except Exception as e:
                update_connect.rollback()
                print("\033[33m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' Error ' + ' ☠ 数据库操作 ： 更新失败！\t' + str(
                    sql) + "\033[0m")
                Event(str(e))
            finally:
                update_cursor.close()

        def delete(self, sql, delete_connect):
            update_cursor = delete_connect.cursor()  # 更新数据表
            # print(sql)
            try:
                update_cursor.execute(sql)
                delete_connect.commit()
                print("\033[36m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' INFO ' + ' ☠ 数据库操作 ： 删除成功！\t' + str(
                    sql) + "\033[0m")
            except Exception as e:
                delete_connect.rollback()
                print("\033[33m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' Error ' + ' ☠ 数据库操作 ： 删除失败！\t' + str(
                    sql) + "\033[0m")
            finally:
                update_cursor.close()

        def insert(self, sql_str, connect, Fail_Event):
            # connect.ping(reconnect=True)
            cursors = connect.cursor()
            try:
                cursors.execute(sql_str)
                connect.commit()
                print("\033[36m" +str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' INFO ' + ' ☠ 数据库操作 ： 插入成功！\t' + str(sql_str) + "\033[0m")
            except Exception as e:
                connect.rollback()
                print("\033[33m" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + ' Error ' + ' ☠ 数据库操作 ： 插入失败！\t' + str(
                    sql_str) + "\033[0m")
                Fail_Event(str(e))
            finally:
                cursors.close()



        def saveLogsFiles(self, logs_files_path, data):
            with open(logs_files_path, "a+", encoding='utf-8', newline='') as file:
                csv_file = csv.writer(file)
                csv_file.writerow(data)

    class SQLActuatorResult():
        def __init__(self):
            self.name = ''

        def record_exist(self, results):
            """
                判断数据表中某行数据是否存在
            :param results: 返回结果为 0 或者 1
            :return: True 或者 False
            """
            try:
                if results[0][0] == 0:
                    return False
                if results[0][0] == 1:
                    return True
            except:
                return False

        def len_exist(self, results):
            """
                 # 表中已存在该数据，允许继续操作
            :param results: 返回结果为 0 或者 1
            :return: True 或者 False
            """
            try:
                if len(results) > 0:
                    return True
                else:
                    return False
            except:
                return False

        def Assembly_Following_Collections_Results(self, results):
            """
                判断数据表中某行数据是否存在
            :param results: 返回结果为 0 或者 1
            :return: True 或者 False
            """
            assembly_following_clle = []
            try:
                for re_index, re_row in enumerate(results):
                    # print(str(re_index)+"__"+str(re_row))
                    clle_data = [re_row[0], re_row[1], re_row[2], re_row[3], re_row[4]]
                    assembly_following_clle.append(clle_data)
            except:
                print("affair_query <Assembly_Following_Collections_Results> Error: " + str(results))
            return assembly_following_clle

        def update_except(self, except_data, fail_logs):
            """
                更新数据异常时，进行文件转写
            :param except_data:
            :param Following_update_spider_status_fail_logs:
            :return:
            """
            with open(fail_logs, "a+", newline='') as file:
                csv_file = csv.writer(file)
                csv_file.writerow(except_data)

        def getUserScreenNameResults(self, results):
            """
                判断数据表中某行数据是否存在
            :param results: 返回结果为 0 或者 1
            :return: True 或者 False
            """
            try:
                return results[0][1]
            except:
                print("affair_query <len_exist> Error: " + str(results))
                return False

        def getSpiderCacheResults(self, results):
            return results

        def getUserLikesResults(self, results):
            assembly_following_clle = []
            for re_index, re_row in enumerate(results):
                if str(re_row[4]).strip() != str('over'):
                    # print(str(re_index)+"__"+str(re_row))
                    clle_data = [re_row[0], re_row[1], re_row[2], re_row[3], re_row[4]]
                    assembly_following_clle.append(clle_data)
            return assembly_following_clle

        def get_profile_picture_uri(self, results):
            """
                通用的查询返回集合函数
            :param results:
            :return:
            """
            # return results
            result_list = []
            for r_index, r_value in enumerate(results):
                result_list.append(r_value)
            return result_list

    class SQLGenerator():
        def __init__(self):
            self.name = ''

        def generater_select_all(self, table_name):
            """
               全表查询 - 通过爬取到的字典，自动生成全表查询的SQL语句
            :param table_name:
            :param variables:
            :return:
            """
            return 'SELECT * ' + 'FROM ' + str(table_name)

        # select xx.aaa,xxx.bbb(ccc,ddd,ee) form xx
        def generater_select_define(self, table_name, variables, f_variables):
            """
                全表查询 - 自定义过滤查询的结果
            :param table_name:
            :param variables:
            :param f_variables:
            :return:
            """
            fb_fex = 'obj'
            fb_com = ''
            str_cr = ','
            for t_i, t_dic in enumerate(variables):
                # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                fb_user_clo = str(t_dic)
                if not fb_user_clo in f_variables:
                    if t_i == (len(variables) - 1):
                        str_cr = ''
                    fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr + """ """
            if str(fb_com).endswith(', '):
                fb_com = str(fb_com).rstrip(', ')
            return 'SELECT ' + """ """ + str(fb_com) + """ """ + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex)

        # select * form xx where xx.aaa = '' ....
        def generater_select_all_where(self, table_name, variables, is_where, where_variables):
            fb_fex = 'fb_user'
            fb_com = ''
            str_cr = ','
            for t_i, t_dic in enumerate(variables):
                # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                fb_user_clo = str(t_dic)
                if fb_user_clo == 'id':
                    fb_user_clo = 'con_id'
                if t_i == (len(variables) - 1):
                    str_cr = ''
                fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr + """
            """
            where_str = ''
            if is_where:
                for w_i, w_dic in enumerate(where_variables):
                    if w_i == 0:
                        where_str = where_str + 'WHERE '
                    where_str = where_str + ' ' + str(fb_fex) + '.' + str(w_dic) + ' = \'' + str(
                        where_variables[str(w_dic)]) + '\''
                    if w_i < (len(where_variables) - 1):
                        where_str = where_str + ' AND '
            return 'SELECT ' + """
            """ + str(fb_fex) + '.id,' + """
            """ + str(fb_com) + """
        """ + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex) + """
        """ + where_str

        # select xx.aaa,xxx.bbb(ccc,ddd,ee)  form xx where xx.aaa = '' ....
        def generater_select_define_where(self, table_name, variables, f_variables, is_where, where_variables):
            """
                select xx.aaa,xxx.bbb(ccc,ddd,ee)  form xx where xx.aaa = '' ....
            :param table_name:
            :param variables:
            :param f_variables:
            :param is_where:
            :param where_variables:
            :return:
            """
            fb_fex = 'obj'
            fb_com = ''
            str_cr = ','
            for t_i, t_dic in enumerate(variables):
                # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                fb_user_clo = str(t_dic)
                if not fb_user_clo in f_variables:
                    # if fb_user_clo == 'id':
                    #     fb_user_clo = 'con_id'
                    if t_i == (len(variables) - 1):
                        str_cr = ''
                        fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr
                    if t_i < (len(variables) - 1):
                        fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr + """ """

            where_str = ''
            if is_where:
                for w_i, w_dic in enumerate(where_variables):
                    if w_i == 0:
                        where_str = where_str + 'WHERE '
                    where_str = where_str + ' ' + str(fb_fex) + '.' + str(w_dic) + ' = \'' + str(
                        where_variables[str(w_dic)]) + '\''
                    if w_i < (len(where_variables) - 1):
                        where_str = where_str + ' AND '
            else:
                return 'SELECT * ' + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex)
            if str(fb_com).endswith(', '):
                fb_com = str(fb_com).rstrip(', ')
            return 'SELECT ' + """ """ + str(fb_com) + ' ' + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex) + """ """ + where_str

        def generater_select_defini_where(self, table_name, variables, f_variables, is_where, where_variables):
            """
                select xx.aaa,xxx.bbb(ccc,ddd,ee)  form xx where xx.aaa = '' ....
            :param table_name:
            :param variables:
            :param f_variables:
            :param is_where:
            :param where_variables:
            :return:
            """
            fb_fex = 'obj'
            fb_com = ' '
            str_cr = ','
            # for t_i, t_dic in enumerate(variables):
            #     # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
            #     if t_i == (len(f_variables) - 1):
            #         fb_com = fb_com + str(fb_fex) + '.' + str(t_dic)
            #         break
            #     fb_com = fb_com + str(fb_fex) + '.' + str(t_dic) + ', '
            for t_i, t_dic in enumerate(variables):
                # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                fb_user_clo = str(t_dic)
                if not fb_user_clo in f_variables:
                    # if fb_user_clo == 'id':
                    #     fb_user_clo = 'con_id'
                    if t_i == (len(variables) - 1):
                        str_cr = ''
                        fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr
                    if t_i < (len(variables) - 1):
                        fb_com = fb_com + str(fb_fex) + '.' + str(fb_user_clo) + str_cr + """ """

            where_str = ''
            if is_where:
                for w_i, w_dic in enumerate(where_variables):
                    if w_i == 0:
                        where_str = where_str + 'WHERE '
                    where_str = where_str + ' ' + str(fb_fex) + '.' + str(w_dic) + ' = \'' + str(
                        where_variables[str(w_dic)]) + '\''
                    if w_i < (len(where_variables) - 1):
                        where_str = where_str + ' AND '
            else:
                return 'SELECT * ' + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex)
            if str(fb_com).endswith(', '):
                fb_com = str(fb_com).rstrip(', ')
            return 'SELECT ' + str(fb_com) + ' ' + 'FROM ' + str(table_name) + ' AS ' + str(fb_fex) + """ """ + where_str

        def generater_delete_where(self, table_name, is_where, where_variables):
            """
                条件删除 - 数据表中的某行
            :param table_name:
            :param is_where:
            :param where_variables:
            :return:
            """
            where_str = ''
            fb_fex = 'fb_user'
            if is_where:
                for w_i, w_dic in enumerate(where_variables):
                    if w_i == 0:
                        where_str = where_str + ' WHERE '
                    where_str = where_str + ' ' + str(w_dic) + ' = \'' + str(
                        where_variables[str(w_dic)]) + '\''
                    if w_i < (len(where_variables) - 1):
                        where_str = where_str + '  AND '
            return 'DELETE FROM ' + str(table_name) + where_str

        def generater_exists_byselect(self, qu_str):
            """
                生成某一行存在的查询 - 如果存在结果返回1 否则0
            :param qu_str:
            :return:
            """
            return 'select case when EXISTS( ' + qu_str + ' ) then True else False end as result'

        def generater_insert(self, table_name, variables):
            """
                根据字典 -- 自动生成 insert sql 语句
            :param table_name:
            :param variables:
            :return:
            """
            key = ''
            fex_key = ''
            fex_value = ''
            for t_i, t_dic in enumerate(variables):
                # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                fb_user_clo = str(t_dic)
                # if str(t_dic) == 'id':
                #     fb_user_clo = 'con_id'
                fb_user_value = str(variables[str(t_dic)])
                if fb_user_value.__contains__('\''):
                    fb_user_value = re.sub(r'\'', '"', fb_user_value)
                if t_i == (len(variables) - 1):
                    key = key + fb_user_clo
                    fex_key = fex_key + '"%s"'
                    fex_value = fex_value + '\'' + str(fb_user_value) + '\''
                    break
                key = key + fb_user_clo + ','
                fex_key = fex_key + '"%s"' + ','
                fex_value = fex_value + '\'' + str(fb_user_value) + '\'' + ','
            # sql = 'INSERT INTO ' + str(table_name) + '('+str(key)+') values('+str(fex_key)+')' % (str(fex_value))
            sql = 'INSERT INTO ' + str(table_name) + '(' + str(key) + ') values(' + str(fex_value) + ')'
            return sql

        def generater_update(self, table_name, variables, f_variables, is_where, where_variables):
            """
                安照条件生成更新语句
            :param table_name:
            :param variables:
            :param is_where:
            :param where_variables:
            :return:
            """
            fec_str = ''
            for t_i, t_dic in enumerate(variables):
                fb_user_clo = str(t_dic)
                if not fb_user_clo in f_variables:
                    # if str(t_dic) == 'id':
                    #     fb_user_clo = 'con_id'
                    fb_user_value = str(variables[str(t_dic)])
                    if fb_user_value.__contains__('\''):
                        fb_user_value = re.sub(r'\'', '"', fb_user_value)
                    # print("正在进行自动化构建mysql数据表的查询语句-->" + str(t_i) + " -->" + str(t_dic) + " -->" + str(variables[str(t_dic)]))
                    # if t_i == (len(variables) - 1):
                    #     fec_str = fec_str + fb_user_clo + '=\'' + fb_user_value + '\''
                    fec_str = fec_str + fb_user_clo + '=\'' + fb_user_value + '\' ,'
            where_str = ''
            fb_fex = 'fb_user'
            if is_where:
                for w_i, w_dic in enumerate(where_variables):
                    if w_i == 0:
                        where_str = where_str + ' WHERE '
                    where_str = where_str + ' ' + str(w_dic) + ' = \'' + str(
                        where_variables[str(w_dic)]) + '\''
                    if w_i < (len(where_variables) - 1):
                        where_str = where_str + '  AND '
            sql = 'UPDATE ' + str(table_name) + ' SET ' + fec_str[0:len(fec_str) - 1] + where_str
            return sql

        def generater_sql(self, sql_type, table_name, data_dic=None, fir_arr=None, is_where=False,
                          where_variables=None):
            """
                自动 SQL 语句生成器 - 逻辑控制器
            :param sql_type: 类型 - 返回自动生成SQL的类型
            :param table_name: 表名称 - 为哪一张表生成SQL有语句
            :param data_dic: 元数据字典 - 根据哪个数据源字典生成SQL语句
            :param fir_arr: 过滤元组 - 指定的一个数组进行过滤掉元数据字典中的某一项，所以其内容为元数据字典的键值对的键
            :param is_where: 是否让条件语句生效
            :param where_variables: 条件元组字典 - 指定的一个元组字典进行自动生成一个条件语句
            :return: 返回自动生成的SQL语句，最终错误返回为该表的 select * frmo xx 内容
            """
            if data_dic is None:
                data_dic = {}
            if fir_arr is None:
                fir_arr = ['no_thing']
            if where_variables is None:
                where_variables = {}
            """
            示例：
                select_exists_sql = generater_sql('select_exists', 'tw_tweet_sent_result',
                                                          data_dic, ['no_thing'], True,
                                                          where_variables={
                                                              'conversation_id_str': str(data_dic['conversation_id_str']),
                                                              'id_str': str(data_dic['id_str']),
                                                              'user_id_str': str(data_dic['user_id_str']),
                                                              'rest_id': str(data_dic['rest_id']),
                                                              'favorite_count': str(data_dic['favorite_count'])})
                        insert_sql = generater_sql('insert', 'tw_tweet_sent_result',
                                                   data_dic, ['no_thing'], True,
                                                   where_variables={
                                                       'conversation_id_str': str(data_dic['conversation_id_str']),
                                                       'id_str': str(data_dic['id_str']),
                                                       'user_id_str': str(data_dic['user_id_str']),
                                                       'rest_id': str(data_dic['rest_id']),
                                                       'favorite_count': str(data_dic['favorite_count'])})
                        update_sql = generater_sql('update', 'tw_tweet_sent_result',
                                                   data_dic, ['no_thing'], True,
                                                   where_variables={
                                                       'conversation_id_str': str(data_dic['conversation_id_str']),
                                                       'id_str': str(data_dic['id_str']),
                                                       'user_id_str': str(data_dic['user_id_str']),
                                                       'rest_id': str(data_dic['rest_id']),
                                                       'favorite_count': str(data_dic['favorite_count'])})

                # # 注释部分的内容，是根据爬取到的内容自动进行建表 -- 曾经一度因为超出单行最大存储数据量而弃用
                # # if (create_exits_logic_definc('facebook_spider,fb_user1', tableBuildStr(datae))):
                # #     print(' 数据表创建成功！')
                # # 0.查询语句 - 条件查询
                # select_all_sql = generater_select_all('fb_user1', data_dic)
                # select_def_sql = generater_select_define('fb_user1', data_dic, ['no_thing'])
                # select_def_where_sql = generater_select_define_where('fb_user1', data_dic, ['no_thing'], True,
                #                                                      where_variables={'con_id': '331', 'user_id': '332'})
                # # 1.询问数据是否存在 - select exit   sql = 'select case when EXISTS( ) then True else False end as result'
                # select_exists_sql = generater_exists_byselect(select_def_where_sql)
                # # 2.条件删除某条数据 - DELETE FROM tb_courses WHERE course_id = 4;
                # delete_where_sql = generater_delete_where('fb_user1', True, where_variables={'con_id': '221', 'user_id': '222'})
                # # 3.插入某条数据
                # insert_sql = generater_insert('fb_user4', data_dic)
                # # 4.更新某条数据 - 条件更新
                # update_sql = generater_update('fb_user4', data_dic, True, where_variables={'con_id': '999188666785524', 'user_id': '999188666785524'})
                :param data_dic:
                :return:
                """
            # 0.查询语句 - 条件查询
            if sql_type == 'select_all':
                return self.generater_select_all(table_name)
            if sql_type == 'select_def':
                return self.generater_select_define(table_name, data_dic, fir_arr)
            # 条件询问型的条件查询
            if sql_type == 'select_dei_where':
                return self.generater_select_defini_where(table_name, data_dic, fir_arr, is_where, where_variables)
            # 过滤型的条件查询
            if sql_type == 'select_def_where':
                return self.generater_select_define_where(table_name, data_dic, fir_arr, is_where, where_variables)
            # 1.询问数据是否存在 - select exit   sql = 'select case when EXISTS( ) then True else False end as result'
            if sql_type == 'select_exists':
                select_def_where_sql = self.generater_select_define_where(table_name, data_dic, fir_arr, is_where,
                                                                          where_variables)
                return self.generater_exists_byselect(select_def_where_sql)
            # 2.条件删除某条数据 - DELETE FROM tb_courses WHERE course_id = 4;
            if sql_type == 'delete':
                return self.generater_delete_where(table_name, is_where, where_variables)
            # 3.插入某条数据
            if sql_type == 'insert':
                return self.generater_insert(table_name, data_dic)
            # 4.更新某条数据 - 条件更新
            if sql_type == 'update':
                return self.generater_update(table_name, data_dic, fir_arr, is_where, where_variables)
            return self.generater_select_all(table_name)
