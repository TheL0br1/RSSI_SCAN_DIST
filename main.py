import SCAN as rssi
import locale


def main():
    rssi_scanner = rssi.RSSI_Scan("wlanapi")
    ap_info1 = rssi_scanner.getRawNetworkScan(sudo=True)
    decoded_string = ap_info1['output'].decode('cp866')
    print(decoded_string)
    localizer = rssi.RSSI_Localizer
    ap_info = rssi_scanner.getAPinfo(sudo=True)
    rssi_values = [ap['signal']/2-100 for ap in ap_info]
    print(rssi_values)

  # print(position)

    print(ap_info)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
