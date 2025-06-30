#  ____  ____      _    __  __  ____ ___
# |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
# | | | | |_) |  / _ \ | |\/| | |  | | | |
# | |_| |  _ <  / ___ \| |  | | |__| |_| |
# |____/|_| \_\/_/   \_\_|  |_|\____\___/
#                           research group
#                             dramco.be/
#
#  KU Leuven - Technology Campus Gent,
#  Gebroeders De Smetstraat 1,
#  B-9000 Gent, Belgium
#
#         File: main.ext
#      Created: 2025-06-30
#       Author: Jarne Van Mulders
#      Version: 0.1
#
#  Description: Communicate with chassis Keysight P5024A VNA
#               Read attributes and sensor data


import ctypes
from visatype import *

KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_PREFIX           = 1050302
KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_REVISION         = 1050551
KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_VENDOR           = 1050513
KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_DESCRIPTION      = 1050514
KTPUSBCHASSIS_ATTR_INSTRUMENT_MODEL                 = 1050512
KTPUSBCHASSIS_ATTR_INSTRUMENT_FIRMWARE_REVISION     = 1050510
KTPUSBCHASSIS_ATTR_SYSTEM_SERIAL_NUMBER             = 1150003
KTPUSBCHASSIS_ATTR_SIMULATE                         = 1050005
KTPUSBCHASSIS_ATTR_FW_UP_TO_DATE                    = 1150021

KTPUSBCHASSIS_ATTR_FAN_COUNT                        = 1150010
KTPUSBCHASSIS_ATTR_FAN_RPM                          = 1150013
KTPUSBCHASSIS_ATTR_FAN_ALARM_OCCURRED               = 1150011

KTPUSBCHASSIS_ATTR_TEMPERATURE_SENSOR_COUNT         = 1150017
KTPUSBCHASSIS_ATTR_TEMPERATURE                      = 1150018

KTPUSBCHASSIS_ATTR_VOLTAGE_RAIL_COUNT               = 1150022
KTPUSBCHASSIS_ATTR_VOLTAGE                          = 1150024

# Load the DLL
tkDLL = ctypes.cdll.LoadLibrary(r"C:\Program Files\IVI Foundation\IVI\Bin\KtPUsbChassis_64.dll")

# Typedefs
tkDLL.KtPUsbChassis_InitWithOptions.argtypes = [ctypes.c_char_p, ViBoolean, ViBoolean, ctypes.c_char_p, ctypes.POINTER(ViSession)]
tkDLL.KtPUsbChassis_InitWithOptions.restype = ViStatus

# Initialisation param
resourceName = ctypes.create_string_buffer(b'PXI10::4C0BC2E482DCC7E0::INSTR')
optionString = ctypes.create_string_buffer(b'Simulate=0,RangeCheck=1,QueryInstrStatus=1,Cache=1')
session = ViSession()

# Init call
status = tkDLL.KtPUsbChassis_InitWithOptions(resourceName, VI_TRUE, VI_TRUE, optionString, ctypes.byref(session))

if status != 0:
    print(f"Init mislukt met statuscode: {status}")
    exit(1)

print(status)

# String attribuut reader
def get_attr_string(attribute_id):
    buffer = (ViChar * 128)()
    status = tkDLL.KtPUsbChassis_GetAttributeViString(session, b"", attribute_id, 128, buffer)
    assert status == 0, f"Fout bij ophalen attribuut {attribute_id}: {status}"
    return buffer.value.decode()

# Boolean attribuut reader
def get_attr_boolean(attribute_id):
    result = ViBoolean()
    status = tkDLL.KtPUsbChassis_GetAttributeViBoolean(session, b"", attribute_id, ctypes.byref(result))
    assert status == 0, f"Fout bij ophalen boolean attribuut {attribute_id}: {status}"
    return result.value == VI_TRUE

# Read and output a few attributes
print(f"DRIVER_PREFIX:       {get_attr_string(KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_PREFIX)}")
print(f"DRIVER_REVISION:     {get_attr_string(KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_REVISION)}")
print(f"DRIVER_VENDOR:       {get_attr_string(KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_VENDOR)}")
print(f"DRIVER_DESCRIPTION:  {get_attr_string(KTPUSBCHASSIS_ATTR_SPECIFIC_DRIVER_DESCRIPTION)}")
print(f"INSTRUMENT_MODEL:    {get_attr_string(KTPUSBCHASSIS_ATTR_INSTRUMENT_MODEL)}")
print(f"FIRMWARE_REVISION:   {get_attr_string(KTPUSBCHASSIS_ATTR_INSTRUMENT_FIRMWARE_REVISION)}")
print(f"SERIAL_NUMBER:       {get_attr_string(KTPUSBCHASSIS_ATTR_SYSTEM_SERIAL_NUMBER)}")
print(f"SIMULATE:            {'True' if get_attr_boolean(KTPUSBCHASSIS_ATTR_SIMULATE) else 'False'}")

# Firmware up-to-date?
is_fw_up_to_date = get_attr_boolean(KTPUSBCHASSIS_ATTR_FW_UP_TO_DATE)
print("Firmware Status:     Chassis firmware is up-to-date" if is_fw_up_to_date else "Firmware Status:     Please update chassis firmware.")

# Get number of fans
numFans = ViInt32()
status = tkDLL.KtPUsbChassis_GetAttributeViInt32(session, None, KTPUSBCHASSIS_ATTR_FAN_COUNT, ctypes.byref(numFans))
assert status == 0, f"Fout bij ophalen fan count: {status}"

print("Chassis Fans:")
for i in range(1, numFans.value + 1):
    fanName = (ViChar * 1024)()
    fanRPM = ViReal64()

    status = tkDLL.KtPUsbChassis_GetFanName(session, ViInt32(i), 1024, fanName)
    assert status == 0, f"Fout bij ophalen fan naam: {status}"

    status = tkDLL.KtPUsbChassis_GetAttributeViReal64(session, fanName, KTPUSBCHASSIS_ATTR_FAN_RPM, ctypes.byref(fanRPM))
    assert status == 0, f"Fout bij ophalen fan RPM: {status}"

    print(f"{i}: {fanName.value.decode()} - {fanRPM.value:.2f} RPM")


# Read temperature sensors
num_sensors = ViInt32()
status = tkDLL.KtPUsbChassis_GetAttributeViInt32(session, None, 1150017, ctypes.byref(num_sensors))  # 1150002 = KTPUSBCHASSIS_ATTR_TEMPERATURE_SENSOR_COUNT
assert status == 0, f"Fout bij ophalen sensor count: {status}"

print("Temperature sensors:")
for i in range(1, num_sensors.value + 1):
    # Get sensor name
    sensor_name_buf = ctypes.create_string_buffer(1024)
    status = tkDLL.KtPUsbChassis_GetTemperatureSensorName(session, ViInt32(i), 1024, sensor_name_buf)
    assert status == 0, f"Fout bij ophalen sensor naam {i}: {status}"

    # Read temperature
    temperature = ViReal64()
    status = tkDLL.KtPUsbChassis_GetAttributeViReal64(session, sensor_name_buf, 1150018, ctypes.byref(temperature))  # 1150003 = KTPUSBCHASSIS_ATTR_TEMPERATURE
    assert status == 0, f"Fout bij uitlezen temperatuur sensor {i}: {status}"

    print(f"{i}: {sensor_name_buf.value.decode()} {temperature.value:.2f} °C")


# Read voltage rails
numVoltageRails = ViInt32()
status = tkDLL.KtPUsbChassis_GetAttributeViInt32(session, None, KTPUSBCHASSIS_ATTR_VOLTAGE_RAIL_COUNT, ctypes.byref(numVoltageRails))
assert status == 0, f"Fout bij ophalen voltage rail count: {status}"

print(f"Number of Voltage Rails: {numVoltageRails.value}")

for i in range(1, numVoltageRails.value + 1):
    voltageRailName = (ViChar * 1024)()
    voltage = ViReal64()

    status = tkDLL.KtPUsbChassis_GetVoltageRailName(session, ViInt32(i), 1024, voltageRailName)
    assert status == 0, f"Fout bij naam voltage rail {i}: {status}"

    status = tkDLL.KtPUsbChassis_GetAttributeViReal64(session, voltageRailName, KTPUSBCHASSIS_ATTR_VOLTAGE, ctypes.byref(voltage))
    assert status == 0, f"Fout bij uitlezen voltage rail {i}: {status}"

    print(f"{i}: {voltageRailName.value.decode()} - {voltage.value:.3f} V")