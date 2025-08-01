# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/9 16:50

import sqlite3


class Sqlite(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()

    def tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        result = self.search(query)
        #  result 为: [('sqlite_sequence',), ('NtRequired',)]
        if len(result) != 0:
            return [item[0] for item in result]

    def search(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        rows = self.cursor.fetchall()
        return rows

    def update(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    pass
