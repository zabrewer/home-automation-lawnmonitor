# BLE LawnPoller
### Monitoring Home Lawn Health with Xiaomi "Mi Flora" Plant Monitor Sensor and a Raspberry Pi Over BlueTooth Low Energy (BLE)
-----------------  

<img src="assets/in_ground1.png" width="100">
<img src="assets/outside1.png" width="100">
<img src="assets/on_counter1.png" width="100">
<img src="assets/wide_inground1.png" width="100">

- [Introduction](#Purpose/About)
- [About the Xiaomi "Mi Flora" Plant Monitor Sensor](#About-the-Xiaomi-"Mi-Flora"-Plant-Monitor-Sensor)
  - ["Mi Flora" Plant Monitor: Battery Life](#"Mi-Flora"-Plant-Monitor:-Battery-Life)
  - ["Mi Flora" Plant Monitor: Data Measured by the Sensor](#"Mi-Flora"-Plant-Monitor:-Data-Measured-by-the-Sensor)
- [Purchasing a Sensor](#Purchasing-a-Sensor)
- [Choosing a Device to Connect to the Sensor](#Choosing-a-Device-to-Connect-to-the-Sensor)
  - [Choosing a Device to Connect to the Sensor: Raspberry Pi Considerations](#Choosing-a-Device-to-Connect-to-the-Sensor:-Raspberry-Pi-Considerations)
- [Understanding Distance Limitations](#Understanding-Distance-Limitations)
- [Upgrade Sensor Firmware to 3.1.9: Overview](#Upgrade-Sensor-Firmware-to-3.1.9:-Overview)
  - [Upgrade Sensor Firmware to 3.1.9: Tips for Success Before You Begin](#Upgrade-Sensor-Firmware-to-3.1.9:-Tips-for-Success-Before-You-Begin)
  - [Upgrade Sensor Firmware to 3.1.9: Detailed Steps](#Upgrade-Sensor-Firmware-to-3.1.9:-Detailed-Steps)
- [Get Sensor BlueTooth MAC Address](#Get-Sensor-BlueTooth-MAC-Address)

## Introduction

In the spring of 2020, I had our home's lawn tilled  up and sod (grass) professionally installed by a landscaper. The project wasn't cheap so I wanted to monitor some basic environmental conditions (especially soil moisture and sunlight) to make sure the grass had the best chance of long term success.  

Somewhere in my research, I read about the Xiaomi plant monitor and had seen integration with HomeAssistant which I was already using. As I was short on time but had several raspberry pi's with Bluetooth Low Energy (BLE) capability, I wrote some basic Python code to poll plant monitors placed around my lawn and post the data to a Google sheet.

I'll eventually add them to HomeAssistant + Graphana/InfluxDB (and perhaps an automated sprinkler system) but I have the data I need for now and alerts on key metrics. 

This repo contains and an overview of the project and related [python code](poller.py) should anyone want to reproduce or use it as a starting point for another project.

[Back To Index](#BLE-LawnMonitor)


## About the Xiaomi "Mi Flora" Plant Monitor Sensor

The Xiaomi "Mi Flora" Plant Monitor is a BLE device that captures basic environmental data for houseplants. It runs on a common CR2032 battery. The batteries (reportedly) last around a year before they have to be replaced but this may vary depending on polling frequency and other considerations. 

### "Mi Flora" Plant Monitor: Battery Life

I cannot verify the accuracy of the battery % yet, I may do so with my multimeter and a resistor in the future. It is worth nothing that after about 2 months of use my sensors are still reporting 99% battery levels with polling each sensor 2x per day.

### "Mi Flora" Plant Monitor: Data Measured by the Sensor

The environmental data measured by the sensor includes:

* Soil Moisture (measured in %) - [Read more about soil moisture here](https://landscapearchitecturemagazine.org/2014/01/21/soils-the-measure-of-moisture-parked/)
* Soil Fertility (μS/cm) -  [Read more about soil fertility here](https://farmagronomy.com.au/the-why-and-how-to-testing-the-electrical-conductivity-of-soils/)
* Light Intensity (measured in lux) - [Read more about light + lux here](https://greeneryunlimited.co/blogs/plant-care/how-to-measure-light-for-plants)
* Air Temp (measured in Celsius)

The basic premise is: You open the app, choose the type of houseplant you have, and the app recommends more light, alerts your phone when it needs water, etc. These devices are actually well-made as noted by others who have conducted detailed teardowns. (See the [references section](#References) below for teardown details, SoC specifications, & more).

It is important to note that these devices they *are not* waterproof (I outlined [waterproofing efforts](#waterproofing) below).

[Back To Index](#BLE-LawnMonitor)

## Purchasing a Sensor

There are at least two versions of the Xiaomi plant monitor sold - from everything I can tell, they are the same other than branding. In online forums you see these referenced as the "International version" and "US version." I believe that most problems reported with the "US version" are due to the 2.7 firmware they ship with and the inability to upgrade the firmware through the US mobile app (I detail how to get past this below). Just to be safe, I started off purchasing a single sensor to make sure everything would work as expected. 

The Plant Monitor sold on Amazon goes under the brand name "Northfifteen" and I purchased it for around $18 US. Other than the branding, the device is identical to the Xiaomi in everything that I have observed (visible board components/SoCs, BLE GATT values, etc).  

The Apple IOS app for Northfifteen looks to be a SDK licensed by Xiaomi, but I had no luck ever getting it to connect to the sensors - the app itself often displayed errors unrelated to connectivity.

The sensors that I purchased all shipped with 2.7 firmware which was problematic even when using BLE scanners/software that I've used on other projects.  I came up with a round about way to get all of the sensors upgrade to the much more stable 3.1.9 firmware which you can [read about below.](#Upgrade-Sensor-Firmware-to-3.1.9)

[Back To Index](#BLE-LawnMonitor)

## Choosing a Device to Connect to the Sensor

I chose to use a Raspberry Pi 3 Model B+ Rev 1.3 and a Raspberry Pi ZeroW because I had on hand from an older project. One is in my garage which has wifi coverage and the other is in a room near 2 more sensors in the back yard.  Between the two devices, I have full access to the 3 backyard sensors (I  have a fourth yet-to-be deployed for the front lawn) but testing is required to make sure you have a consistent BLE connection (see [Testing Connectivity to the Sensors](#Testing-Connectivity-to-the-Sensors) below).

The device(s) you may choose to connect to the sensors will depend entirely on your environmental factors e.g.:

* Access (proximity) to a power source
* Wifi/ethernet
* BLE distance limitations
* Desired sensor placement
* What you want to measure in regards to sensor placement:
  * Light/Luminosity: Is there a shady part of the lawn where you want to measure sunlight to understand if you have the minimum number of hours for necessary for a type of grass or plant? Do you maybe need to have limbs removed from a tree?
  * Water: When to water, low spots that hold water, rainfall, etc.

If distance/connectivity is an environmental limitation, you may have to incorporate another device like an [ESP32](https://en.wikipedia.org/wiki/ESP32) with a BLE chip to get the data back to a data store or 2nd device acting as a message broker.  Intermediate (low power) devices acting as a broker may be necessary to get data to its ultimate destination: e.g. file, MQTT subscriber, google sheets, HomeAssistant (or other home automation solution), database, cloud, etc.

It's outside of the scope of this write-up, but there are multiple tutorials on using ESP32s (or other low power devices) as brokers and powering them via solar.

### Choosing a Device to Connect to the Sensor: Raspberry Pi Considerations

If you do decide on a Raspberry Pi, **make sure you have one with onboard BLE** or you will have to purchase a 3rd party USB BLE device in addition.

Raspberry Pi models with BLE include:

* Pi 3B - 4.1 BLE
* Pi 3B+ - 4.2 BLE
* Pi Zero W (Wireless) - 4.1 BLE
* Pi 4 - 5.0 BLE

**Note:** None of the Pi Zeros other than the Pi Zero W have onboard BLE capabilities and none of the Pis before the 3B have onboard BLE.

**Note2:** The sensors use a [Dialog Semiconductor DA14580 SoC](https://www.dialog-semiconductor.com/products/connectivity/bluetooth-low-energy/smartbond-da14580-and-da14583) which uses BLE version 4.2 

[Back To Index](#BLE-LawnMonitor)

## Understanding Distance Limitations

BLE 4.2 supposedly has a max distance of up to 50m (about 164') but it completely depends on environmental deployment and I sincerely doubt that in the use case here. 

I will once again re-iterate that you will have very unreliable connectivity with any firmware on the sensors prior to 3.1.9. My recommendation is upgrade the firmware, ensure connectivity to the sensors (next few steps below), and then to test in temporary outdoor locations before placing sensors and polling devices.

[Back To Index](#BLE-LawnMonitor)

## Upgrade Sensor Firmware to 3.1.9: Overview

Upgrading the sensor is a finicky process and I had no luck using the "Northfifteen" mobile app.  You will have much better luck with the official Xiaomi app called "Mi Home."  I found that connectivity prior to 3.1.9 is prone to drops and other issues using various BLE devices and scanners. Connectivity seems to be much easier after the firmware upgrade. **I wouldn't bother installing the Northfifteen app - follow the steps below in order to get the firmware to 3.1.9 (current version as of this writing).**

### Upgrade Sensor Firmware to 3.1.9: Tips for Success Before You Begin

* If you have multiple sensors, take the battery out of all but one to keep things simple.
* I had issues with one of the CR2032 batteries that shipped with a sensor and had to replace it. They are cheap and I usually have some on-hand for projects and car key FOBs.
* You may have to try to connect several times, the best thing to do is have the app open, take the battery out put it back in, and then try to connect to the device. The LED/light sensor on the top of the device should light up. It may take a few tries but this process does work.

### Upgrade Sensor Firmware to 3.1.9: Detailed Steps

1) Before installing the Xiaomi Mi Home mobile app, you should sign up for a Xiaomi home account from a laptop/desktop and use those credentials to sign into the mobile app. Signing up via the Mobile app does not give as many options and you may not be able to connect to the sensor. *You will not need the app after all sensors have been upgraded so you can delete it from your mobile device.*

> **IMPORTANT:** You *must* choose **mainland china** as your location when signing up on the Mi Home website, otherwise you will not be able to add a Plant Monitor to your account via the mobile app! English as the language and mainland china as the location are both allowed in the online account setup.  A permanent email is not required, the Xiaomi app is only to used once to upgrade the firmware for each sensor.

2) Sign into the Xiaomi mobile app. *With the battery out of all sensors except the one you plan to upgrade*, put the battery into the single sensor. The LED at the top should light up momentarily.

3) Click on the (+) in the top right-hand corner of the mobile app to add the sensor.

4) You should see the sensor as a new device near the top of the screen - click on it when you do. 

> **NOTE:** If you *do not* see the sensor near the top of the screen after clicking the + sign try one or more of the following:
> * Take the battery out and put it back in and try to connect again
>  * If you do not see the LED on the top of the sensor light up momentarily, replace the CR2032 battery
> * Exit/re-open the mobile app 
> * In certain instances, disabling and re-enabling bluetooth on the phone works
> * Try connecting with another app/device to see if you can see the sensor. Several tools are listed under the [Get Sensor BlueTooth MAC](#Get-Sensor-BlueTooth-MAC) section below.
> * Note that once you've connected to one sensor, the rest of the connections/upgrades seem to go smoothly

5) After a successful first time connection, you *must* choose a plant to finish the device setup - it doesn't matter which one. After, you should see the device in the Mi Home mobile app's main page. 

6) Click on the device's picture in the mobile app, click the three dots on the top right-hand corner of the mobile app.  

7) Click `Device settings` then `Hardware Settings`.  If the Firmware is anything prior to 3.1.9, upgrade the sensor. **It's best not to exit the screen until the firmware upgrade is complete.**

8) *Optional*: Once the 3.1.9 firmware upgrade done, you can rename the sensor from the previous Settings screen under "Device name."   

**Note:** If you have more than one sensor, it's best to get the BLE MAC as outlined in the next step and then remove the battery and repeat the process for other sensors.

[Back To Index](#BLE-LawnMonitor)

## Get Sensor BlueTooth MAC Address

> **Note:** All of the sensors will show up as "FlowerCare" on scans so its best to leave all batteries out of all but the one you're currently upgrading/testing at the time.

There are any number of ways to get the sensor's BlueTooth MAC. If you already have your Pi setup, you can install the `hcitool` package on the pi and do a BLE scan:

```shell
pi@iot-pi:~ sudo apt-get -y install hcitool
pi@iot-pi:~ $ sudo hcitool lescan
LE Scan ...
40:16:3A:62:44:FF (unknown)
C4:7C:8D:63:D4:A1 Flower care
```
There are also mobile apps such "BLE Scanner" (iOS) that work - all you need is the MAC address of each device so it's not necessary to connect to the sensor over BlueTooth at this this point.

> **IMPORTANT:** Once have the MAC address for "Flower care," write it down or copy it exactly as it appears.

Repeat the firmware upgrade and MAC discovery processes above for all sensors one at a time. 

Once complete for all devices, you can delete the Mi Home app from your mobile device.

[Back To Index](#BLE-LawnMonitor)

## Setting Up Python Environment (Raspberry Pi)

As stated previously, it makes sense to test connectivity and placement first.  This example assumes a Raspberry Pi with Raspbian or any other compatible Linux flavor OS with Python 3.7+ installed.

> **Note:** To save a step later, this section includes retrieving this git repository + Python code and creating a virtual environment on the Raspberry Pi.

> The default version of python on the Raspbian OS is 2.7. If you're following these steps verbatim (i.e. assuming a Raspberry Pi and Raspbian) you need to install Python 3.7 and pip by running `sudo apt install -y python3 && sudo apt install -y python3-pip` first.

1) Ensure your version of Python (the code in this repo was tested on 3.7 although 3.5+ should work)
``` shell
pi@iot-pi:~ $ python3 --version
Python 3.7.3
pi@iot-pi:~ $
```

2) Make sure pip is installed:
``` shell
pi@iot-pi:~ $ pip3 --version
pip 18.1 from /usr/lib/python3/dist-packages/pip (python 3.7)
pi@iot-pi:~ $
```

3) Create the directory for the Python virtual environment
``` shell
pi@iot-pi:~ $ mkdir -p ~/dev/lawnpoller
```

4) Clone this repo into `~/dev/lawnpoller` directory:

``` shell
pi@iot-pi:~ $ git clone zabrewer@github.com:lawnpoller ~/dev/lawnpoller
```

5) Create Python Virtual Environment in the `~/dev/lawnpoller` directory:
``` shell
pi@iot-pi:~ $ python3 -m venv ~/dev/lawnpoller && cd ~/dev/lawnpoller && source bin/activate
(lawnpoller) pi@iot-pi:~/dev/lawnpoller $
```
> Note the shell above changed to the name of the virtual environment in parentheses indicating that we are now in the ```lawnpoller``` virtual environment.  E.g. ```(lawnpoller) pi@iot-pi:~/dev/lawnpoller $```

6) If all went well, we can install Python dependencies into the virtual environment:
``` shell
(lawnpoller) pi@iot-pi:~/dev/lawnpoller $ python setup.py .
```
> If you have more than one Raspberry Pi (or other polling device), you will have to repeat Steps 1-6 above for each Pi.

## Testing Connectivity to the Sensors

We are now ready to test connectivity to a sensor by using the Python shell.  You should have the BLE MAC for the device that you are testing.

> For the first connection, I recommend that the sensor should be close to the Raspberry Pi, you can always repeat this process for testing distance limitations and more.

1) Verify that the lawnpoller virtual environment is still active and enter the Python interactive shell:
```Python
pi@iot-pi: source ~/dev/lawnpoller/bin/activate && python
(lawnpoller) pi@iot-pi: ~/dev/lawnpoller $
Python 3.7.3 (default, Dec 20 2019, 18:57:59)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

2) Test connectivity to the sensor (by BlueTooth MAC address) using the btlewrap and miflora Python packages

> You must change ```sensor_mac = 'YOUR-SENSOR-MAC'``` below to your include your devices MAC address, e.g. ```sensor_mac = 'AA:BB:CC:DD:EE:FF'```

```python
>>> from miflora.miflora_poller import MiFloraPoller
>>> from btlewrap.bluepy import BluepyBackend
>>> sensor_mac = 'YOUR-SENSOR-MAC'
>>> poller = MiFloraPoller(sensor_mac, BluepyBackend)
>>> print(poller.firmware_version())
>>> print(poller.firmware_version())
>>> print(poller.firmware_version())
>>> exit()
```

> If your device connection was successful, you should see output from the sensor after the print statement lines above.

Repeat steps 1 & 2 above as necessary for Pi's and sensors including outdoor placement.

## Google Sheets: Intro

TimeStamp	Pi	Sensor	Battery	Temp	Moisture	Light	Conductivity

    Go to the Google APIs Console.
    Create a new project.
    Click Enable API. Search for and enable the Google Drive API.
    Create credentials for a Web Server to access Application Data.
    Name the service account and grant it a Project Role of Editor.
    Download the JSON file.
    Copy the JSON file to your code directory and rename it to client_secret.json



https://console.developers.google.com/


### Google Sheets: Creating the Sheet

### Google Sheets: Creating Google Sheets API Key

## Customizing the Python Code from this Repo
 
## Creating a Polling Schedule Using Cron
