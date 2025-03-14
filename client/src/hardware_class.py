# src/hardware_class.py
from gpiozero import Button, RGBLED
from colorzero import Color, Lightness, Saturation, Hue
import asyncio
import time
from env import ENV

class ButtonControl:
    """
    A class representing a control system for physical buttons used in a measurement device.

    Attributes:
    - BTN_MEASURE: Button object for initiating measurement.
    - BTN_WHITE_REFERENCE: Button object for initiating white reference calibration.
    - BTN_BACKGR_RADIATION: Button object for initiating background radiation measurement.

    Methods:
    - measure(): Print a message indicating measurement initiation.
    - white_ref(): Print a message indicating white reference calibration initiation.
    - backgr_rad(): Print a message indicating background radiation measurement initiation.
    - monitor_for_press(): Asynchronous method to continuously monitor button presses and trigger corresponding actions.

    Usage Example:
    ```
    buttons_control = ButtonControl()
    asyncio.run(buttons_control.monitor_for_press())
    ```
    """

    def __init__(self, event_manager) -> None:
        self.BTN_MEASURE = Button(ENV.BTN_MEASURE, pull_up=True)
        self.BTN_WHITE_REFERENCE = Button(ENV.BTN_WHITE_REFERENCE, pull_up=True)
        self.BTN_BACKGR_RADIATION = Button(ENV.BTN_BACKGR_RADIATION, pull_up=True)
        self.event_manager = event_manager
        
        pass

    def measure(self):
        print("MEASURE")
        self.event_manager.measure_event.set()

    def white_ref(self):
        print("WHITEREF")
        self.event_manager.white_ref_event.set()

    def backgr_rad(self):
        print("BACKGROUND RADIATION")
        self.event_manager.backgr_rad_event.set()

    async def monitor_for_press(self):
        def debounced_handler(btn):
            while btn.is_pressed:
                time.sleep(0.2) #debounce
            if not self.event_manager.in_progress:
                if btn == self.BTN_MEASURE:
                    self.measure()
                elif btn == self.BTN_WHITE_REFERENCE:
                    self.white_ref()
                else:
                    self.backgr_rad()
              
        while True:
            await asyncio.sleep(0.5)
            self.BTN_MEASURE.when_pressed = debounced_handler
            self.BTN_WHITE_REFERENCE.when_pressed = debounced_handler
            self.BTN_BACKGR_RADIATION.when_pressed = debounced_handler
            
class LedControl:
    """
    A class representing a control system for the 
    Common Anode RGB LED used in a measurement device.

    Attributes:
    - LED_RGB: (gpiozero.RGBLED) Object initiated using the environment variables for GPIO pins.

    """

    def __init__(self) -> None:
        self.LED_RGB = RGBLED(ENV.LED_R, ENV.LED_G, ENV.LED_B, active_high=False)
        self.gradient = [
            "#4cfb73",
            "#22f14f",
            "#0ae33a",
            "#08d025",
            "#0bbf05",
            "#0cab06", #Green
            "#109f0b",
            "#269616",
            "#156e08",
            "#114709",
            "#0b2807",
        ]
        pass
    
    async def startup_notification(self):
        await self.gradient_hue()
        print("Done startup...")
        return
        
    async def gradient_hue(self):
        j = 0.005
        i = 0
        l = 0.1
        descending = False
        max_i = len(self.gradient) - 1
        while j < 0.95:
            if l <= 0.80:
                l += 0.005 
            current_color = self.gradient[i]
            self.LED_RGB.color = Color(current_color) * Lightness(l) + Saturation(j)
            j += 0.005
            await asyncio.sleep(0.05)
            if descending:
                if i == 0:
                    descending = False
            if not descending:
                if i == max_i:
                    descending = True
            if descending:
                i -= 1
            else:
                i += 1
        self.LED_RGB.color = Color(0, 0, 0)
        return
        
    async def on(self):
        self.LED_RGB.color = Color(0,1,0) * Lightness(0.6)
        
    async def off(self):
        self.LED_RGB.color = Color(0,0,0)
        
    async def blink_red(self):
        i = 0
        while i <= 3: 
            self.LED_RGB.color = Color(1,0,0) * Lightness(0.7) + Saturation(0.3)
            await asyncio.sleep(0.65)
            self.LED_RGB.color = Color(0,0,0)
            await asyncio.sleep(0.65)
            i += 1
        