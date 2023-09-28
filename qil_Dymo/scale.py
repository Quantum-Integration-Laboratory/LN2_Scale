import usb.core
import usb.util

import math

#Our scale seems to increment these by one
DATA_MODE_KILOGRAMS = 3
DATA_MODE_OUNCES = 12

VENDOR_ID  = 0x0922#Dymo Vendor ID
PRODUCT_ID = 0x8009# Product Code

class USB(object):

    def __init__(self, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        
        #find the device
        self.device = usb.core.find(idVendor=vendor_id,
                                    idProduct=product_id)
        #check that the device connected
        if self.device is None:
            raise ValueError('Our device is not connected')
        
        #Setup
        self.device.set_configuration()
        self.endpoint = self.device[0][(0,0)][0]
    
    def __del__(self):
        self.device.reset()

    def get_weight(self,attempts = 10):
        data = None
        grams = 0
        while data is None and attempts > 0:
            try:
                data = self.device.read(self.endpoint.bEndpointAddress,
                                        self.endpoint.wMaxPacketSize)
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    attempts -= 1
                    continue
        #check for error returns
        if data==None:
            return "Connection Error"
        elif data[1] in [1,6,7,8]:
            if data[1] ==1:
                return "Fault"
            elif data[1]==6:
                return "Overweight"
            elif data[1]==7:
                return "Calibrate"
            elif data[1]==8:
                return "Re-Zero"
                

        weight = None
        raw_weight = data[4] + data[5] * 256

        if data[2] == DATA_MODE_OUNCES:
            scaling_factor = math.pow(10, (data[3] - 256))
            ounces = raw_weight * scaling_factor
            weight = ounces
        elif data[2] == DATA_MODE_KILOGRAMS:
            scaling_factor = math.pow(10, (data[3]^-256))
            grams = raw_weight*scaling_factor
            weight = grams

        if data[1] == 5:
            weight = weight * -1

        return weight
