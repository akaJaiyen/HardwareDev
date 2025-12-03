from machine import Pin, ADC, PWM, SoftI2C
from time import sleep
import ssd1306
i2c = SoftI2C(sda=Pin(48), scl=Pin(47))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# display.hline(48,10,30,3)
# display.line(63,10,40,50,3)
# display.line(63,10,83,50,3)


display.hline(90,30,10,3)

display.line(95,30,85,40,3)
display.line(75,35,85,40,3)
display.line(95,30,105,40,3)
display.line(115,35,105,40,3)

display.vline(30,19,42,3)
display.hline(30,29,10,3)
display.vline(40,29,15,3)
display.hline(20,43,10,3)
display.vline(20,43,10,3)

display.vline(57,0,70,3)

display.hline(85,2,13,4)
display.vline(98,2,13,4)

display.vline(35,2,13,4)
display.hline(22,14,13,4)
display.hline(22,8,13,4)
display.vline(22,8,6,4)
display.line(20,1,30,8,4)



display.show()