#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pymongo

MONGODB='mongodb';

class Query:
    """universal query creator"""
    def __init__(self, db, db_type=MONGODB):
        self.db_type = db_type
        self.db = db
        if self.db_type == MONGODB:
            self.query = {}
    def location_withIn_box(self, slat, slon, elat, elon):
        if self.db_type == MONGODB:
            self.query['location'] = {'$within': {'$box':[[slat, slon],
                                                          [elat, elon]]}}
        return self
    def _gt(self, field, data):
        if self.db_type == MONGODB:
            self.query[field] = {"$gte":data}
        return self
    def _lt(self, field, data):
        if self.db_type == MONGODB:
            self.query[field] = {"$lt":data}
        return self
    def _in(self, field, start, end):
        if self.db_type == MONGODB:
            self.query[field] = {"$gte":start, '$lt':end}
        return self
    def date_after(self, date):
        return self._gt('date', date)
    def date_before(self, date):
        return self._lt('date', date)
    def date_between(self, sdate, edate):
        return self._in('date', sdate, edate)
    def mag_greater_than(self, mag):
        return self._gt('magnitude', mag)
    def mag_less_than(self, mag):
        return self._lt('magnitude', mag)
    def mag_between(self, low, high):
        return self._in('magnitude', low, high)
    def execute(self):
        if self.db_type == MONGODB:
            return self.db.find(self.query)



class MongoDB:
    """MongoDB backend"""
    def __init__(self, dbname, collection_name):
        self.conn = pymongo.Connection()
        self.db = self.conn[dbname]
        self.col = self.db[collection_name]
        self._create_index()
    def _create_index(self):
        self.col.create_index([('location', pymongo.GEO2D),
                               ('date', pymongo.ASCENDING),
                               ('magnitude', pymongo.ASCENDING)])
    def _insert(self, quake):
        self.col.insert({'date': quake['date'],
                         'depth': quake['depth'],
                         'location': [quake['latitude'],
                                      quake['longtitude']],
                         'magnitude': quake['magnitude'],
                         'mag_type':quake['mag_type']})
    def insert(self, quakes):
        if type(quakes) == list:
            for quake in quakes:
                self._insert(quake)
        else:
            self.insert(quake)
    def create_query(self):
        return Query(self.col, MONGODB)
    def find(self, query):
        return query.execute()
