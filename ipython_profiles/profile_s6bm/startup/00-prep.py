print(f'Enter {__file__}...')
# ----- Ipython control config and standard library import ----- #
# NOTE:
# Do not change the order of import, otherwise it will fail
import os
import matplotlib
import matplotlib.pyplot as plt

import apstools
import bluesky
from datetime import datetime
import getpass
import numpy as np
import ophyd
import socket
import yaml

print("*****")

# get system info
HOSTNAME = socket.gethostname() or 'localhost'
USERNAME = getpass.getuser() or '6-BM-A user'

keywords_vars = {}  # {name: short description}
keywords_func = {}  # {name: short descciption}

print(f'''
🐉: Greetings, {USERNAME}@{HOSTNAME}!
    I, the mighty 🐉, 
    have imported 
        os
        matplotlib
        matplotlib.pyplot as plt <-- interactive, using widget as backend
        apstools
        bluesky
        datetime
        getpass
        numpy 
        ophyd
        socket
        yaml     
    for you, rejoice.
''')


# ----- Setup base bluesky RunEngine and MongoDB ----- #
# metadata streamed to MongoDB server over the network
import databroker
metadata_db = databroker.Broker.named("mongodb_config")
keywords_vars['metadata_db'] = 'Default metadata handler'

# setup RunEngine

from bluesky.callbacks.best_effort import BestEffortCallback
RE = bluesky.RunEngine({})
keywords_vars['RE'] = 'Default RunEngine instance'

RE.subscribe(metadata_db.insert)
RE.subscribe(BestEffortCallback())
RE.md['beamline_id'] = 'APS 6-BM-A'
RE.md['proposal_id'] = 'internal test'
RE.md['pid'] = os.getpid()
RE.md['login_id'] = USERNAME + '@' + HOSTNAME
RE.md['versions'] = {}
RE.md['versions']['apstools'] = apstools.__version__
RE.md['versions']['bluesky'] = bluesky.__version__
RE.md['versions']['databroker'] = databroker.__version__
RE.md['versions']['matplotlib'] = matplotlib.__version__
RE.md['versions']['numpy'] = np.__version__
RE.md['versions']['ophyd'] = ophyd.__version__
RE.md['SESSION_STARTED'] = datetime.isoformat(datetime.now(), " ")

# ----- Define utility functions ----- #
keywords_func['load_config'] = 'Load configuration file (YAML)'
def load_config(yamlfile):
    """load yaml to a dict"""
    with open(yamlfile, 'r') as stream:
        _dict = yaml.safe_load(stream)
    return _dict

keywords_func['instrument_in_use'] = 'instrument status, manual set on IOC'
_signal_instrument_in_use = ophyd.EpicsSignalRO(
    "6bm:instrument_in_use", 
    name="_signal_instrument_in_use",
)
def instrument_in_use():
    """check if the soft IOC for 6BM-A"""
    try:
        state = _signal_instrument_in_use.get()
    except TimeoutError:
        state = False
        print("🙈: cannot find this soft IOC PV, please check the settings.")
    finally:
        print(f"🙈: the instrument is {'' if state else 'not'} in use.")　
        return state

keywords_func['hutch_light_on'] = 'Hutch lighting status'
_signal_hutch_light_on = apstools.synApps_ophyd.userCalcsDevice("6bma1:", 
    name="_signal_hutch_light_on")
def hutch_light_on():
    """check PV for hutch lighting"""
    try:
        state = bool(_signal_hutch_light_on.calc1.val.get())
    except TimeoutError:
        state = None
        print("🙈: cannot find this soft IOC PV, please check the settings.")
    finally:
        print(f"🙈: the hutch is {'' if state else 'not'} on.")
    return state

print(f'leaving {__file__}...\n')
