# Copyright (c) 2011, Mark Chenoweth
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions
#   and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of
#   conditions and the following disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import urllib, datetime
from urllib import request
from datetime import date, timedelta

class Quote(object):

    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%H:%M:%S'

    def __init__(self):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = (
            [] for _ in range(7)
        )

    def append(self, dt, open_, high, low, close, volume):
        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(float(open_))
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self.volume.append(int(volume))

    def to_csv(self):
        return ''.join(
            ["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(
                self.symbol, self.date[row].strftime('%Y-%m-%d'),
                self.time[row].strftime('%H:%M:%S'),
                self.open_[row], self.high[row], self.low[row],
                self.close[row], self.volume[row])
             for row in iter(range(len(self.close)))])

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_csv())

    def read_csv(self, filename):
        self.symbol = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = (
            [] for _ in range(7))
        for line in open(filename, 'r'):
            symbol, ds, ts, open_, high, low, close, volume = line.rstrip().split(',')
            self.symbol = symbol
            dt = datetime.datetime.strptime(ds+' '+ts, self.DATE_FMT+' '+self.TIME_FMT)
            self.append(dt, open_, high, low, close, volume)
        return True

    def __repr__(self):
        return self.to_csv()

class GoogleQuote(Quote):
    ''' Daily quotes from Google. Date format='yyyy-mm-dd' '''
    def __init__(self, symbol, start_date=(date.today() - timedelta(weeks=26)).isoformat(),
                 end_date=date.today().isoformat()):
        super(GoogleQuote, self).__init__()
        self.symbol = symbol.upper()
        start = datetime.date(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
        end = datetime.date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
        url_string = "http://www.google.com/finance/historical?q={0}".format(self.symbol)
        url_string += "&startdate={0}&enddate={1}&output=csv".format(
            start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        csv = urllib.request.urlopen(url_string).readlines()
        csv.reverse()
        for row in iter(range(0, len(csv)-1)):
            ds, open_, high, low, close, volume = csv[row].rstrip().decode().split(',')
            open_, high, low, close = [float(x) for x in [open_, high, low, close]]
            dt = datetime.datetime.strptime(ds, '%d-%b-%y')
            self.append(dt, open_, high, low, close, volume)

if __name__ == '__main__':
    q = GoogleQuote('yhoo')                           # download most recent 6m of YHOO data
    print (q)
    q = GoogleQuote('aapl','2017-01-01')              # download Apple data since 01 Jan 2017
    print (q)                                         # print it out
    q = GoogleQuote('orcl','2017-01-01','2017-11-30') # download Oracle data between 2 dates
    q.write_csv('orcl.csv')                           # save it to disk
    q = Quote()                                       # create a generic quote object
    q.read_csv('orcl.csv')                            # populate it with our previously saved data
    print (q)                                         # print it out
  


