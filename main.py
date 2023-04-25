import time
import matplotlib.pyplot as plt

from win32wifi import Win32Wifi as ww

import SCAN as rssi
from config import accessPoints


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

def draw(pos):


    # Создаем полотно и оси координат
    # Рисуем точки
    plt.cla()

    for x in accessPoints_s:
        circle = plt.Circle((x['location']['x'], x['location']['y']), x['distance'], color='blue', fill = False)
        ax.add_artist(circle)
    ax.scatter(pos[0], pos[1])
    ax.scatter([6,6,0,0],[0,4,0,4])
    # Добавляем подписи осей
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_xlim([-10, 12])
    ax.set_ylim([-6, 8])

    # Добавляем заголовок
    ax.set_title('Координаты точек')

    # Показываем график
    plt.show(block=False)
    plt.pause(0.01)


def main():
    i = 0
    rssi_values = [0,0,0,0,0,0,0,0,0,0,0]

    while True:
        i+=1
        refresh_data()
        rssi_scanner = rssi.RSSI_Scan("wlanapi")
        ssids = ["rssid_test2", "rssid_test", "rssid_test3", "rssid_test4"]
        # ap_info1 = rssi_scanner.getRawNetworkScan(sudo=True)
        # decoded_string = ap_info1['output'].decode('cp866')
        # print(decoded_string)
        localizer = rssi.RSSI_Localizer(accessPoints=accessPoints_s)
        ap_info = rssi_scanner.getAPinfo(networks=ssids, sudo=True)
        ap_info = sorted(ap_info, key=lambda x: (x['ssid']))
        rssi_values = [sum(pair) for pair in zip(rssi_values, [ap['signal'] / 2 - 100 for ap in ap_info])]
        print(ap_info)
        if len(rssi_values) >= 3 and i>=10:
            rssi_values = [x/(i) for x in rssi_values]
            print(rssi_values)

            i=0
            draw(localizer.getNodePosition(rssi_values))
            rssi_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        time.sleep(0.50)





if __name__ == '__main__':
    main()

