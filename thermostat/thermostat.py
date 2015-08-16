
gpioStop = open("/sys/class/gpio/unexport/", 'w')
gpioInit.write("17")
gpioInit.write("27")
gpioStop.close()
gpioInit = open("/sys/class/gpio/export", 'w')
gpioInit.write("17")
gpioInit.write("27")
gpioInit.close()
gpio17 = open("/sys/class/gpio/gpio17/direction", 'w')
gpio27 = open("/sys/class/gpio/gpio27/direction", 'w')
gpio17.write("out")
gpio27.write("out")
gpio17.close()
gpio27.close()



# gpio17 = open("/sys/class/gpio/gpio17/value", 'w')
# gpio27 = open("/sys/class/gpio/gpio27/value", 'w')


