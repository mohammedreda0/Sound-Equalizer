from os import sep
from typing import Counter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QSlider
from numpy.core.arrayprint import DatetimeFormat
from numpy.core.numerictypes import maximum_sctype
from numpy.lib.function_base import place
import pyqtgraph
from GUI import Ui_MainWindow
import sys
import numpy as np
from math import *
import numpy.fft as fft
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from scipy.io import wavfile
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
import sounddevice as sd
import scipy.io.wavfile
import soundfile as sf

yarr = [1, 2, 3, 4]
xarr = [1, 2, 3, 0]

R2 = np.corrcoef(xarr, yarr)
print(R2)
