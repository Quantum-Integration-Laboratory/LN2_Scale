# LN2 Scale
An interface to talk to the scale that measures our LN2 dewer and hopefully sends us a message when its getting low. Forked from Null-none/dymo-scale. 

# Installation
We don't require this package to be installed to pip as everything should just run from this local folder. Installation of requirements should be 
```
pip install -r ./requirements.txt
```

## Setting up path and environment variable (Windows)
We need to point the USB drivers to the correct place make note of where libusb is installed, for me it was something like this:
```
../AppData/Local/Programs/Python/Python39/Lib/site-packages/libusb/_platform/_windows
```
Make sure to add both the `x64` and `x86` folders to path.

While we are there also need to set some environment variables such that we don't need to share secrets. The main one is we need to add a variable `SLACK_BOT_TOKEN` on windows this is in the same place as Path variables.

If the config flag `ALERT_CRASH` is set a `MAINTAINER_SLACK_CHANNEL` slack channel must also be set as an environment variable, this will be something along the lines of `U########`. (Ben Note: I will set it to me but this will likely need to be changed at somepoint.)

## Using the Scheduler (Windows).
The goal is to let the operating system handle the repition of the logging, this should be somewhat less resource intensive.

Open the windows task scheduler, set up a new task

**Trigger:** Begin Task on *startup*, Repeat task every *hour* for a duration of *indefinitely*
**Action:** Start a program *Log.py*

# Config.yaml
This is where we can change most of our settings this is read whenever the program is launched
```
scales:
  PID: (int) Product ID of the scale
  VID: (int) Vendor ID of the scale
slack:
  LOW_CHANNEL: (str) The Slack Channel to send to when we're low
  VERY_LOW_CHANNEL: (str) The Slack channel to send to when we are very low and refil is urgent
  LOW_MESSAGE: (str) The message to send when we are low, only requirement is that a percentage is inserted somewhere
  VERY_LOW_MESSAGE: (str) The message to send when we are very low, only requirement is that a percentage is inserted somewhere
  PLOTTING: (bool) If we send a plot with the low message
logging:
  PATH: (str) The path to save our logs to
  LOGNAME: (str) The name to add to the file timestamp
  REMOVE_OLD: (bool) remove old images, redundant as we just override
  ALERT_CRASH: (bool) Should a slack message be sent on a crash, see environement variables section
weight:
  MAX_WEIGHT: (float) The weight when full
  DRY_WEIGHT: (float) The weight when empty
  LOW: (float) The percentage when we should send the low alert
  VERY_LOW: (float) The percentage when we should send the very low alert
```
# Bens Notes on the scale.
**Vendor ID:** 0x0922

**Product ID:** 0x0922

## Rough Return Registers:
Taken from [this](https://gist.github.com/tresf/898ab2d4d259aef2d4f7) Project they seem to line up pretty well.

Register| 0 | 1      | 2     | 3         | 4        | 5        |
|--------|---|--------|-------|-----------|----------|----------|
|Name| ? | STATUS | UNITS | PRECISION | WEIGHT HB | WEIGHT LB |
 ### STATUS
 I haven't checked these but 2 and 3 seem to line up, busy will still return
| Return|Status|
|---|------------------------|
| 1 |         Fault          |
| 2 |     Stable at Zero     |
| 3 |          Busy          |
| 4 |   Stable at Non-Zero   |
| 5 | Underweight (negative) |
| 6 |       Overweight       |
| 7 |        Calibrate       |
| 8 |         Re-zero        |

### UNITS
| Return|Units|
|---|------------------------|
| 3|         kilograms          |
| 12 |     Ounces     |

### PRECISION
Is a signed int such that we scale by
$$10^{Precision \ XOR \ 255}$$

### WEIGHT HB and WEIGHT LB
Our weight as a 16bit number, with high and low byte. In python it can be combined as:
$$HB+LB*255$$