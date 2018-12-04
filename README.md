# ServerRoom-TemperatureSensor

The problem we are trying to address.

The problem addressed when making this project was the temperature of the server room in our school. The idea was to monitor the server room to make sure it was not overheating, because it is a common problem. We solved this problem by making a temperature monitor that can display the high, low, and current temperatures. This monitor can also give a light signal when the temperature leaves a certain temperature range.


Design Process

The idea was prompted to us by our teacher Mr. Replogle. He gave us a website to work with to complete this project. The website, https://www.rototron.info/projects/pi-temperature-monitor/ . We took the base from that and decided to make changes according to what we needed to accomplish. Such as, he had a reset, but we decided not to add the switch.


What it does

This temperature monitor has a sensor to get the temperature of a room. A small LCD screen displays the high temperature, the low temperature, and the current temperature; as well as, when there is an HTTP request. If the current temperature is within a set range, which ours is 60 – 80 degrees Fahrenheit, a small LED light will glow green; however, the light of the LED glows red if it exits that range.


Guide

We wrote a write-up on how we did it all and how it is set up. It is all in the word document called "Temperature Monitor." Also, there are pictures of before, after, and a clearer demonstration of how its set up in "Temperature Monitor Media" powerpoint.


After completion

Insert the tray into your server room at your location of choice. Power your Raspberry Pi. VNC Viewer into said Pi. Open the command line and run the script. sudo webiopi –d –c /etc/webiopi/config
Open the website via your IP address at port 8000
