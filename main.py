import time

import matplotlib.pyplot as plt
from win32wifi import Win32Wifi as ww

import SCAN as rssi
from config import accessPoints
from firebase import *

fig, ax = plt.subplots()
accessPoints_s = sorted(accessPoints, key=lambda x: (x['ssid']))


def refresh_data():
    interfaces = ww.getWirelessInterfaces()
    # print("WLAN Interfaces: {:d}".format(len(interfaces)))
    handle = ww.WlanOpenHandle()
    for idx, interface in enumerate(interfaces):
        #  print(
        #     "\n  {:d}\n  GUID: [{:s}]\n  Description: [{:s}]".format(idx, interface.guid_string, interface.description))
        try:
            scan_result = ww.WlanScan(handle, interface.guid)
        except:
            #     print(sys.exc_info())
            continue
    # print("\n  Scan result: {:d}".format(scan_result))
    ww.WlanCloseHandle(handle)

def calculate_position():
    i = 0
    rssi_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    connect_to_RTDB()
    ssids = get_modules_id("9707274")
    model_id = get_model_id("9707274")
    boundaries = get_boundaries("9707274")
    while True:
        i += 1
        refresh_data()
        rssi_scanner = rssi.RSSI_Scan("wlanapi")
        # ap_info1 = rssi_scanner.getRawNetworkScan(sudo=True)
        # decoded_string = ap_info1['output'].decode('cp866')
        # print(decoded_string)
        localizer = rssi.RSSI_Localizer(accessPoints=accessPoints_s)
        ap_info = rssi_scanner.getAPinfo(networks=ssids, sudo=True)
        ap_info = sorted(ap_info, key=lambda x: (x['ssid']))
        rssi_values = [sum(pair) for pair in zip(rssi_values, [ap['signal'] / 2 - 100 for ap in ap_info])]
        print(ap_info)
        if len(rssi_values) >= 3 and i >= 10:
            rssi_values = [x / (i) for x in rssi_values]
            print(rssi_values)

            i = 0
            pos = localizer.getNodePosition(rssi_values)
            if pos[0] < boundaries['min']['x']:
                pos[0] = 0
            if pos[0] > boundaries['max']['x']:
                pos[0] = 14
            if pos[1] > boundaries['max']['y']:
                pos[1] = 1.5
            if pos[1] < boundaries['min']['y']:
                pos[1] = 0
            write_position("modelWorkers/"+model_id+"/gena/coordinates", pos[0], pos[1])

            rssi_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        time.sleep(0.40)


def main():
    calculate_position()
main()
