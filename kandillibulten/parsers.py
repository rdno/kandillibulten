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

import datetime
import os
import poppler
import re

class PdfParser(object):
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
    def get_id(self, page, row_y):
        text = self.get_text(page, 0, row_y, 80, row_y)
        data = self.check_data(text, '(\d+)\s*')
        if data:
            return int(data.group(1))
        return None
    def get_datetime(self, page, row_y):
        t = lambda x1, x2: self.get_text(page, x1, row_y, x2, row_y)
        asInt = lambda x: int(x.group(1))
        getSec = lambda x: min(int(round(float(x.group(1)))), 59)
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
        asFloat = lambda x: float(x.group(1))
        coor_pat = '(\d{1,2}\.\d{1,2})\s*'
        lat = self.check_data(t(300, 340), coor_pat)
        longt = self.check_data(t(370, 410), coor_pat)
        ref = self.check_data(t(420, 440), '(\w)\s*')
        if lat and longt and ref:
            return {'lat':asFloat(lat),
                    'long':asFloat(longt),
                    'ref':ref.group(1)}
    def get_depth(self, page, row_y):
        t = lambda x1, x2: self.get_text(page, x1, row_y, x2, row_y)
        depth = self.check_data(t(460, 480), '(\d+)\s*')
        ref = self.check_data(t(500, 520), '(\w)\s*')
        if depth and ref:
            return {'depth':int(depth.group(1)),
                    'ref':ref.group(1)}
    def find_rectangle_to_selection(self, t, page_height):
        h = t.y2 -t.y1
        n = self.new_rect(t.x1, page_height-t.y1,
                          t.x2, page_height-t.y2)
        return n
    def is_magnitude_in_right_row(self, mag, page, rect, page_height):
        def same_row(f, s):
            if f.y1 >= (s.y1+s.y2)/2 >= f.y2:
                return True
            return False
        for rec in page.find_text(mag):
            sel = self.find_rectangle_to_selection(rec, page_height)
            if same_row(sel, rect):
                return True
        return False
    def get_magnitude(self, page, y, page_height):
        xs = [741, 687, 634, 581, 527]
        types = ['Mw', 'Ml', 'Md', 'Mb', 'Ms']
        getType = lambda x:types[xs.index(x)]
        n = lambda x: self.get_text(page, x+25, y, x+5, y+5) #rightToleft
        r = lambda x: self.get_text(page, x+30, y, x+50, y+5)
        sr = lambda x: self.new_rect(x+25, y, x+5, y+5)
        is_valid = re.compile('^\s*(?P<mag>\d\.\d)\s+$')
        ref_valid = re.compile('^\w*\s*(?P<ref>\w)\s+$')
        mags = {}
        for x in xs:
            m = is_valid.match(n(x))
            mr = ref_valid.match(r(x))
            if m and mr:
                if self.is_magnitude_in_right_row(m.group('mag'), page, sr(x), page_height):
                    mags[getType(x)] = {'ref':mr.group('ref'),
                                        'mag':float(m.group('mag'))}
        mag_type = self.select_best_magnitude(mags)
        return {'magnitude':mags[mag_type]['mag'],
                'ref':mags[mag_type]['ref'],
                'type':mag_type}
    def select_best_magnitude(self, mags):
        #mags: {'Mw':{mag:3, ref:N}, 'Ml':{mag:3.1, ref:R}}
        refs = {'N':[], 'R':[]}
        #type priority Mw > Ml > Md > Mb > Ms
        def select_best_type(types):
            for mag_type in ['Mw', 'Ml', 'Md', 'Mb', 'Ms']:
                if mag_type in types:
                    return mag_type
        #ref priority N > R
        for mag in mags:
            refs[mags[mag]['ref']].append(mag)

        if len(refs['N']) == 1:
            return refs['N'][0]
        elif len(refs['N']) == 0:
            if len(refs['R']) == 1:
                return refs['R'][0]
            else:
                return select_best_type(refs['R'])
        else:
            return select_best_type(refs['N'])
    def parse_data(self):
        if self.data:
            return self.data
        pages = (self.doc.get_page(x) for x in range(self.startpage-1,
                                                     self.endpage))
        ys = range(170, 570, 20)
        old_no = 0
        for page in pages:
            page_height = page.get_size()[1]
            for y in ys:
                no = self.get_id(page, y)
                if no and no != old_no:
                    coor = self.get_coor(page, y)
                    depth = self.get_depth(page, y)
                    mag = self.get_magnitude(page, y, page_height)
                    self.data.append({'id': no,
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
            print "%4d %s %.2f %.2f %2d %.1f (%s)" % (quake['id'],
                                                      quake['date'],
                                                      quake['latitude'],
                                                      quake['longtitude'],
                                                      quake['depth'],
                                                      quake['magnitude'],
                                                      quake['mag_type'])

