# src/env.py
import dotenv
dotenv.load_dotenv("../.env")
import os

class ENV:
    API_URL = os.getenv("API_URL")
    LED_R = os.getenv("LED_R")
    LED_G = os.getenv("LED_G")
    LED_B = os.getenv("LED_B")
    BTN_MEASURE = os.getenv("BTN_MEASURE")
    BTN_WHITE_REFERENCE = os.getenv("BTN_WHITE_REFERENCE")
    BTN_BACKGR_RADIATION = os.getenv("BTN_BACKGR_RADIATION")
    DEVICE_ID = os.getenv("DEVICE_ID")
    SHARED_KEY = os.getenv("SHARED_KEY")
    SHARED_SIGN_KEY = os.getenv("SHARED_SIGN_KEY")
    SHARED_ENCR_KEY = os.getenv("SHARED_ENCR_KEY")