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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText("Error")
        self.msg.setWindowTitle("Error")

        self.player = QMediaPlayer()
        self.player2 = QMediaPlayer()

        self.modified_signal = np.array([])
        self.current_slider_gain = [1.0] * 3

        self.bands_powers = [0.0, 0.25, 0.50, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0]
        self.band_slider = {}

        for index in range(3):
            self.band_slider[index] = getattr(
                self.gui, 'band_{}'.format(index+1))

        for slider in self.band_slider.values():
            slider.setDisabled(True)
            slider.setStyleSheet('selection-background-color: grey')

        for index, slider in self.band_slider.items():
            slider.sliderReleased.connect(
                lambda index=index: self.slider_gain_updated(index))

        self.main_graph_data = []
        self.main_graph_sample_rate = 0
        self.current_signal_duration = 0
        self.main_graph_time = []
        self.x_range1 = self.gui.main_graph.getViewBox(
        ).state['viewRange'][0]
        self.play_is_clicked = False
        self.counter = 0
        self.time_length = 0
        self.data_length = 0
        self.step = 0
        self.player = QMediaPlayer()
        self.gui.volume_slider.setMaximum(100)
        self.gui.volume_slider.setMinimum(0)
        self.pen1 = pyqtgraph.mkPen((255, 0, 0), width=3)
        self.max_icon = QtGui.QPixmap("E:/DSP/task33/icons/max.png")
        self.highMid_icon = QtGui.QPixmap("E:/DSP/task33/icons/2.png")
        self.min_icon = QtGui.QPixmap("E:/DSP/task33/icons/mute.png")
        self.lowMid_icon = QtGui.QPixmap("E:/DSP/task33/icons/1.png")
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(
            "E:/DSP/task33/icons/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(QtGui.QPixmap(
            "E:/DSP/task33/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.gui.open_action.triggered.connect(self.open_signal)
        self.gui.play_pause_botton.clicked.connect(self.play_pause)
        self.gui.volume_slider.valueChanged.connect(self.change_volume)
        self.show()

    def open_signal(self):
        self.gui.band_1.setProperty("value", 4)
        self.gui.band_2.setProperty("value", 4)
        self.gui.band_3.setProperty("value", 4)
        self.main_graph_data.clear()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open File", r"E:/DSP/task33/music", "music(*.wav)", options=options)
        print(file_path)
        self.main_graph_sample_rate, data = wavfile.read(
            file_path)
        self.main_graph_data = (data[:, 0].tolist())
        print(len(self.main_graph_data))
        print(self.main_graph_sample_rate)
        self.current_signal_duration = len(
            self.main_graph_data)/self.main_graph_sample_rate
        print(self.current_signal_duration)
        self.main_graph_time = list((np.linspace(
            0, self.current_signal_duration, (len(self.main_graph_data)))))
        for slider in self.band_slider.values():
            slider.setDisabled(False)
            slider.setStyleSheet('selection-background-color: blue')
        # print(self.main_graph_time)
        self.plot_main_graph()
        # print(self.main_graph_data[:10])

        # plt.plot(self.main_graph_data)
        self.step = (1/10)*0.5
        # plt.show()
        url = QUrl.fromLocalFile(file_path)
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.setVolume(50)
        self.gui.volume_slider.setValue(50)

    def change_volume(self):
        current_value = int(self.gui.volume_slider.value())
        self.gui.volume_value_label.setText(str(current_value))
        self.player.setVolume(current_value)
        if current_value > 80:
            self.gui.volume_image_label.setPixmap(self.max_icon)
        elif current_value <= 80 and current_value >= 40:
            self.gui.volume_image_label.setPixmap(self.highMid_icon)
        elif current_value < 40 and current_value > 0:
            self.gui.volume_image_label.setPixmap(self.lowMid_icon)
        else:
            self.gui.volume_image_label.setPixmap(self.min_icon)

    def play_pause(self):
        if(len(self.main_graph_data) > 0):
            if(self.play_is_clicked):
                self.pause_signal()
            else:
                self.play_signal()
        else:

            self.msg.setInformativeText('Please ')

            self.msg.exec_()

    def pause_signal(self):
        self.gui.play_pause_botton.setIcon(self.play_icon)
        self.player.pause()
        self.player2.pause()

        self.timer1.stop()
        self.play_is_clicked = False

    def plot_main_graph(self):
        print(len(self.main_graph_time))
        self.data_length = int(len(self.main_graph_data)/10)
        self.time_length = int(len(self.main_graph_data)/10)
        self.gui.main_graph.setYRange(
            (min(self.main_graph_data)-0.5), (max(self.main_graph_data)+0.5))
        # self.gui.main_graph.setXRange(0, .05)
        # print(len(self.main_graph_data))
        self.gui.main_graph.plotItem.clear()
        self.gui.main_graph.setXRange(0, 1)
        self.gui.main_graph.plotItem.plot(
            self.main_graph_time[:self.time_length], self.main_graph_data[:self.data_length], pen=self.pen1)
        # plotWidget = pyqtgraph.plot(self.main_graph_time,self.main_graph_data,self.pen1)

    def plot_modified_graph(self):
        self.data_length = int(len(self.samples_after)/10)
        self.gui.main_graph.setYRange(
            (min(self.samples_after)-0.5), (max(self.samples_after)+0.5))
        # self.gui.main_graph.setXRange(0, .05)
        # print(len(self.main_graph_data))
        self.gui.main_graph.plotItem.clear()
        self.x_range1[0] = 0
        self.x_range1[1] = 1
        self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
        self.gui.main_graph.plotItem.plot(
            self.main_graph_time[:self.time_length], self.samples_after[:self.data_length], pen=self.pen1)

    def play_signal(self):
        if self.x_range1[0] > (self.main_graph_time[self.time_length-1])+0.1:
            self.x_range1[0] = 0
            self.x_range1[1] = 1
            self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
        self.gui.play_pause_botton.setIcon(self.pause_icon)
        self.player.play()
        self.play_is_clicked = True
        print(self.time_length)
        print(
            f"the max range is {self.x_range1[1]} and min range is {self.x_range1[0]}")
        # no_of_updates = ((self.current_signal_duration)*1000)/20
        # step = ((self.current_signal_duration)/30)/no_of_updates
        # print(f"the desired length of the graph is = {step*no_of_updates}")
        self.timer1 = pyqtgraph.QtCore.QTimer()
        self.timer1.timeout.connect(lambda: self.update_Xaxis(step=self.step))
        self.timer1.start(500)

    def update_Xaxis(self, step):
        if self.x_range1[0] < (self.main_graph_time[self.time_length-1])+0.1:
            self.x_range1[0] = self.x_range1[0]+step
            self.x_range1[1] = self.x_range1[1]+step
            self.gui.main_graph.setXRange(self.x_range1[0], self.x_range1[1])
        else:
            self.timer1.stop()
            self.gui.play_pause_botton.setIcon(self.play_icon)
            self.play_is_clicked = False
        # print(
            # f"the max range is {self.x_range1[1]} and min range is {self.x_range1[0]}")
        # print(f"step = {step}")
        # print(f"no of updates = {no_of_updates}")

    # def modify_signal(self):
    #     frequency_content = np.fft.rfftfreq(
    #         len(self.main_graph_data), d=1/self.main_graph_sample_rate)
    #     modified_signal = np.fft.rfft(self.main_graph_data)
    #     print(frequency_content)
    #     for index, slider_gain in enumerate(self.current_slider_gain):
    #         frequency_range_min = (index + 0) * \
    #             self.main_graph_sample_rate / (2 * 10)
    #         frequency_range_max = (index + 1) * \
    #             self.main_graph_sample_rate / (2 * 10)
    #         range_min_frequency = frequency_content > 60
    #         range_max_frequency = frequency_content <= 196
    #         slider_min_max = []
    #         for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
    #             slider_min_max.append(
    #                 is_in_min_frequency and is_in_max_frequency)
    #         modified_signal[slider_min_max] *= slider_gain
    #     self.samples_after = np.fft.irfft(modified_signal)
    #     self.plot_modified_graph()
    #     self.now = datetime.now()
    #     self.now = f'{self.now:%Y-%m-%d %H-%M-%S.%f %p}'

    #     scipy.io.wavfile.write(
    #         f'{self.now}Output.wav', self.main_graph_sample_rate, self.samples_after.astype(np.int16))
    #     self.player2.setMedia(QMediaContent(
    #         QUrl.fromLocalFile(f'{self.now}Output.wav')))
    #     self.player.stop()
    #     self.player2.play()

    def slider_gain_updated(self, index):
        slider_gain = self.bands_powers[self.band_slider[index].value()]
        # self.band_label[index].setText(f'{slider_gain}')
        self.current_slider_gain[index] = slider_gain
        self.modify_signal2(index)

    def modify_signal2(self, index):
        frequency_content = np.fft.rfftfreq(
            len(self.main_graph_data), d=1/self.main_graph_sample_rate)

        modified_signal = np.fft.rfft(self.main_graph_data)
        # if index == 0:
        range_min_frequency1 = frequency_content > 800
        range_max_frequency1 = frequency_content <= 2000
        # 440 - 3500 Xylophone and piano
        slider_min_max1 = []
        for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency1, range_max_frequency1):
            slider_min_max1.append(
                is_in_min_frequency and is_in_max_frequency)
        modified_signal[slider_min_max1] *= self.current_slider_gain[0]

        range_min_frequency2 = frequency_content > 0
        range_max_frequency2 = frequency_content <= 1000
        # 440 - 3500 Xylophone and piano
        slider_min_max2 = []
        for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency2, range_max_frequency2):
            slider_min_max2.append(
                is_in_min_frequency and is_in_max_frequency)
        modified_signal[slider_min_max2] *= self.current_slider_gain[1]

        range_min_frequency3 = frequency_content > 1800
        range_max_frequency3 = frequency_content <= 11000
        # 440 - 3500 Xylophone and piano
        slider_min_max3 = []
        for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency3, range_max_frequency3):
            slider_min_max3.append(
                is_in_min_frequency and is_in_max_frequency)
        modified_signal[slider_min_max3] *= self.current_slider_gain[2]

        # elif index == 1:
        #     range_min_frequency = frequency_content > 0
        #     range_max_frequency = frequency_content <= 1000
        #     # 700 - 9000 guitar
        #     # contrabasson 20 - 150
        #     slider_min_max = []
        #     for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
        #         slider_min_max.append(
        #             is_in_min_frequency and is_in_max_frequency)
        #     modified_signal[slider_min_max] *= self.current_slider_gain[1]

        # elif index == 2:
        #     range_min_frequency = frequency_content > 1800
        #     range_max_frequency = frequency_content <= 11000
        #     # 0 - 880 drums
        #     # piccolo 500 - 4000
        #     slider_min_max = []
        #     for is_in_min_frequency, is_in_max_frequency in zip(range_min_frequency, range_max_frequency):
        #         slider_min_max.append(
        #             is_in_min_frequency and is_in_max_frequency)
        #     modified_signal[slider_min_max] *= self.current_slider_gain[2]

        self.samples_after = np.fft.irfft(modified_signal)
        self.plot_modified_graph()
        self.now = datetime.now()
        self.now = f'{self.now:%Y-%m-%d %H-%M-%S.%f %p}'

        scipy.io.wavfile.write(
            f'{self.now}Output.wav', self.main_graph_sample_rate, self.samples_after.astype(np.int16))
        self.player2.setMedia(QMediaContent(
            QUrl.fromLocalFile(f'{self.now}Output.wav')))
        self.player.stop()
        self.player2.play()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Emphasizer = MainWindow()
    sys.exit(app.exec_())
