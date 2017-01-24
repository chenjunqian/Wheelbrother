#coding=utf-8
"""crawler database """
import MySQLdb
import json
import inspect
import model

class Store(object):

    def __init__(self):
        self.dbName = 'wheelbrother'
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root')
        self.conn.select_db(self.dbName)
        self.cur__ = self.conn.cursor()


    def save(self):
        '''store'''
        store_dic = {}
        attributes = inspect.getmembers(self, lambda attr: not inspect.isroutine(attr))

        for attr in attributes:
            if attr[0].startswith('__') or attr[0].endswith('__'):
                continue
            else:
                store_dic[attr[0]] = attr[1]
                print attr[0]
                print type(self.__getattribute__(attr[0]))

        print 'store_dic : '+'\n' + str(store_dic)

        filed_name = list()
        filed_value = list()
        for item in store_dic:
            filed_name.append(item)
            filed_value.append(store_dic[item])
        print tuple(filed_name)
        print tuple(filed_value)
        sqlcommand = 'INSERT INTO ' + self.dbName+ '_' + self.__class__.__name__ + str(tuple(filed_name)) + ' VALUE'+str(tuple(filed_value))
        self.cur__.execute(sqlcommand)
        self.cur__.close()
        self.conn.commit()
        self.conn.close()


class VoteupAnswer(Store):

    link = model.Filed()
    name = 'test name'
    question = 'test question'

    def __init__(self):
        self.user_link = 'a'
        self.username = 'user name'
        self.question_id = 'question id'
        VoteupAnswer.link = 'link'


if __name__ == '__main__':
    vote = VoteupAnswer();
    store = Store()

    vote.save()
