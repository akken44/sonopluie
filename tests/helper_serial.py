class SerialException(Exception):
    '''
    Base class for serial port related exceptions.
    '''
    pass


class MockSerial(object):
    have_gps_data = True
    data = '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47'.encode('utf8')

    def __init__(self, *args, **kwargs):
        pass

    def readline(self):
        if self.have_gps_data:
            return (self.data)
        else:
            error = SerialException()
            raise error
