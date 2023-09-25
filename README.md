# LN2 Scale
An interface to talk to the scale that measures our LN2 dewer and hopefully sends us a message when its getting low. Forked from Null-none/dymo-scale. 

# Installation
In order to make files easier to access they can be installed as a package via pip and such.

Our naming convention for a driver is `qil_<DriverName>` matching cases, where `<>` indicates the parts you can change. 
 
With the driver repo written it should be cloned onto a lab pc using github desktop, into the directory `./Docs/GITHUB/Drivers/`, such that there will now be a folder named `./Docs/GITHUB/Drivers/<repo name>`. with structure
```
<repo name>
  |->qil_<DriverName>
  ...
  |->requirements.txt
  \->setup.py
```

With everything cloned correctly, open a terminal or anaconda prompt depending on what is used `cd ./<path>/<repo name>` and then run 
```
pip install --editable .
```
The `--editable` flag means the installed script just points back to the folder so updates will be recognised when we pull any updates into this folder
### Note for windows
We need to point the USB drivers to the correct place make note of where libusb is installed, for me it was something like this:
```
../AppData/Local/Programs/Python/Python39/Lib/site-packages/libusb/_platform/_windows
```
Make sure to add both the `x64` and `x86` folders to path.


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