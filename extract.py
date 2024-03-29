#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Rıdvan Örsvuran (C) 2012
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import datetime
import json

from kandillibulten.database import MongoDB
from kandillibulten.parsers import PdfParser

def data2json(data, jsonfilename):
    is_date = lambda x: isinstance(x, datetime.datetime)
    date_handler = lambda x: x.isoformat() if is_date(x) else None

    jsonfile = open(jsonfilename, 'w')
    json.dump(data, jsonfile, default=date_handler)

def data2mongo(data, dbname):
    db = MongoDB(dbname, 'quakes')
    db.insert(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract data from pdf file")
    parser.add_argument("filetoparse", type=str,
                        help="Pdf file to parse")
    parser.add_argument("-s", "--start-page", dest="startpage", default=1,
                        type=int, help="First page to parse",
                        metavar="PAGE_NUM")
    parser.add_argument("-e", "--end-page", dest="endpage", default=None,
                        type=int, help="Last page to parse",
                        metavar="PAGE_NUM")
    parser.add_argument("-p", "--print",
                        action="store_true", dest="printdata",
                        default=False, help="Print parsed data")
    parser.add_argument("-t", "--timeit",
                      action="store_true", dest="timeit", default=False,
                      help="Calc parsing time")
    parser.add_argument("-j", "--dump-json", type=str, dest="json",
                      default=None, metavar="FILENAME",
                      help="Dump data to json file")
    parser.add_argument("-m", "--dump-mongodb", type=str, dest="mongo",
                      default=None, metavar="DB_NAME",
                      help="Dump data to mongodb")
    args = parser.parse_args()
    pdf_data = PdfParser(args.filetoparse,
                         args.startpage, args.endpage)
    if args.timeit:
        import time
        start = time.time()
        pdf_data.parse_data()
        print "Data parsed in %.2f seconds." % (time.time() - start)
    if args.json:
        data2json(pdf_data.parse_data(), args.json)
    if args.mongo:
        data2mongo(pdf_data.parse_data(), args.mongo)
    if args.printdata:
        pdf_data.parse_data()
        pdf_data.print_data()
