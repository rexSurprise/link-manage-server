# -*- coding: utf-8 -*-
"""
ScriptName: query
Project: Manager
Author: Rex_Surprise.
Create Date: 2020-10-02 20:54:50
Description:
"""
import hashlib
import pprint

__author__ = 'Rex_Surprise'

import pymysql


class Query(object):
    def __init__(self, host, port, user, password, database):
        self._conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)
        # 得到一个可以执行SQL语句的光标对象
        self._cursor = self._conn.cursor(
            cursor=pymysql.cursors.DictCursor)  # 执行完毕返回的结果集默认以字典显示
        # 得到一个可以执行SQL语句并且将结果作为字典返回的游标

    def select_category(self, uid):
        sql = 'select uname from userinfo where uid=%s'
        res = self.__select_db(sql, uid)
        if res:
            return res[0].get('uname')

    def select_all(self, options):
        rows = options.get('rows', 20)
        page = options.get('page', 1)
        keyword = options.get('keyword', None)
        sort = options.get('sort', 'DESC')
        sort_field = options.get('sortField', 'lid')
        sort_field = 'uid' if sort_field == 'category' else sort_field
        #  经测试存在SQL注入！ 修复ORDER BY的SQL注入
        sort_field = 'lid' if not sort_field.isalpha() else sort_field
        sort = 'DESC' if not sort.isalpha() else sort
        search = ''
        args = [(page - 1) * rows, rows]
        if keyword is not None:
            search = "WHERE `title` LIKE %s OR `link` LIKE %s OR `DESCRIBE` LIKE %s "
            [args.insert(0, '%{}%'.format(keyword)) for i in range(3)]
        sql = 'select * from links ' + search + f"ORDER BY `{sort_field}` {sort} limit %s,%s"
        # print(sql)
        return self.__select_db(sql, args)

    def select_count(self, options):
        keyword = options.get('keyword', None)
        search = ''
        args = []
        if keyword is not None:
            keyword = '%{}%'.format(keyword)
            search = "WHERE `title` LIKE %s OR `link` LIKE %s OR `DESCRIBE` LIKE %s "
            args = [keyword, keyword, keyword]
        sql = 'select count(*)  AS total from links ' + search

        return self.__select_db(sql, args)

    def add_item(self, data):
        """
        :param data: 必须包含的keys: [title,link,favicon,describe,category]
        :return: success ret True
        """
        sql = "INSERT INTO links VALUES(NULL, %s, %s, %s, %s, (SELECT uid FROM `userinfo` WHERE uname=%s));"
        return not not self.__execute_db(sql, [item[1] for item in data])

    def update_item(self, data):
        """
        :param data: 必须包含的keys: [title,link,favicon,describe,category, lid]
        :return: success ret True
        """
        print(data)
        sql = "UPDATE links SET title=%s, link=%s, favicon=%s, `describe`=%s, uid=(SELECT uid FROM `userinfo` WHERE uname=%s) WHERE lid=%s"
        return not not self.__execute_db(sql, [item[1] for item in data])

    def del_item(self, lid):
        sql = "delete from links where lid=%s"
        return not not self.__execute_db(sql, lid)

    def __del__(self):
        self._cursor.close()
        self._conn.close()

    def __select_db(self, sql, arg=None):
        """查询"""
        # 检查连接是否断开，如果断开就进行重连
        self._conn.ping(reconnect=True)
        # 使用 execute() 执行sql
        self._cursor.execute(sql, arg)
        # 使用 fetchall() 获取查询结果
        data = self._cursor.fetchall()
        return data

    def __execute_db(self, sql, arg):
        """更新/新增/删除"""
        try:
            # 检查连接是否断开，如果断开就进行重连
            self._conn.ping(reconnect=True)
            # 使用 execute() 执行sql
            res = self._cursor.execute(sql, arg)
            # 提交事务
            self._conn.commit()
            return res
        except Exception as e:
            print("操作出现错误：{}".format(e))
            # 回滚所有更改
            self._conn.rollback()


if __name__ == '__main__':
    conn = {
        'host': '192.168.0.124',
        'port': 3306,
        'user': 'root',
        'password': '1234',
        'database': 'rsnav'
    }
    q = Query(*conn.values())
    print(q.select_category(1))
    data = {
        'link': "https://www.lanqiao.cn/questions/102676/",
        'title': "Python练手项目",
        # 'lid': "02a44259755d38e615",
        'favicon': "https://fanyi-cdn.cdn.bcebos.com/static/translation/img/favicon/favicon-32x32_ca689c3.png",
        'describe': "随时在线流畅使用。",
        'category': "其他网站",
    }
    lst = ['title', 'link', 'favicon', 'describe', 'category']
    data_dict = sorted(data.items(), key=lambda item: lst.index(item[0]))
    print(()[0])
    # print(q.add_item(data))
    # print(q.update_item(data))
    # print(q.del_item(13))
