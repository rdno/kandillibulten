# -*- coding: utf-8 -*-
import datetime
import poppler
import sys
import os
import re
import json

from optparse import OptionParser

class PdfData(object):
    def __init__(self, filename, startpage=1, endpage=None):
        self.filename = filename
        self.doc = self.open_pdf_doc(self.filename)
        self.startpage = startpage
        self.endpage = self.doc.get_n_pages()
        if endpage:
            self.endpage = endpage
        self.data = []
    def open_pdf_doc(self, filename):
        fullname = lambda x:'file://'+os.path.abspath(filename)
        return poppler.document_new_from_file(fullname(filename), '')
    def new_rect(self, x1, y1, x2, y2):
        r = poppler.Rectangle()
        r.x1 = x1
        r.y1 = y1
        r.x2 = x2
        r.y2 = y2
        return r
    def check_data(self, text, pat):
        p = re.compile(pat)
        return p.match(text)
    def get_text(self, page, x1, y1, x2, y2):
        return page.get_text(0, self.new_rect(x1, y1, x2, y2))
    def get_no(self, page, row_y):
        text = self.get_text(page, 0, row_y, 80, row_y)
        data = self.check_data(text, '(?P<no>\d+)\s*')
        if data:
            return int(data.group('no'))
        return None
    def get_datetime(self, page, row_y):
        t = lambda x1, x2: self.get_text(page, x1, row_y, x2, row_y)
        asInt = lambda x: int(x.group(0))
        getSec = lambda x: min(int(round(float(x.group(0)))), 59)
        day = self.check_data(t(90, 110), '(\d{1,2})\s*')
        month = self.check_data(t(120, 140), '(\d{1,2})\s*')
        year = self.check_data(t(150, 180), '(\d{4})\s*')
        hour = self.check_data(t(200, 220), '(\d{1,2})\s*')
        minute = self.check_data(t(230, 250), '(\d{1,2})\s*')
        second = self.check_data(t(260, 285), '(\d{1,2}\.\d)\s*')
        #data = self.check_data(t(90, 190), '(?P<date>\d+ \d+ \d{4})\s*')
        if day and month and year and hour and minute and second:
            return datetime.datetime(asInt(year),
                                     asInt(month),
                                     asInt(day),
                                     asInt(hour),
                                     asInt(minute),
                                     getSec(second))
        return None
    def get_coor(self, page, row_y):
        t = lambda x1, x2: self.get_text(page, x1, row_y, x2, row_y)
        asFloat = lambda x: float(x.group(0))
        coor_pat = '(\d{1,2}\.\d{1,2})\s*'
        lat = self.check_data(t(300, 340), coor_pat)
        longt = self.check_data(t(370, 410), coor_pat)
        ref = self.check_data(t(420, 440), '(\w)\s*')
        if lat and longt and ref:
            return {'lat':asFloat(lat),
                    'long':asFloat(longt),
                    'ref':ref.group(0)}
    def get_depth(self, page, row_y):
        t = lambda x1, x2: self.get_text(page, x1, row_y, x2, row_y)
        depth = self.check_data(t(460, 480), '(\d+)\s*')
        ref = self.check_data(t(500, 520), '(\w)\s*')
        if depth and ref:
            return {'depth':int(depth.group(0)),
                    'ref':ref.group(0)}
    def get_magnitude(self, page, y):
        xs = range(530, 780, 50)
        types = ['Ms', 'Mb', 'Md', 'Ml', 'Mw']
        getType = lambda x:types[xs.index(x)]
        n = lambda x: self.get_text(page, x+50, y, x+5, y+5) #rightToleft
        is_valid = re.compile('^\s*(?P<mag>\d\.\d)\s+(?P<ref>\w)\s*$')
        for x in xs:
            m = is_valid.match(n(x))
            if m:
                return {'magnitude':float(m.group('mag')),
                        'ref': m.group('ref'),
                        'type': getType(x)}
        fallback = re.compile('^\s*(?P<mag>\d\.\d)\s+[\w\d\.\s]+(?P<ref>\w)\s*$')
        for x in xs:
            f = fallback.match(n(x))
            if f:
                return {'magnitude':float(f.group('mag')),
                        'ref': f.group('ref'),
                        'type': getType(x)}
    def parse_data(self):
        if self.data:
            return self.data
        pages = (self.doc.get_page(x) for x in range(self.startpage-1,
                                                     self.endpage))
        ys = range(170, 570, 20)
        old_no = 0
        for page in pages:
            for y in ys:
                no = self.get_no(page, y)
                if no and no != old_no:
                    coor = self.get_coor(page, y)
                    depth = self.get_depth(page, y)
                    mag = self.get_magnitude(page, y)
                    self.data.append({'no': no,
                                      'date': self.get_datetime(page, y),
                                      'latitude': coor['lat'],
                                      'longtitude': coor['long'],
                                      'coor_ref': coor['ref'],
                                      'depth':depth['depth'],
                                      'depth_ref':depth['ref'],
                                      'magnitude':mag['magnitude'],
                                      'mag_type':mag['type'],
                                      'mag_ref':mag['ref']})
                    old_no = no
        return self.data
    def print_data(self):
        for quake in self.data:
            print "%4d %s %.2f %.2f %2d %.1f (%s)" % (quake['no'],
                                                      quake['date'],
                                                      quake['latitude'],
                                                      quake['longtitude'],
                                                      quake['depth'],
                                                      quake['magnitude'],
                                                      quake['mag_type'])
def data2json(data, jsonfilename):
    is_date = lambda x: isinstance(x, datetime.datetime)
    date_handler = lambda x: x.isoformat() if is_date(x) else None

    jsonfile = open(jsonfilename, 'w')
    json.dump(data, jsonfile, default=date_handler)

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
    (options, args) = parser.parse_args()
    if len(args) >= 1:
        pdf_data = PdfData(args[0], options.startpage, options.endpage)
        if options.timeit:
            import time
            start = time.time()
            pdf_data.parse_data()
            print "Data parsed in %.2f seconds." % (time.time() - start)
        if options.json:
            data2json(pdf_data.parse_data(), options.json)
        if options.printdata:
            pdf_data.parse_data()
            pdf_data.print_data()
