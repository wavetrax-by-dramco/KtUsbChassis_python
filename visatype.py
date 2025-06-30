# -*- coding: utf-8 -*-
import ctypes
ViChar = ctypes.c_char
ViInt8 = ctypes.c_int8
ViInt16 = ctypes.c_int16
ViUInt16 = ctypes.c_uint16
ViInt32 = ctypes.c_int32
ViUInt32 = ctypes.c_uint32
ViInt64 = ctypes.c_int64
ViString = ctypes.c_char_p
ViReal32 = ctypes.c_float
ViReal64 = ctypes.c_double
# Types that are based on other visatypes
ViBoolean = ViUInt16
VI_TRUE = ViBoolean(True)
VI_FALSE = ViBoolean(False)
ViStatus = ViInt32
13
ViSession = ViUInt32
ViAttr = ViUInt32
ViConstString = ViString
ViRsrc = ViString