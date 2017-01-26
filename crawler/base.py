#coding=utf-8
"""crawler database """
import MySQLdb
import json
import inspect

class BaseModel(object):

    def __init__(self, **kwargs):
        print 'init : '+str(self)
        self.db = 'wheelbrother'
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root')
        self.conn.select_db(self.db)
        self.cur__ = self.conn.cursor()
        if len(kwargs) > 0:
            sqlcommand = 'SELECT * FROM ' + self.db + '_' + self.__class__.__name__ + ' WHERE '
            for name, value in kwargs.items():
                if isinstance(value, str):
                    sqlcommand = sqlcommand+str(name)+ '=' + "'" +str(value) + "'" + ' '
                else:
                    sqlcommand = sqlcommand+str(name)+ '=' +str(value) + ' '
            print sqlcommand


    def save(self):
        '''store'''
        store_dic = {}
        attributes = inspect.getmembers(self, lambda attr: not inspect.isroutine(attr))

        for attr in attributes:
            if attr[0].startswith('__') or attr[0].endswith('__'):
                continue
            else:
                store_dic[attr[0]] = attr[1]

        filed_name = list()
        filed_value = list()
        for name, value in store_dic.items():
            filed_name.append(name)
            filed_value.append(value)
        sqlcommand = 'INSERT INTO ' + self.db + '_' + self.__class__.__name__ + str(tuple(filed_name)) + ' VALUE'+str(tuple(filed_value))
        self.cur__.execute(sqlcommand)
        self.cur__.close()
        self.conn.commit()
        self.conn.close()

