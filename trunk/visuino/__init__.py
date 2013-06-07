'''
The VISUINO project presents an a friendly user interface for visual
programming of the Arduino platform.
'''
print('visuino.__init__: Loading settings...')
from .settings import load_default
load_default()