class SerialException(Exception):
    '''
    Base class for serial port related exceptions.
    '''
    pass


class MockSerial(object):
    have_gps_data = True
    lat = 4807.038
    lat_dir = 'N'
    lon = 01131.000
    lon_dir = 'E'

    def __init__(self, *args, **kwargs):
        pass

    def readline(self):
        if self.have_gps_data:
            return ('$GPGGA,123519,{lat},{lat_dir},{lon},{lon_dir},1,08,0.9,'
                    '545.4,M,46.9,M,,*47'.format(lat=self.lat,
                                                 lat_dir=self.lat_dir,
                                                 lon=self.lon,
                                                 lon_dir=self.lon_dir,
                                                 )
                    .encode('utf8'))
        else:
            error = SerialException()
            raise error
