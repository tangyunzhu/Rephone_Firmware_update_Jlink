from distutils.core import setup
import py2exe
import numpy
import zmq

import subprocess
import datetime
import shlex
import serial
import os
import signal
import sys
import threading
from serial.tools import list_ports
from time import sleep

setup(console=['Program.py'])