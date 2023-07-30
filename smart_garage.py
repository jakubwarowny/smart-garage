import uasyncio as asyncio
from machine import Pin, ADC

# Motion sensor
alarm_led = Pin(28, Pin.OUT)
alarm_is_deactivated = Pin(27, Pin.OUT)
led = Pin(26, Pin.OUT)
motion_sensor = Pin(2, Pin.IN, Pin.PULL_UP)
alarm = Pin(14, Pin.OUT)
button_active_alarm = Pin(14, Pin.IN, Pin.PULL_UP)
activation_alarm = False

# Lamps
lamp1 = Pin(19, Pin.OUT)
lamp2 = Pin(18, Pin.OUT)
button_lamp1 = Pin(13, Pin.IN, Pin.PULL_UP)
button_lamp2 = Pin(12, Pin.IN, Pin.PULL_UP)

# Temperature sensor from Raspberry
sensor_temp = ADC(4)
conversion_factor = 3.3 / 65535
fan = Pin(0, Pin.OUT)

# Change state activation_alarm
async def active_alarm():
    global activation_alarm
    while True:
        await asyncio.sleep_ms(10)
        if button_active_alarm.value() == 0:
            activation_alarm = not activation_alarm
            await asyncio.sleep(1)

async def main():
    while True:
        if motion_sensor.value() == 1:
            # and alarm is activation, waiting for state 1 from sensor
            if activation_alarm: 
                for _ in range(20):
                    print("Alarm is on")
                    alarm_led.toggle()
                    alarm_is_deactivated.value(0)
                    alarm.toggle()
                    await asyncio.sleep(0.1)
            # alarm is deactivated, waiting for state 1 from sensor
            else:
                print("Lamps is on")
                alarm_is_deactivated.value(1)
                led.value(1)
                await asyncio.sleep(3)
        # alarm is activation, but sensor have state 0
        elif activation_alarm:
            print("Alarm is on, waiting for move")
            alarm_is_deactivated.value(0)
            led.value(0)
            alarm_led.value(0)
            alarm.value(0)
            await asyncio.sleep(0.5)
        # alarm is deactivated and sensor have state 0
        else:
            print("Waiting for move")
            alarm_is_deactivated.value(1)
            led.value(0)
            alarm_led.value(0)
            alarm.value(0)
            await asyncio.sleep(0.5)

# turn on / turn off lamps
async def turn_on_lamps():
    lamp1_state = False
    lamp2_state = False
    
    while True:
        await asyncio.sleep_ms(10)
        if button_lamp1.value() == 0:
            lamp1_state = not lamp1_state
            lamp1.value(1 if lamp1_state else 0)
            await asyncio.sleep(0.5)
        elif button_lamp2.value() == 0:
            lamp2_state = not lamp2_state
            lamp2.value(1 if lamp2_state else 0)
            await asyncio.sleep(0.5)
            
async def temperature_sensor():
    while True:
        # Temperature reading
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706) / 0.01721
        temperature_rounded = round(temperature, 1)
        print(f"Temperature: {temperature_rounded} °C")
        if temperature_rounded >= 35:
            fan.value(1)
            print("The temperature is too high, fan is on")
        elif temperature_rounded <= 27:
            fan.value(0)
        await asyncio.sleep(30)
        
# Run the main loop as an asynchronous job with asyncio.gather()
async def run_tasks():
    await asyncio.gather(active_alarm(), main(), turn_on_lamps(), temperature_sensor())
# Run main loop asynchronous
asyncio.run(run_tasks())