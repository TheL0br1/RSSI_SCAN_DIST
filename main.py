import SCAN as rssi
import locale
import time
from config import accessPoints


def main():
    while True:
        rssi_scanner = rssi.RSSI_Scan("wlanapi")
        ssids = ["rssid_test3", "rssid_test2", "rssid_test"]
        ap_info1 = rssi_scanner.getRawNetworkScan(sudo=True)
        decoded_string = ap_info1['output'].decode('cp866')
        # print(decoded_string)
        localizer = rssi.RSSI_Localizer(accessPoints=accessPoints)
        ap_info = rssi_scanner.getAPinfo(networks=ssids, sudo=True)
        rssi_values = [ap['signal'] / 2 - 100 for ap in ap_info]
        if len(rssi_values) >= 3:
            print(ap_info)
            print(rssi_values)
            print(localizer.getNodePosition(rssi_values))
        time.sleep(3)


# print(position)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
