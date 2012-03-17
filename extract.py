# -*- coding: utf-8 -*-
import datetime
import json

from kandillibulten.database import MongoDB
from kandillibulten.parsers import PdfParser


from optparse import OptionParser

def data2json(data, jsonfilename):
    is_date = lambda x: isinstance(x, datetime.datetime)
    date_handler = lambda x: x.isoformat() if is_date(x) else None

    jsonfile = open(jsonfilename, 'w')
    json.dump(data, jsonfile, default=date_handler)

def data2mongo(data, dbname):
    db = MongoDB(dbname, 'quakes')
    db.insert(data)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] filetoparse.pdf")
    parser.add_option("-s", "--start-page", dest="startpage", default=1,
                      type="int",
                      help="First page to parse", metavar="PAGE_NUM")
    parser.add_option("-e", "--end-page", dest="endpage", default=None,
                      help="Last page to parse", metavar="PAGE_NUM")
    parser.add_option("-p", "--print",
                      action="store_true", dest="printdata", default=False,
                      help="Print parsed data")
    parser.add_option("-t", "--timeit",
                      action="store_true", dest="timeit", default=False,
                      help="Calc parsing time")
    parser.add_option("-j", "--dump-json", type="string", dest="json",
                      default=None, metavar="FILENAME",
                      help="Dump data to json file")
    parser.add_option("-m", "--dump-mongodb", type="string", dest="mongo",
                      default=None, metavar="DB_NAME",
                      help="Dump data to mongodb")
    (options, args) = parser.parse_args()
    if len(args) >= 1:
        pdf_data = PdfParser(args[0], options.startpage, options.endpage)
        if options.timeit:
            import time
            start = time.time()
            pdf_data.parse_data()
            print "Data parsed in %.2f seconds." % (time.time() - start)
        if options.json:
            data2json(pdf_data.parse_data(), options.json)
        if options.mongo:
            data2mongo(pdf_data.parse_data(), options.mongo)
        if options.printdata:
            pdf_data.parse_data()
            pdf_data.print_data()
