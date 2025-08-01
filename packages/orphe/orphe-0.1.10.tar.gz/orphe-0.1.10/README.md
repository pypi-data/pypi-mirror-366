# ORPHE ANALYTICS SDK for Python

---------------------------------------

ORPHE ANALYTICIS SDK for Python is a client library that accesses the ORPHE ANALYTICS resource API and real-time API.

## Install

You can install ORPHE ANALYTICIS SDK for Python (hereafter orphe-py) using PyPI. Install with the following command.

```bash
$ pip install orphe
```

If you are using Python 3, you can install it with the following command.

```bash
$ pip3 install orphe
```

## Usage

To start using ORPHE ANALYTICIS SDK, create a client. To create a client, use the URL of the connection destination and the credentials of the edge account (token or user name/password combination). See intdash client for other available parameters.

```python
import orphe

analytics = orphe.Analytics(
    url = "https://example.analytics.orphe.ai",
    token = "your_token",
)
```

Example:
An example for retrieving and storing a value is given below.

```python
import orphe

# Generate a client with a URL and an edge token
analytics = orphe.Analytics(
    url = "https://example.analytics.orphe.ai",
    token= "your_token"
)
# Get data by specifying the measurement UUID
analyzed = analytics.load(
    measurement_uuid = "e07cdf8c-83e6-46cf-8a03-e315eef6162a",
)

# Extract, analyze and display values from stored data (channel 1 -> plantar left, channel 2 -> plantar right)
for gait in analyzed.gait.stored[1]:
    print(f"Plantar left/{gait.time}/{gait.quaternion_w}/{gait.quaternion_x}/{gait.quaternion_y}/{gait.quaternion_z}")

for gait in analyzed.gait.stored[2]:
    print(f"Plantar right/{gait.time}/{gait.quaternion_w}/{gait.quaternion_x}/{gait.quaternion_y}/{gait.quaternion_z}")
    
# If you want to take out the value of gait analysis, you can filter it by [gait.analyzed] from stored data (channel 3 -> Instep left, channel 4 -> Instep right)
for gait in analyzed.gait.stored[3]:
    if not gait.analyzed:
        continue
    print(f"Instep left/{gait.time}/{gait.stride}/{gait.cadence}/{gait.duration}")

for gait in analyzed.gait.stored[4]:
    if not gait.analyzed:
        continue
    print(f"Instep right/{gait.time}/{gait.stride}/{gait.cadence}/{gait.duration}")

# To save the value, use [orphe.Unit]
units = []
for gait in analyzed.gait.stored[1]:
    units.append(orphe.Unit(
        time = gait.time,
        id = "Height",
        value = 160
    ))

# Save the data by specifying the measurement UUID and the list of [orphe.Unit].
analytics.save(
    measurement_uuid="e07cdf8c-83e6-46cf-8a03-e315eef6162a",
    units=units
)
```

After analytics.load is performed, the retrieved valuesanalyzed will contain the values retrieved from ORPHE CORE and the values analyzed by ANALYTICS.
By gait, the data of gait analysis is retrieved, and left and right data can be retrieved respectively.

In addition, if you want to perform real-time analysis, you can use the following method.

```python
import orphe

# Generate a client with a URL and an edge token
analytics = orphe.Analytics(
    url = "https://example.analytics.orphe.ai",
    token= "your_token"
)

# Defines a callback for realtime. [value] will contain the raw and parsed data.
# New real-time data can be sent by returning list[Unit].
# * Real-time data transmission is sent to a separate edge specified by [upstream_edge_uuid].
def callback(value: AnalyticsValue) -> list[Unit]:
    if value.gait.left.stride != None:
        print(value.gait.left.stride)
    if value.gait.left.euler_x != None:
        print(value.gait.left.euler_x)
        
    units = []
    time = value.pose.realtime.time
    val = random.randint(0, 100)
    units.append(Unit(
        time=time,
        channel=3,
        id="RANDOM",
        value=val,
    ))
    return units

# Start real-time acquisition by specifying the callback and the ID of the edge.
# Specify the EdgeUUID to get the real-time data being measured in [downstream_edge_uuid].
# Specify the EdgeUUID for sending real-time values from the SDK in [upstream_edge_uuid].
analytics.realtime(
    callback = callback,
    downstream_edge_uuid="08058fc6-3374-407a-b9ed-fcbe81217ac9",
    upstream_edge_uuid="2e21f332-fb85-4679-ba55-e07e36c12667"
)
```
