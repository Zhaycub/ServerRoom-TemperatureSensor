# -*- coding: utf-8 -*-

# Author : rdagger
# Site   : http://www.rototron.info
# 
# Date   : 19/04/2014

# Imports
import webiopi
import datetime
import time
from webiopi import deviceInstance
import sys
sys.path.append("/home/pi/webiopi/test01/scripts")
import lcd2
from suds.client import Client

# Initialize LCD display
lcd2.__init__()

# Enable debug output
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

# Temperature thresholds
COLD = 69.9
HOT = 79.0

# RGB LED GPIO's
RED = 11
GREEN = 9
BLUE = 10

# Switch GPIO
# Next version of WebIOPi should support interrupts (better approach)
SWITCH = 18

# Display State: Current Temperature or Temperature Range
displayCurrent = False

# Set temperature sensor (specified in WebIOPi config)
t = deviceInstance("ServerRoom")

# Initialize temperature range variables
tLow = t.getFahrenheit()
tHigh = t.getFahrenheit()

# Hour Counter
hourCounter = datetime.datetime.now().hour

# Critical flag
criticalSent = False


# Web Service URI
# *** YOU MUST CHANGE TO THE IP OF YOUR WEB SERVER ***
URI = 'http://(IP.ADDRESS):8000/'


# Called by WebIOPi at script loading
def setup():
    webiopi.debug("Script with macros - Setup")
    # Setup GPIOs
    GPIO.setFunction(RED, GPIO.PWM)
    GPIO.setFunction(GREEN, GPIO.PWM)
    GPIO.setFunction(BLUE, GPIO.PWM)
    GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    

# Looped by WebIOPi
def loop():
    # Run every 5 seconds
    try:
        # Get current temperature
        fahrenheit = t.getFahrenheit()
        webiopi.debug("Current: %0.1f°F" % fahrenheit)

        # Set high & low 
        if fahrenheit > tHigh:
            tHigh = fahrenheit
        if fahrenheit < tLow:
            tLow = fahrenheit
        webiopi.debug("Low:     %0.1f°F" % tLow)
        webiopi.debug("High:    %0.1f°F" % tHigh)

        # Temperature thresholds
        global tHigh
        global tLow
        webiopi.debug("Cold Threshold:    %0.1f°F" % COLD)
        webiopi.debug("Hot Threshold:     %0.1f°F" % HOT)
      
        # Display State
        global displayCurrent
        displayCurrent = not displayCurrent

        # WH1602B-CTI Backlight Colors at 3.3V
        # Red:           RGB 0.0, 1.0, 1.0
        # Green:        RGB 1.0, 0.0, 1.0
        # Blue:         RGB 1.0, 1.0, 0.0
        # Purple:       RGB 0.0, 1.0, 0.0
        # Chartreuse:   RGB 0.0, 0.0, 1.0
        # Cyan:         RGB 1.0, 0.0, 0.0
        # Aquamarine:   RGB 1.0, 0.0, 0.5
        # Turquoise:    RGB 1.0, 0.5, 0.0
        # Violet:       RGB 0.0, 1.0, 0.5
        # Slate Blue:   RGB 0.5, 1.0, 0.0
        # Lime:         RGB 0.5, 0.0, 1.0
        # Yellow Green: RGB 0.0, 0.5, 1.0
        # Peach:        RGB 0.0, 0.9, 1.0
        # Orange:       RGB 0.0, 0.96, 1.0
        # Yellow:       RGB 0.0, 0.7, 1.0
        # White:        RGB 0.0, 0.6, 0.8

        if GPIO.digitalRead(SWITCH) == GPIO.LOW:
            # Reset switch pressed
            tHigh = fahrenheit
            tLow = fahrenheit
            # LCD background white
            GPIO.pwmWrite(RED, 0.0)
            GPIO.pwmWrite(GREEN, 0.6)
            GPIO.pwmWrite(BLUE, 0.8)
            lcd2.lcd_byte(lcd2.LCD_LINE_1, lcd2.LCD_CMD)
            lcd2.lcd_string("Current: %0.1f" % (fahrenheit)  + chr(223) + "F")
            lcd2.lcd_byte(lcd2.LCD_LINE_2, lcd2.LCD_CMD)
            lcd2.lcd_string("Temp Range Reset")
        elif displayCurrent:
            # LCD background for current state
            if fahrenheit >= HOT:
                GPIO.pwmWrite(RED, 0.0)
                GPIO.pwmWrite(GREEN, 1.0)
                GPIO.pwmWrite(BLUE, 1.0)
            elif fahrenheit <= COLD:
                GPIO.pwmWrite(RED, 1.0)
                GPIO.pwmWrite(GREEN, 1.0)
                GPIO.pwmWrite(BLUE, 0.0)
            else:
                GPIO.pwmWrite(RED, 1.0)
                GPIO.pwmWrite(GREEN, 0.0)
                GPIO.pwmWrite(BLUE, 1.0)
            # Display current
            lcd2.lcd_byte(lcd2.LCD_LINE_1, lcd2.LCD_CMD)
            lcd2.lcd_string("Current: %0.1f" % (fahrenheit)  + chr(223) + "F")
            lcd2.lcd_byte(lcd2.LCD_LINE_2, lcd2.LCD_CMD)
            lcd2.lcd_string(" ")
        else:
            # LCD background for range state
            if fahrenheit >= HOT:
                GPIO.pwmWrite(RED, 0.0)
                GPIO.pwmWrite(GREEN, 0.96)
                GPIO.pwmWrite(BLUE, 1.0)
            elif fahrenheit <= COLD:
                GPIO.pwmWrite(RED, 0.5)
                GPIO.pwmWrite(GREEN, 1.0)
                GPIO.pwmWrite(BLUE, 0.0)
            else:
                GPIO.pwmWrite(RED, 1.0)
                GPIO.pwmWrite(GREEN, 0.0)
                GPIO.pwmWrite(BLUE, 0.5)
            # Display range
            lcd2.lcd_byte(lcd2.LCD_LINE_1, lcd2.LCD_CMD)
            lcd2.lcd_string("Low:  %0.1f" % (tLow)  + chr(223) + "F")
            lcd2.lcd_byte(lcd2.LCD_LINE_2, lcd2.LCD_CMD)
            lcd2.lcd_string("High: %0.1f" % (tHigh)  + chr(223) + "F")

        # Log will be uploaded based on the hour counter
        global hourCounter
        global criticalSent
        webiopi.debug("Hour Counter:     %0.0f" % hourCounter)
        
        # Check if hour changed
        if hourCounter != datetime.datetime.now().hour:
            hourCounter = datetime.datetime.now().hour
            # Upload log
            client = Client(URI)
            sResult = client.service.UploadLog('Server Room',
                                               'Info',
                                               fahrenheit)
            webiopi.debug("Log Upload: " + sResult)
            # Reset critical notification flag
            criticalSent = False
        # Notify if temperature critical
        if not criticalSent and fahrenheit >= HOT:
            client = Client(URI)
            sResult = client.service.Notify('rdagger',
                                            fahrenheit)
            webiopi.debug("Log Notify: " + sResult)
            # Only allow 1 email per hour
            criticalSent = True
  
    except:
        webiopi.debug("error: " + str(sys.exc_info()[0]))
    finally:
        webiopi.sleep(5)  

# Called by WebIOPi at server shutdown
def destroy():
    webiopi.debug("Script with macros - Destroy")
    # Reset GPIO functions
    GPIO.setFunction(RED, GPIO.IN)
    GPIO.setFunction(GREEN, GPIO.IN)
    GPIO.setFunction(BLUE, GPIO.IN)
    GPIO.setFunction(SWITCH, GPIO.IN)

# A macro to reset temperature range from web
@webiopi.macro
def ResetTempRange():
    webiopi.debug("Reset Temp Range Macro...")
    global tHigh
    global tLow
    fahrenheit = t.getFahrenheit()
    tHigh = fahrenheit
    tLow = fahrenheit
    # LCD Background Cyan
    GPIO.pwmWrite(RED, 1.0)
    GPIO.pwmWrite(GREEN, 0.0)
    GPIO.pwmWrite(BLUE, 0.0)
    # Display current temperature on LCD display
    lcd2.lcd_byte(lcd2.LCD_LINE_1, lcd2.LCD_CMD)
    lcd2.lcd_string("Temp Range Reset")
    lcd2.lcd_byte(lcd2.LCD_LINE_2, lcd2.LCD_CMD)
    lcd2.lcd_stri9ng("( HTTP Request )")


# A macro to get the sensor temperature from web
@webiopi.macro
def GetSensorTemp():
    webiopi.debug("GetSensorTemp Macro...")
    # Get current temperature
    fahrenheit = t.getFahrenheit()
    # LCD Background Purple
    GPIO.pwmWrite(RED, 0.0)
    GPIO.pwmWrite(GREEN, 1.0)
    GPIO.pwmWrite(BLUE, 0.0)
    
    # Display current temperature on LCD display
    lcd2.lcd_byte(lcd2.LCD_LINE_1, lcd2.LCD_CMD)
    lcd2.lcd_string("Current: %0.1f" % (fahrenheit)  + chr(223) + "F")
    lcd2.lcd_byte(lcd2.LCD_LINE_2, lcd2.LCD_CMD)
    lcd2.lcd_string("( HTTP Request )")
    return "Current:  %0.1f°F\r\nLow:      %0.1f°F\r\nHigh:     %0.1f°F" % (fahrenheit, tLow, tHigh)

# A macro to get the temperature logs
@webiopi.macro
def GetTempLogs(take):
    webiopi.debug("GetTempLogs Macro...")
    client = Client(URI)
    return client.service.GetLog(take)

