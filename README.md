# TCPserial
Python script to create a TCP server on the specified port to expose the specied serial port to the network.

Personally, I'm using this as a workaround to Windows serial ports in Windows Subsystem for Linux (WSL) to flash chips with ESP-IDF.
Connection to a socket can be achieved by specifying a URI instead of the port name/path like so:
```
idf.py flash -p socket://192.168.1.71:8080 -b 921600
```

# ESP-IDF Flashing Speed Support
When using the ESP-IDF build system to flash chips (idf.py, esptool.py, etc...) communication always starts off at a baud rate of 115200 but, by default, after retrieving initial information about the chip, the baud rate is changed to higher values (or to one that you specify) before the "large" binaries are sent over.

Since esptool is connected to the socket of this script and not a serial port, it can't signal the change of baudrate to the port TCPSerial is exposing so this script looks for the flaher's change baud command in every message and uppon detection parses the requested value changes the serial port's baud rate after delivering the response from the esp chip back to the build system.

The fastest I've managed was around 980000, bytes start dropping. 921600 behaves rock stable for me (long cable).
