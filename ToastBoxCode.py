import tkinter
import time
import math
import smtplib
from pigpio_encoder import pigpio_encoder

#Imports NFC library
from pn532 import *

#Motor Initialisation
import RPi.GPIO as GPIO
GPIO.setwarnings(False) #Stops warnings 
GPIO.setmode(GPIO.BCM)  #BCM Numbering
GPIO.setup(5, GPIO.OUT) #Forward
GPIO.setup(6, GPIO.OUT) #Back
GPIO.setup(16, GPIO.OUT) #Enable
GPIO.output(5, 0)
GPIO.output(6, 0)

#Magnet control GPIO
GPIO.setup(25, GPIO.OUT)
GPIO.output(25, 1) #Start with magnet on

#Lever check GPIO
GPIO.setup(24, GPIO.IN) #pull_up_down=GPIO.PUD_DOWN
LeverPulled = False
#Setup Emails
smptUser='toastbox1000@gmail.com'
smptPass='CunninghamBox'

toAdd='cameronphun@gmail.com'
toAdd2='luke.nadj@gmail.com'
toAdd3='nihalsoofi@gmail.com'

subject='Toaster Notification'



def leverON(channel):
    global LeverPulled
    LeverPulled = True

GPIO.add_event_detect(24, GPIO.RISING,callback=leverON, bouncetime=3)

#Counter Value
x = 1

def rotary_callback(counter):
    global x
    x = counter
    print("Counter value: ", counter)

def sw_short():
    print("Switch pressed")
    CountdownTimer.startTimer()


class Clock(tkinter.Label):
    """ Class that contains the clock widget and clock refresh """

    def __init__(self, parent=None, seconds=True, colon=False):
        """
        Create and place the clock widget into the parent element
        It's an ordinary Label element with two additional features.
        """
        tkinter.Label.__init__(self, parent)

        self.display_seconds = seconds
        if self.display_seconds:
            self.time     = time.strftime('%H:%M:%S')
        else:
            self.time     = time.strftime('%I:%M %p').lstrip('0')
        self.display_time = self.time
        self.configure(text=self.display_time)

        if colon:
            self.blink_colon()

        self.after(200, self.tick)


    def tick(self):
        """ Updates the display clock every 200 milliseconds """
        if self.display_seconds:
            new_time = time.strftime('%H:%M:%S')
        else:
            new_time = time.strftime('%I:%M %p').lstrip('0')
        if new_time != self.time:
            self.time = new_time
            self.display_time = self.time
            self.config(text=self.display_time)

        #rotary
        if my_rotary.counter != my_rotary.last_counter:
            my_rotary.last_counter = my_rotary.counter
            my_rotary.rotary_callback(my_rotary.counter)

        self.after(200, self.tick)


    def blink_colon(self):
        """ Blink the colon every second """
        if ':' in self.display_time:
            self.display_time = self.display_time.replace(':',' ')
        else:
            self.display_time = self.display_time.replace(' ',':',1)
        self.config(text=self.display_time)
        self.after(1000, self.blink_colon)

class Timer(tkinter.Label):
    """ Class that contains the countdown timer widget and refresh """

    def __init__(self, parent=None, default=1):
        """
        Create and place the timer widget into the parent element
        It's an ordinary Label element with two additional features.
        """
        tkinter.Label.__init__(self, parent)

        self.defaultHour, self.defaultMinute = divmod(x, 4)
        self.defaultMinute = 15*self.defaultMinute
        self.hour = self.defaultHour
        self.minute = self.defaultMinute

        self.TimerStarted = False
        
        self.update() 
        self.tick2()           

    def update(self):
        """ Updates the display clock """
        self.hourSTR = str(self.hour)
        self.minuteSTR = str(self.minute)
        self.minuteSTR = self.minuteSTR.zfill(2)
        self.time = self.hourSTR + ":" + self.minuteSTR
        self.display_time = self.time
        self.configure(text=self.display_time)

    def tick2(self):
        self.hour, self.minute = divmod(x, 4)
        self.minute = 15*self.minute
        self.update()
        #print(self.display_time)
        if self.TimerStarted and LeverPulled:
            self.tick()
        else:
            self.after(200, self.tick2)

    def tick(self):
        """ Updates the display clock every 200 milliseconds """
        
        self.minute -= 1
        if self.minute == -1:
            self.minute = 59
            self.hour = self.hour - 1

        global LeverPulled
        #When timer ends by time
        if self.hour == 0 and self.minute == 0:
            #Unlock magnet for 2 seconds
            GPIO.output(25, 0)
            time.sleep(2)
            GPIO.output(25, 1)
            
            #Turn on motor to release phone
            GPIO.output(5, 1)
            GPIO.output(6, 0)
            time.sleep(0.05)
            GPIO.output(5, 0)

            #Restart timer selection loop
            self.TimerStarted = False
            LeverPulled = False
            self.tick2()
        
        #When timer ends by NFC
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            if hex(uid[0])=='0x5d' and hex(uid[1])=='0x1a' and hex(uid[2])=='0x88' and hex(uid[3])=='0xaa':
                #Unlock magnet for 2 seconds
                GPIO.output(25, 0)
                time.sleep(2)
                GPIO.output(25, 1)

                #Turn on motor to release phone
                GPIO.output(5, 1)
                GPIO.output(6, 0)
                time.sleep(0.05)
                GPIO.output(5, 0)

                #Restart timer selection loop
                self.TimerStarted = False
                LeverPulled = False
                self.tick2()

        if self.TimerStarted:
            self.update()
            self.after(1000, self.tick)

    def startTimer(self):
        if self.TimerStarted == False:
            GPIO.output(6, 1)
            GPIO.output(5, 0)
            time.sleep(0.05)
            GPIO.output(6, 0)
            #Email
            header='ToastBox Australia'
            body='Dear User, \nYou have just placed your phone into our ToastBox\nKind Regards,\nToastBox Team'
            s=smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(smptUser,smptPass)
            s.sendmail(smptUser, toAdd,header+'\n\n'+body)
            s.sendmail(smptUser, toAdd2,header+'\n\n'+body)
            s.sendmail(smptUser, toAdd3,header+'\n\n'+body)
            s.quit()
        self.TimerStarted = True
        
    def blink_colon(self):
        """ Blink the colon every second """
        if ':' in self.display_time:
            self.display_time = self.display_time.replace(':',' ')
        else:
            self.display_time = self.display_time.replace(' ',':',1)
        self.config(text=self.display_time)
        self.after(1000, self.blink_colon)
        
my_rotary = pigpio_encoder.Rotary(clk=27, dt=22, sw=18)
my_rotary.setup_rotary(min=1, max=32, rotary_callback=rotary_callback)
my_rotary.setup_switch(sw_short_callback=sw_short)

window = tkinter.Tk()
frame  = tkinter.Frame(window, width=800, height=800 )
frame.pack()

clock1 = Clock(frame, seconds=True, colon=False)
clock1.pack()
clock1.configure(bg='orange',fg='black',font=("helvetica",50))
    
CountdownTimer = Timer(frame, default=x)
CountdownTimer.pack()
CountdownTimer.configure(bg='orange',fg='black',font=("helvetica",50))

def main():
    try: 
        #NFC Initialisation
        global pn532 
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

    except Exception as e:
        print(e)

    window.mainloop()

        
if __name__ == "__main__":
    
    main()
