import googlesheet
import uuid
from miflora.miflora_poller import MiFloraPoller
import btlewrap
import bluepy.btle
from datetime import datetime

# we import bluepy.btlem to trap errorrs like this one:
# bluepy.btle.BTLEDisconnectError: Failed to connect to peripheral C4:7C:8D:63:EE:6B, addr type: public

backend = btlewrap.bluepy.BluepyBackend

# set variables:
debug = False  # unset this to see all errors
# spreadsheet/file name (individual sheet names set below)
google_spreadsheet = 'YardMonitor'
# define local file that has API key
apifile = 'client_secret.json'

#define local scope for goole API
google_scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# get device mac
formatted_mac = ':'.join([
    '{:02x}'.format((uuid.getnode() >> ele) & 0xff)
    for ele in range(0, 8 * 6, 8)
][::-1])

# we're running the same code on all pi's, get our current device
if formatted_mac == 'b8:27:eb:c9:3a:99':
    hostname = 'HousePi-A'
elif formatted_mac == 'b8:27:eb:05:ce:61':
    hostname = 'GaragePi'

# dict of our sensors with BLE MACs
sensors = {
    'Backyard1': 'C4:7C:8D:63:D4:A1',
    'Backyard2': 'C4:7C:8D:63:ED:DA',
    'Backyard3': 'C4:7C:8D:63:EE:6B',
    'Frontyard1': 'C4:7C:8D:63:F5:29'
}

# function that returns dict of Pi name, sensor name, timestamp, sensor data
def yard_poller(pi_name, sensor_name, sensor_mac):
    poller_dict = {}
    datetime_obj = datetime.now()
    timestamp = datetime_obj.strftime("%d-%b-%Y %H:%M:%S")
    poller = MiFloraPoller(sensor_mac, backend, cache_timeout=300, retries=0)

    # trapped failed connections - BLE can be finicky.
    if debug is False:
        try:
            batt_level = poller.battery_level()
            temp = poller.parameter_value('temperature')
            temp_f = (temp * 9 / 5) + 32
            brightness = poller.parameter_value('light')
            soil_health = poller.parameter_value('conductivity')
            soil_moisture = poller.parameter_value('moisture')
            failed_cx = False

        except btlewrap.base.BluetoothBackendException as e:
            batt_level = 'Failed Cx'
            temp_f = 'Failed Cx'
            soil_moisture = 'Failed Cx'
            brightness = 'Failed Cx'
            soil_health = 'Failed Cx'
            failed_cx = True
            pass

    poller_dict.update({'TimeStamp': timestamp})
    poller_dict.update({'PiName': pi_name})
    poller_dict.update({'SensorName': sensor_name})
    poller_dict.update({'Battery': batt_level})
    poller_dict.update({'Temp': temp_f})
    poller_dict.update({'Moisture': soil_moisture})
    poller_dict.update({'Light': brightness})
    poller_dict.update({'Conductivity': soil_health})
    if failed_cx is not True:
        poller.clear_history()
    else:
        pass
    return poller_dict


# through testing, each pi can only reach certain sensors
# I had 2 Pis but you can always use an MQTT gateway instead of 2 Pis
# I'm just calling them based upon range of pi to the specific sensor
# not very advanced but it works
def main():
    if hostname == 'GaragePi':
        # make our cx to each device using yard_poller function, you may have to do some testing regarding distance
        backyard_sensor1 = yard_poller(hostname, 'BackYard1',
                                       sensors['Backyard1'])
        googlesheet.write_data(
            secretfile=apifile,
            scopes=google_scope,
            filename=google_spreadsheet,
            worksheetname='Backyard1',
            sensordata=backyard_sensor1)

        backyard_sensor2 = yard_poller(hostname, 'Backyard2',
                                       sensors['Backyard2'])
        googlesheet.write_data(
            secretfile=apifile,
            scopes=google_scope,
            filename=google_spreadsheet,
            worksheetname='Backyard2',
            sensordata=backyard_sensor2)

    elif hostname == 'HousePi-A':
        backyard_sensor1 = yard_poller(hostname, 'BackYard1',
                                       sensors['Backyard1'])
        googlesheet.write_data(
            secretfile=apifile,
            scopes=google_scope,
            filename=google_spreadsheet,
            worksheetname='Backyard1',
            sensordata=backyard_sensor1)

        backyard_sensor2 = yard_poller(hostname, 'Backyard2',
                                       sensors['Backyard2'])
        googlesheet.write_data(
            secretfile=apifile,
            scopes=google_scope,
            filename=google_spreadsheet,
            worksheetname='Backyard2',
            sensordata=backyard_sensor2)

        backyard_sensor3 = yard_poller(hostname, 'BackYard3',
                                       sensors['Backyard3'])
        googlesheet.write_data(
            secretfile=apifile,
            scopes=google_scope,
            filename=google_spreadsheet,
            worksheetname='Backyard3',
            sensordata=backyard_sensor3)

if __name__ == "__main__":
    main()