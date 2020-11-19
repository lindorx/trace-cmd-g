'''
from ctypes import *

fields_list=[('num',c_short),('magic_number',c_char*15),
('header_page',c_char*11),('header_page_size',c_int)
	                 ]

class TestStruct(Structure):
	_fields_ = fields_list

with open('/home/lindorx/lgit/trace-cmd-g/test/test.dat','rb') as fin:
    data_size=sizeof(TestStruct)
    data=fin.read(data_size)
    print("data_size="+str(data_size))
    ttf1=TestStruct(data)

    print(ttf1.num)
'''

from trace_dat import *

tt1=trace_dat("./test/test.dat")
print(tt1.test())