#!/usr/local/bin/python2
# -*- coding: utf-8 -*-
import re
import mechanize
from bs4 import BeautifulSoup
import calendar
import json
import os
from datetime import datetime, timedelta
import sys

begin = 2015
end = 2015

now = datetime.now()


URL = 'http://fhy.wra.gov.tw/ReservoirPage_2011/StorageCapacity.aspx'
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

""" Get days of every month """
for reservior in {'主要水庫', '所有水庫', '水庫及攔河堰'}:
    for year in range(begin, end + 1):
        for month in range(1, 13):
            days = calendar.monthrange(year, month)[1]

            for day in range(1, days + 1):
                """ initialize list and dictionary """
                info = []
                content = {}

                """ it will delay 1~2 days for data update, so will fetch (now - 2) days """
                if datetime(year, month, day) > now - timedelta(days=2):
                    print "date upate to", year, month, (day - 1)
                    #sys.exit(0)
                    continue
                

                """ Create folder and file for storing data """
                c_path = os.getcwd()
                directory = c_path + '/' + reservior + '/' + str(year)
                if not os.path.exists(directory):
                    print "create directory"
                    os.makedirs(directory)
                filename = str(month) + '-' + str(day) + '.json'
                
                """ skip file if it exist """
                if os.path.isfile(directory + '/' + filename):
                    print "skip ", str(year), str(month), str(day)
                    continue

                f = open(directory + '/' + filename, 'w')

                """ Generate data for post form """
                r = br.open(URL)
                br.select_form(nr=0)
                #print br.form

                br['ctl00$cphMain$cboSearch'] = [str(reservior)]
                br['ctl00$cphMain$ucDate$cboYear'] = [str(year)]
                br['ctl00$cphMain$ucDate$cboMonth'] = [str(month)]
                br['ctl00$cphMain$ucDate$cboDay'] = [str(day)]

                br.set_all_readonly(False)
                br['__EVENTTARGET'] = 'ctl00$cphMain$btnQuery'


                #br.find_control("btnQuery").disabled = True

                response = br.submit()
                page =  br.response().get_data()
                
                """ clear history data of mechanize to release memory""" 
                r.close()
                br.clear_history()

                """ Read response """
                soup = BeautifulSoup(page)
                #print soup.prettify()
                
                print reservior
                print year, month, day

                """ Parse necessary data """
                for element in soup.find(id='frame').tr.next_siblings:
                    
                    if element:
                        element = str(element).replace('\r', '')

                    m = re.match(r'(<tr>|<tr class="alternate">)\s*<td>(.*)</td><td align="right">(.*)</td><td>\s*(.*)<br/>\s*(.*)\s*</td><td align="right">(.*)</td><td align="right">(.*)</td><td align="right">(.*)</td><td align="right">(.*)</td><td>(.*)</td><td>(.*)</td><td align="right">(.*)</td><td align="right">(.*)</td><td align="right">(.*)</td>', str(element), re.M)

                    if m:
                        #print m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8), m.group(9), m.group(10), m.group(11), m.group(12), m.group(13), m.group(14)
                        content = {
                            "name": m.group(2),
                            "daily": 
                                {
                                "capacity": m.group(3),
                                "start_time": m.group(4),
                                "end_time": m.group(5),
                                "rain": m.group(6),
                                "in_water": m.group(7),
                                "out_water": m.group(8),
                                "diff": m.group(9),
                                "nuclear": m.group(10),
                                },
                            "in_time": 
                                {
                                "time": m.group(11),
                                "height": m.group(12),
                                "capacity": m.group(13),
                                "now_cap_percent": m.group(14),
                                }
                            }
                        info.append(content)

                f.write(json.dumps(info, ensure_ascii=False))
                f.close()



