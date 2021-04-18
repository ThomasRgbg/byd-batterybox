# byd-batterybox
Musings about the BYD Batterybox HVS

Due to the forum entry https://www.photovoltaikforum.com/thread/154935-iobroker-adapter-f%C3%BCr-byd-hvs/?postID=2245679#post2245679 I found https://github.com/christianh17/ioBroker.bydhvs . But since my home automation playground is completly written from scratch in Python, I started to convert the iobroker adapter into a Python3 script. 

While trying around (and also had a closer look into the .js files of the BYD app) I got the feeling this is the Modbus RTU protocol. However, running over a TCP connection. The background is, in the battery box is a simple serial to network module. (Likely from www.hlktech.net, the web username/password is still their default - BE CAREFUL WHEN CHANGING ANY NETWORK SETTINGS, THERE IS MAYBE NO RESET POSSIBLE WHEN LOCKED OUT... however, having an webserver runing with a well-known password is also not desireable...) 

So when using the Modbus RTU protocol on port 8080, it seems you can get meaningful data from the Batterybox. 

This is just a proof-of-concept and the beginning of more work. The TOOD list is long:

* I used the minimalmodbus library for CRC calculation, but not for the communication and packets itself.
* At the moment only int16 values are read and just single values are supported.
* Each read will create a new TCP socket connection.

IMPORTANT: As the MIT license says, NO WARRANTY. Please be extremly when using this scripsts, it is all on your own risk. To my best knowledge, this script does only read values. But I can not give any guarantee it works. And the consequences can be quite significant. Not just a non-working device or lost guarantee. However, this is also about high-voltage, high-power, high-energy electricity devices with all related risks....
