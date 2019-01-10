'''
Created on 06.07.2015

@author: jrenken
'''

import datetime
from nmea import NmeaRecord
from parser import Parser


class PsonlldParser(Parser):
    '''
    Parser for the PSONLLD sentences provided by Sonardyne USBL system Ranger2
    $PSONLLD,153005.253,24,A,50.02495,8.873323,425.3,,,,,,,,*3e<CR><LF>
    Ships heading is only provided by the PSONALL sentence  ----v.
    $PSONALL,Ship 1,CRP,134446.175,650879.00,5688874.16,0.00,180.00,,G,0.00,0.00,,0.109,0.001*51
    '''

    def __init__(self):
        '''
        constructor only calls the parents class constructor
        '''
        super(PsonlldParser, self).__init__()

    def parse(self, data):
        if data.startswith('$PSONLLD'):
            nmea = NmeaRecord(data)
            if (nmea.valid):
                try:
                    if nmea[3] == 'V':
                        return {}
                    result = {'id': nmea[2], 'lat': nmea.value(4),
                              'lon': nmea.value(5), 'depth': nmea.value(6)}
                    t = datetime.datetime.utcnow()
                    try:
                        dt = datetime.datetime(t.year, t.month, t.day,
                                        int(nmea[1][0:2]), int(nmea[1][2:4]),
                                        int(nmea[1][4:6]), int(nmea[1][7:]) * 100)
                    except ValueError:
                        dt = t
                    td = dt - datetime.datetime(1970, 1, 1)
                    result['time'] = td.total_seconds()
                    return dict((k, v) for k, v in result.iteritems() if v is not None)
                except ValueError:
                    return {}
        elif data.startswith('$PSONALL'):
            nmea = NmeaRecord(data)
            if (nmea.valid):
                try:
                    heading = nmea.value(7)
                    if heading:
                        result = {'id': nmea[1], 'heading': nmea.value(7)}
                        return result
                    else:
                        return {}
                except ValueError:
                    return {}

