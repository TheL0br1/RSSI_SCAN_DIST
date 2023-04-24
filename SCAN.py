import subprocess
import numpy



class RSSI_Scan(object):
    def __init__(self, interface):
        self.interface = interface

    def getRawNetworkScan(self, sudo=False):
        if sudo:
            scan_command = ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid']
        else:
            scan_command = ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid']
        scan_process = subprocess.Popen(scan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (raw_output, raw_error) = scan_process.communicate()
        scan_process.wait()
        return {'output': raw_output, 'error': raw_error}

    @staticmethod
    def getSSID(raw_cell):
        ssid = raw_cell.split('SSID')[1]
        ssid = ssid.split(':')[1]
        ssid = ssid.split('\r\n')[0]
        ssid = ssid.strip()
        return ssid

    @staticmethod
    def getQuality(raw_cell):
        quality = raw_cell.split('Signal             : ')[1]
        quality = quality.split('\r\n')[0]
        quality = int(quality.strip('%  '))
        return quality

    @staticmethod
    def getSignalLevel(raw_cell):
        signal = raw_cell.split('Signal             : ')[1]
        signal = signal.split('\r\n')[0]
        signal = int(signal.strip('%  '))
        return signal

    def parseCell(self, raw_cell):
        cell = {
            'ssid': self.getSSID(raw_cell),
            'quality': self.getQuality(raw_cell),
            'signal': self.getSignalLevel(raw_cell)
        }
        return cell

    def formatCells(self, raw_cell_string):
        raw_cell_string = raw_cell_string.decode('cp866')
        raw_cells = raw_cell_string.split('\r\n\r\n')  # Divide raw string into raw cells.
        raw_cells.pop(0)  # Remove unneccesary "Scan Completed" message.
        raw_cells.pop()
        if (len(raw_cells) > 0):  # Continue execution, if atleast one network is detected.
            # Iterate through raw cells for parsing.
            # Array will hold all parsed cells as dictionaries.
            formatted_cells = [self.parseCell(cell) for cell in raw_cells]
            # Return array of dictionaries, containing cells.
            return formatted_cells
        else:
            print("Networks not detected.")
            return False

    @staticmethod
    def filterAccessPoints(all_access_points, network_names):
        focus_points = []  # Array holding the access-points of concern.
        # Iterate through all access-points found.
        for point in all_access_points:
            # Check if current AP is in our desired list.
            if point['ssid'] in network_names:
                focus_points.append(point)
        return focus_points

    def getAPinfo(self, networks=False, sudo=False):
        # Unparsed access-point listing. AccessPoints are strings.
        raw_scan_output = self.getRawNetworkScan(sudo)['output']
        # Parsed access-point listing. Access-points are dictionaries.
        all_access_points = self.formatCells(raw_scan_output)
        # Checks if access-points were found.
        if all_access_points:
            # Checks if specific networks were declared.
            if networks:
                # Return specific access-points found.
                return self.filterAccessPoints(all_access_points, networks)
            else:
                # Return ALL access-points found.
                return all_access_points
        else:
            # No access-points were found.
            return False


class RSSI_Localizer(object):

    def __init__(self, accessPoints):
        self.accessPoints = accessPoints
        self.count = len(accessPoints)

    @staticmethod
    def getDistanceFromAP(accessPoint, signalStrength):
        beta_numerator = float(accessPoint['reference']['signal'] - signalStrength)
        beta_denominator = float(10 * accessPoint['signalAttenuation'])
        beta = beta_numerator / beta_denominator
        distanceFromAP = round(((10 ** beta) * accessPoint['reference']['distance']), 4)
        accessPoint.update({'distance': distanceFromAP})
        return accessPoint


    def getDistancesForAllAPs(self, signalStrengths):
        apNodes = []
        for i in range(len(self.accessPoints)):
            ap = self.accessPoints[i]
            distanceFromAP = self.getDistanceFromAP(
                ap,
                signalStrengths[i]
            )
            apNodes.append({
                'distance': distanceFromAP['distance'],
                'x': ap['location']['x'],
                'y': ap['location']['y']
            })
        return apNodes

    def createMatrices(self, accessPoints):
        # Sets up that te matrics only go as far as 'n-1' rows,
        # with 'n being the # of access points being used.
        n_count = self.count - 1
        # initialize 'A' matrix with 'n-1' ranodm rows.
        a = numpy.empty((n_count, 2))
        # initialize 'B' matrix with 'n-1' ranodm rows.
        b = numpy.empty((n_count, 1))
        # Define 'x(n)' (x of last accesspoint)
        x_n = accessPoints[n_count]['x']
        # Define 'y(n)' (y of last accesspoint)
        y_n = accessPoints[n_count]['y']
        # Define 'd(n)' (distance from of last accesspoint)
        d_n = accessPoints[n_count]['distance']
        # Iteration through accesspoints is done upto 'n-1' only
        for i in range(n_count):
            ap = accessPoints[i]
            x, y, d = ap['x'], ap['y'], ap['distance']
            a[i] = [2 * (x - x_n), 2 * (y - y_n)]
            b[i] = [(x ** 2) + (y ** 2) - (x_n ** 2) - (y_n ** 2) - (d ** 2) + (d_n ** 2)]
        return a, b

    @staticmethod
    def computePosition(a, b):
        # Get 'A_transposed' matrix
        at = numpy.transpose(a)
        # Get 'A_transposed*A' matrix
        at_a = numpy.matmul(at, a)
        # Get '[(A_transposed*A)^-1]' matrix
        inv_at_a = numpy.linalg.inv(at_a)
        # Get '[A_transposed*B]'
        at_b = numpy.matmul(at, b)
        # Get '[(A_transposed*A)^-1]*[A_transposed*B]'
        # This holds our position (xn,yn)
        x = numpy.matmul(inv_at_a, at_b)
        return x

    def getNodePosition(self, signalStrengths):
        apNodes = self.getDistancesForAllAPs(signalStrengths)
        print(apNodes)
        #return
        a, b = self.createMatrices(apNodes)
       # print(a)
       # print(b)
        position = self.computePosition(a, b)
        # print(a)
        # print(b)
        return position


