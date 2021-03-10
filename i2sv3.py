# -*- coding: utf-8 -*-
import sys
import time
from time import sleep
import wave
import numpy
import struct
import PyQt5.QtWidgets
import pyaudio
import pyqtgraph as pg
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QDoubleValidator, QIntValidator,  QProgressBar, QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QErrorMessage
from PyQt5.QtCore import QObject, QThread, pyqtSignal

# to build app: pyinstaller --windowed i2sv3.spec

p = pyaudio.PyAudio()

# wave file output settings
comptype = "NONE"
compname = "not compressed"

lightstylesheet = """
        QWidget, QErrorMessage {
        background-color: white;
        font-family: 'arial';
        color:black;
        }
        
        QLineEdit, QComboBox, QProgressBar {
            font-weight: 400;
            color: black;
            font-size: 11px;
            border-radius: 5px;
            background-color: rgb(240,240,240);
            padding-left: 2px;
            
            }
        
        

        QPushButton {
            font-weight: 800;
            color: black;
            font-size: 10px;
            border-radius: 10px;
            background-color: rgb(240,240,240);
            }
        QPushButton:hover, QComboBox:hover, QLineEdit:hover {
            font-weight: 800;
            color: black;
            font-size: 10px;
            border-radius: 10px;
            background-color: rgb(220,220,220);
            
            }
            
        QComboBox::drop-down 
            {
                border: 0px; /* This seems to replace the whole arrow of the combo box */
                background-color: rgb(100,100,100);
            }
            
            /* Define a new custom arrow icon for the combo box */
            
            QComboBox::down-arrow {
                image: url(/Users/Y-S/Desktop/i2s-clean/dropdownwhite-01.png);
                width: 10px;
                height: 10px;
                
            }
            
            QProgressBar {
            text-align: center
            }
        
       """

darkstylesheet = """
        QWidget, QErrorMessage {
        background-color: rgb(10,10,15);
        color: white;
        font-family: 'arial';
        }
        
        QLineEdit, QComboBox, QProgressBar {
            font-weight: 400;
            color: white;
            font-size: 11px;
            border-radius: 5px;
            background-color: rgb(20,20,30);
            padding-left: 2px;
            }
        
        

        QPushButton {
            font-weight: 800;
            color: white;
            font-size: 10px;
            border-radius: 10px;
            background-color: rgb(20,20,30);
            }
        QPushButton:hover, QComboBox:hover, QLineEdit:hover {
            font-weight: 800;
            color: white;
            font-size: 10px;
            border-radius: 10px;
            background-color: rgb(50,70,70);
            
            }
            
         QComboBox::drop-down 
            {
                border: 0px; /* This seems to replace the whole arrow of the combo box */
                background-color: rgb(200,200,200);
            }
            
            /* Define a new custom arrow icon for the combo box */
            
            QComboBox::down-arrow {
                image: url(/Users/Y-S/Desktop/i2s-clean/dropdown-01.png);
                width: 10px;
                height: 10px;
                
            }
            
            QProgressBar {
            text-align: center
            }
          
            
        """


def average(values):
    return round(sum(values) / len(values), 2)

'''Implementation of multithreading to avoid bad user experience caused by the freezing Ui on sound playback,
Using QThread, pyqtSignal and QObject along with a progress bar to visualize the conversion rate'''


class ProgressBar(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):

        for i in range(int(num_samples)):
            if not over:
                self.progress.emit(i + 1)
            else:
                break
        self.progress.emit(int(num_samples))
        self.finished.emit()


class ProgressBarI(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):

        for i in range(len(full_wave)):
            if not over:
                self.progress.emit(i + 1)
            else:
                break

        self.progress.emit(len(full_wave))
        self.finished.emit()


class Worker(QObject):
    finished = pyqtSignal(str)

    def run(self):
        """Long-running task - 1 - play sample."""

        if 999 < sampling_rate < 100001 and num_samples and amp and frequency != 0:
            start_time = time.time()
            global sucess, over
            samples = numpy.array([numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) * amp for x in
                                   range(num_samples)]).astype(numpy.float32).tobytes()

            stream = p.open(format=pyaudio.paFloat32,
                            channels=num_channels,
                            rate=sampling_rate,
                            output=True,
                            )

            stream.write(samples)
            # print(stream.get_time())
            # print(" %s seconds " % round((time.time() - start_time), 4))

            stream.stop_stream()

            stream.close()
            sucess = True
            over = True

            self.finished.emit(str(" %s seconds " % round((time.time() - start_time), 4)))

        else:
            sucess = False
            over = True
            self.finished.emit('The <b>sampling rate</b> should have a value between 1000 and 100000'
                               ' and <b>all of the values should be different from 0</b>.')


class WorkerI(QObject):
    finished = pyqtSignal(str)

    def run(self):
        """Long-running task - 2 - play sound."""

        if 999 < sampling_rate < 100001 and num_samples and amp != 0:
            global sucess, over

            start_time = time.time()

            full_wave = []

            for i in values_list_comp:
                frequency = i * fq_mod

                sine_wave = [numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) * amp for x in
                             range(num_samples)]
                full_wave.extend(sine_wave)

            samples = numpy.array(full_wave).astype(numpy.float32).tobytes()
            # print(samples)

            stream = p.open(format=pyaudio.paFloat32,
                            channels=num_channels,
                            rate=sampling_rate,
                            output=True,
                            )
            stream.write(samples)
            stream.stop_stream()

            stream.close()

            sucess = True
            over = True

            self.finished.emit(str(" %s seconds " % round((time.time() - start_time), 4)))
            # p.terminate()
        else:
            sucess = False
            over = True
            self.finished.emit('The <b>sampling rate</b> should have a value between 1000 and 100000'
                               ' and <b>all of the values should be different from 0</b>.')


class ImageToSoundUi(object):
    def __init__(self):
        super(ImageToSoundUi, self).__init__()

        imageToSound.setObjectName("imageToSound")
        imageToSound.resize(952, 670)
        # TODO: ADD ICON
        imageToSound.setWindowIcon(QIcon('icon-last-01.png'))

        self.centralwidget = QtWidgets.QWidget(imageToSound)
        self.centralwidget.setStyleSheet(darkstylesheet)

        # DARK MODE button
        self.dark_button = QtWidgets.QPushButton(self.centralwidget)
        self.dark_button.setGeometry(QtCore.QRect(830, 5, 113, 32))
        self.dark_button.clicked.connect(self.dark_mode)

        # Load image
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 5, 113, 32))
        self.pushButton.clicked.connect(self.get_image_data)

        self.prevLabel = QtWidgets.QLabel(self.centralwidget)
        self.prevLabel.setGeometry(QtCore.QRect(10, 42, 60, 16))

        self.imagePrev = QtWidgets.QLabel(self.centralwidget)
        self.imagePrev.setGeometry(QtCore.QRect(10, 60, 121, 181))

        # Image data
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 310, 121, 16))

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 330, 60, 16))

        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 350, 71, 16))

        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(10, 370, 71, 16))

        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 390, 71, 16))

        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(10, 410, 71, 16))

        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(10, 440, 121, 16))

        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(10, 480, 101, 16))

        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(10, 530, 101, 16))

        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(10, 590, 101, 16))

        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(10, 610, 111, 16))

        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(10, 255, 121, 16))

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 280, 104, 26))

        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.activated.connect(self.calculate_freq)

        # PLOTS

        self.graphicsView_2 = pg.PlotWidget(self.centralwidget)
        self.graphicsView_2.setBackground((10, 10, 15))
        self.graphicsView_2.setGeometry(QtCore.QRect(140, 10, 411, 131))
        styles = {"font-size": "10px", "color": "gray"}
        self.graphicsView_2.setLabel("left", "Pixels value: <br> (0-255)", **styles)

        self.graphicsView_3 = pg.PlotWidget(self.centralwidget)
        self.graphicsView_3.setBackground((10, 10, 15))
        self.graphicsView_3.setGeometry(QtCore.QRect(140, 150, 411, 131))
        self.graphicsView_3.setLabel("left", "Wave<br> frequency", **styles)

        self.graphicsView_4 = pg.PlotWidget(self.centralwidget)
        self.graphicsView_4.setBackground((10, 10, 15))
        self.graphicsView_4.setGeometry(QtCore.QRect(140, 440, 791, 141))
        self.graphicsView_4.setLabel("left", "Volume <br> (amplitude)", **styles)

        self.graphicsView_5 = pg.PlotWidget(self.centralwidget)
        self.graphicsView_5.setBackground((10, 10, 15))
        self.graphicsView_5.setGeometry(QtCore.QRect(550, 150, 381, 131))
        self.graphicsView_5.setLabel("left", "Volume <br> (amplitude)", **styles)

        # Buttons - save / play

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(700, 600, 113, 32))
        self.pushButton_2.clicked.connect(self.play_sound)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(820, 600, 113, 32))
        self.pushButton_3.clicked.connect(self.save_sound)

        # Labels
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(140, 320, 111, 16))

        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(140, 370, 111, 16))

        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(270, 320, 111, 16))

        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(270, 370, 111, 16))

        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(400, 340, 104, 26))

        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")

        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(400, 320, 111, 16))

        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(400, 390, 104, 26))
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")

        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setGeometry(QtCore.QRect(400, 370, 111, 16))

        self.label_20 = QtWidgets.QLabel(self.centralwidget)
        self.label_20.setGeometry(QtCore.QRect(570, 10, 121, 16))

        self.label_22 = QtWidgets.QLabel(self.centralwidget)
        self.label_22.setGeometry(QtCore.QRect(570, 90, 111, 16))

        self.label_23 = QtWidgets.QLabel(self.centralwidget)
        self.label_23.setGeometry(QtCore.QRect(570, 40, 111, 16))

        self.label_24 = QtWidgets.QLabel(self.centralwidget)
        self.label_24.setGeometry(QtCore.QRect(700, 40, 111, 16))

        self.label_25 = QtWidgets.QLabel(self.centralwidget)
        self.label_25.setGeometry(QtCore.QRect(700, 90, 111, 16))

        self.label_26 = QtWidgets.QLabel(self.centralwidget)
        self.label_26.setGeometry(QtCore.QRect(830, 40, 111, 16))

        self.label_21 = QtWidgets.QLabel(self.centralwidget)
        self.label_21.setGeometry(QtCore.QRect(520, 320, 111, 16))

        self.label_27 = QtWidgets.QLabel(self.centralwidget)
        self.label_27.setGeometry(QtCore.QRect(830, 90, 111, 16))

        self.label_28 = QtWidgets.QLabel(self.centralwidget)
        self.label_28.setGeometry(QtCore.QRect(300, 645, 171, 16))

        self.label_29 = QtWidgets.QLabel(self.centralwidget)
        self.label_29.setGeometry(QtCore.QRect(140, 300, 121, 16))

        self.label_31 = QtWidgets.QLabel(self.centralwidget)
        self.label_31.setGeometry(QtCore.QRect(10, 550, 101, 16))

        self.label_32 = QtWidgets.QLabel(self.centralwidget)
        self.label_32.setGeometry(QtCore.QRect(10, 500, 101, 16))

        # LINE EDITS - FULL WAVE

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setValidator(QIntValidator())
        self.lineEdit.setText('10')
        self.lineEdit.setGeometry(QtCore.QRect(140, 340, 113, 21))
        self.lineEdit.textChanged.connect(self.vis_sound)

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setValidator(QDoubleValidator())
        self.lineEdit_2.setText('1')
        self.lineEdit_2.setGeometry(QtCore.QRect(270, 340, 113, 21))
        self.lineEdit_2.textChanged.connect(self.vis_sound)

        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setValidator(QIntValidator())
        self.lineEdit_3.setGeometry(QtCore.QRect(520, 340, 113, 21))
        self.lineEdit_3.setText('32000')
        self.lineEdit_3.textChanged.connect(self.vis_sound)

        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_4.setValidator(QIntValidator())
        self.lineEdit_4.setGeometry(QtCore.QRect(270, 390, 113, 21))
        self.lineEdit_4.setText('2')
        self.lineEdit_4.textChanged.connect(self.vis_sound)

        self.lineEdit_5 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_5.setValidator(QIntValidator())
        self.lineEdit_5.setGeometry(QtCore.QRect(140, 390, 113, 21))
        self.lineEdit_5.setText('44000')
        self.lineEdit_5.textChanged.connect(self.vis_sound)

        # SINE SAMPLER
        self.comboBox_4 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_4.setGeometry(QtCore.QRect(830, 60, 104, 26))
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")

        self.lineEdit_6 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_6.setValidator(QIntValidator())
        self.lineEdit_6.setText('44000')
        self.lineEdit_6.setGeometry(QtCore.QRect(570, 110, 113, 21))
        self.lineEdit_6.textChanged.connect(self.make_sine_sample)

        self.lineEdit_7 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_7.setValidator(QIntValidator())
        self.lineEdit_7.setText('10000')
        self.lineEdit_7.setGeometry(QtCore.QRect(570, 60, 113, 21))
        self.lineEdit_7.textChanged.connect(self.make_sine_sample)

        self.lineEdit_8 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_8.setValidator(QIntValidator())
        self.lineEdit_8.setText('200')
        self.lineEdit_8.setGeometry(QtCore.QRect(700, 60, 113, 21))
        self.lineEdit_8.textChanged.connect(self.make_sine_sample)

        self.lineEdit_9 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_9.setValidator(QIntValidator())
        self.lineEdit_9.setText('1')
        self.lineEdit_9.setGeometry(QtCore.QRect(700, 110, 113, 21))
        self.lineEdit_9.textChanged.connect(self.make_sine_sample)

        self.lineEdit_10 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_10.setValidator(QIntValidator())
        self.lineEdit_10.setText('32000')
        self.lineEdit_10.setGeometry(QtCore.QRect(830, 110, 113, 21))
        self.lineEdit_10.textChanged.connect(self.make_sine_sample)

        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(700, 300, 113, 32))
        self.pushButton_5.clicked.connect(self.play_sample)

        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(820, 300, 113, 32))
        self.pushButton_6.clicked.connect(self.save_sample)

        # TODO: Change position of how to button

        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(702, 350, 228, 32))
        self.pushButton_7.clicked.connect(self.how_to)

        imageToSound.setCentralWidget(self.centralwidget)

        self.set_texts(imageToSound)
        self.make_sine_sample()
        self.get_image_data('/Users/Y-S/Desktop/i2s/100x167.jpg')

        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.setStyleSheet(darkstylesheet)
        self.error_dialog.setWindowTitle("Value Error!")


        self.info_dialog = QtWidgets.QMessageBox()
        self.info_dialog.setStyleSheet("background-color:rgb(30,30,40);color: whitesmoke")
        self.info_dialog.setWindowTitle("How to use?")

        self.save_dialog = QtWidgets.QErrorMessage()
        self.save_dialog.setStyleSheet(darkstylesheet)
        self.save_dialog.setWindowTitle("Sound saved!")

        self.progress_bar = QProgressBar(self.centralwidget)

        self.progress_bar.setGeometry(QtCore.QRect(140, 605, 540, 23))

        # TODO: Add github repo link

    def set_texts(self, imageToSound):

        imageToSound.setWindowTitle("Image to Sound Converter")

        self.dark_button.setText("light mode")
        self.pushButton.setText("Load image")
        self.prevLabel.setText("Preview:")

        self.label_2.setText("Image data:")
        self.label_2.setStyleSheet("font-weight:bold;")

        self.label_3.setText("size:")
        self.label_4.setText("no. pixels:")
        self.label_5.setText("avg. R:")
        self.label_6.setText("avg. G:")
        self.label_7.setText("avg. B:")

        self.label_8.setText("Sound data:")
        self.label_8.setStyleSheet("font-weight:bold;")

        self.label_9.setText("no. sine waves:")
        self.label_10.setText("avg. frequency:")
        self.label_11.setText("duration:")
        self.label_12.setText("")
        self.comboBox.setItemText(0, "horizontal")
        self.comboBox.setItemText(1, "vertical")

        self.label_13.setText("Conversion mode:")
        self.label_13.setStyleSheet("font-size: 13px;font-weight:bold;")

        self.pushButton_2.setText("play sound")
        self.pushButton_3.setText("save sound")
        self.label_14.setText("samples per wave:")
        self.label_15.setText("sampling rate:")
        self.label_16.setText("freq. modifier:")
        self.label_17.setText("volume (playback):")

        self.label_18.setText("no. channels:")
        self.comboBox_2.setItemText(0, "2")
        self.comboBox_2.setItemText(1, "1")

        self.label_19.setText("sample width:")
        self.comboBox_3.setItemText(0, "2")
        self.comboBox_3.setItemText(1, "1")
        self.comboBox_3.setItemText(2, "3")
        self.comboBox_3.setItemText(3, "4")

        self.label_20.setText("Sine wave sampler:")
        self.label_20.setStyleSheet("font-size: 13px;font-weight:bold;")

        self.label_26.setText("no. channels:")
        self.comboBox_4.setItemText(0, "2")
        self.comboBox_4.setItemText(1, "1")

        self.label_22.setText("sampling rate:")
        self.label_23.setText("no. samples:")
        self.label_24.setText("frequency:")
        self.label_25.setText("volume (playback):")

        self.pushButton_5.setText("play sample")
        self.pushButton_6.setText("save sample")
        self.label_21.setText("amplitude (save):")
        self.label_27.setText("amplitude (save):")

        self.label_28.setText("Image to Sound Converter by Georgios Lazaridis© All rights reserved.")
        self.label_28.setStyleSheet("font-size: 9px;")
        self.label_28.adjustSize()

        self.label_29.setText("Sound modifiers:")
        self.label_29.setStyleSheet("font-size: 13px;font-weight:bold;")

        self.pushButton_7.setText("how to use?")

    # Functionality
    def how_to(self):
        # TODO: Add how to information text
        self.info_dialog.setText('A lot of you will ask the question how to and why to use this program?'
                                 ' Is it even fun?')
        self.info_dialog.setIcon(QMessageBox.Question)
        self.info_dialog.setWindowIcon(QIcon('icon-last-01.png'))
        self.info_dialog.exec_()

    def dark_mode(self):
        if self.dark_button.text() == "dark mode":
            self.centralwidget.setStyleSheet(darkstylesheet)

            self.graphicsView_2.setBackground((10, 10, 15))
            self.graphicsView_3.setBackground((10, 10, 15))
            self.graphicsView_5.setBackground((10, 10, 15))
            self.graphicsView_4.setBackground((10, 10, 15))

            self.error_dialog.setStyleSheet(darkstylesheet)
            # TODO: ADD style to info box
            self.info_dialog.setStyleSheet("background-color:rgb(30,30,40);color: whitesmoke")

            self.dark_button.setText("light mode")
        else:
            self.centralwidget.setStyleSheet(lightstylesheet)

            self.graphicsView_4.setBackground('w')
            self.graphicsView_2.setBackground('w')
            self.graphicsView_3.setBackground('w')
            self.graphicsView_5.setBackground('w')

            self.error_dialog.setStyleSheet(lightstylesheet)
            # TODO: ADD style to info box
            self.info_dialog.setStyleSheet("font-weight:bold;")

            self.dark_button.setText("dark mode")

    def get_image_data(self, filename):
        global name
        if not filename:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getOpenFileName(self.centralwidget, "Choose your image", "",
                                                      "Image Files (*.jpg *.gif *.png *.jpeg *.bmp)", options=options)
        if filename:
            # print(filename)
            self.imagePrev.setPixmap(QPixmap(filename).scaledToWidth(111))
            name = filename
        if filename != '':
            img = Image.open(filename)
            width, height = img.size

            xaxis = range(len(img.getdata(0)))
            R1 = list(img.getdata(0))
            G1 = list(img.getdata(1))
            B1 = list(img.getdata(2))

            self.graphicsView_2.clear()
            self.plot_rgb(xaxis, R1, "red", 'r')
            self.plot_rgb(xaxis, G1, "green", 'g')
            self.plot_rgb(xaxis, B1, "blue", 'b')

            styles = {"font-size": "10px", "color": "gray", "margin-top": "-10px"}
            self.graphicsView_2.setLabel("bottom", "Number of pixels: " + str(width * height), **styles)

            self.label_3.setText("size: " + str(width) + " x " + str(height))
            self.label_4.setText("no. pixels: " + str(width * height))
            self.label_5.setText("avg. R: " + str(average(R1)))
            self.label_6.setText("avg. G: " + str(average(G1)))
            self.label_7.setText("avg. B: " + str(average(B1)))

            self.label_3.adjustSize()
            self.label_4.adjustSize()
            self.label_5.adjustSize()
            self.label_6.adjustSize()
            self.label_7.adjustSize()

            self.calculate_freq()

    def calculate_freq(self):
        global values_list_comp
        img = Image.open(name)

        styles = {"font-size": "10px", "color": "gray", "margin-top": "-10px"}

        width, height = img.size

        R1 = list(img.getdata(0))
        G1 = list(img.getdata(1))
        B1 = list(img.getdata(2))

        # sinus waves data
        x = []
        y = []
        z = []

        # Conversion mode - scan rows or columns for average pixel values

        if self.comboBox.currentText() == "horizontal":
            r = zip(*[iter(R1)] * width)
            g = zip(*[iter(G1)] * width)
            b = zip(*[iter(B1)] * width)
            self.label_32.setText(str(height * 3))
            self.graphicsView_3.setLabel("bottom", "Number of sine waves: " + str(height * 3), **styles)

        elif self.comboBox.currentText() == "vertical":
            r = zip(*[iter(R1)] * height)
            g = zip(*[iter(G1)] * height)
            b = zip(*[iter(B1)] * height)
            self.label_32.setText(str(width * 3))
            self.graphicsView_3.setLabel("bottom", "Number of sine waves: " + str(width * 3), **styles)

        x.extend(list(r))
        y.extend(list(g))
        z.extend(list(b))

        r_avg = []
        g_avg = []
        b_avg = []

        for i in x:
            r_avg.append(int(average(i)))

        for i in y:
            g_avg.append(int(average(i)))

        for i in z:
            b_avg.append(int(average(i)))

        comp = []

        comp.extend(list(zip(r_avg, g_avg, b_avg)))

        values_list_comp = [x for sets in comp for x in sets]  # flatten the list

        self.label_31.setText(str(average(values_list_comp)))
        self.graphicsView_3.clear()
        self.plot_avgs(values_list_comp, "samples avg. freq", (117, 113, 244))

        self.vis_sound()

    def vis_sound(self):
        global full_wave, fq_mod, sampling_rate, num_samples, amp
        if self.lineEdit_2.text() and self.lineEdit_5.text() and self.lineEdit.text() and self.lineEdit_4.text() != '':

            fq_mod = float(self.lineEdit_2.text())
            sampling_rate = int(self.lineEdit_5.text())
            num_samples = int(self.lineEdit.text())
            amp = int(self.lineEdit_4.text())

            if 999 < sampling_rate < 100001 and num_samples and amp != 0:
                self.graphicsView_4.clear()

                full_wave = []
                for i in values_list_comp:
                    frequency = i * fq_mod
                    sine_wave = [numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) * amp for x in
                                 range(num_samples)]
                    full_wave.extend(sine_wave)

                self.plot_full(full_wave, "full sound", (117, 113, 244))
                styles = {"font-size": "10px", "color": "gray", "margin-top": "-10px"}
                self.graphicsView_4.setLabel("bottom", "number of samples: " + str(len(full_wave)), **styles)

            else:
                self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                              ' and <b>all of the values should be different from 0</b>.')

    def plot_rgb(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphicsView_2.plot(x, y, name=plotname, pen=pen)

    def plot_avgs(self, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphicsView_3.plot(y, name=plotname, pen=pen)

    def plot_full(self, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphicsView_4.plot(y, name=plotname, pen=pen)

    def plot_sampler(self, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphicsView_5.plot(y, name=plotname, pen=pen)

    def make_sine_sample(self):
        global frequency, sampling_rate, num_samples, amp
        if self.lineEdit_8.text() and self.lineEdit_6.text() and self.lineEdit_7.text() and self.lineEdit_9.text() != '':

            frequency = int(self.lineEdit_8.text())
            sampling_rate = int(self.lineEdit_6.text())
            num_samples = int(self.lineEdit_7.text())
            amp = int(self.lineEdit_9.text())
            self.graphicsView_5.clear()

            if 999 < sampling_rate < 100001 and num_samples and amp and frequency != 0:
                sine_wave = [numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) * amp for x in
                             range(num_samples)]

                self.plot_sampler(sine_wave, "single sample", (117, 113, 244))
                styles = {"font-size": "10px", "color": "gray", "margin-top": "-10px"}
                self.graphicsView_5.setLabel("bottom", "number of samples: " + str(num_samples), **styles)

            else:
                self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                              ' and <b>all of the values should be different from 0</b>.')
        else:
            self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                          ' and <b>all of the values should be different from 0</b>.')

    def reportprogress(self, n):
        self.progress_bar.setValue(n)

    def rendertime(self, n):
        if sucess:
            self.label_12.setText(n)
            self.label_12.adjustSize()
        else:
            self.error_dialog.showMessage(n)

    def enablebuttons(self):
        self.pushButton_2.setEnabled(True)
        self.pushButton_5.setEnabled(True)

    def play_sample(self):
        global frequency, sampling_rate, num_samples, amp, num_channels, over, sucess

        if self.lineEdit_8.text() and self.lineEdit_6.text() and self.lineEdit_7.text() and self.lineEdit_9.text() != '':

            over = False
            sucess = False

            self.pushButton_5.setEnabled(False)
            self.pushButton_2.setEnabled(False)

            frequency = int(self.lineEdit_8.text())
            sampling_rate = int(self.lineEdit_6.text())
            num_samples = int(self.lineEdit_7.text())
            amp = int(self.lineEdit_9.text())
            num_channels = int(self.comboBox_4.currentText())

            self.progress_bar.setRange(0, num_samples)
            self.progress_bar.setValue(0)

            # Setup QThread workers
            self.thread = QThread()
            self.thread2 = QThread()

            self.worker = Worker()
            self.worker2 = ProgressBar()

            # Step 1: Move worker to the thread
            self.worker.moveToThread(self.thread)
            self.worker2.moveToThread(self.thread2)

            # Step 2: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.thread2.started.connect(self.worker2.run)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.thread.wait)

            self.worker2.finished.connect(self.thread2.quit)
            self.worker2.finished.connect(self.worker2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)
            self.thread2.finished.connect(self.thread2.wait)

            self.worker2.progress.connect(self.reportprogress)
            self.worker.finished.connect(self.rendertime)

            # Step 6: Start the thread
            self.thread.start()
            self.thread2.start()

            # display timing
            # reset progress bar and button

            self.thread.finished.connect(self.enablebuttons)

            # p.terminate()
        else:
            self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                          ' and <b>all of the values should be different from 0</b>.')

    def save_sample(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self.centralwidget, "Save sample", "sample.wav",
                                                  "Wave file (*.wav)", options=options)
        if filename and self.lineEdit_8.text() and self.lineEdit_6.text() and self.lineEdit_7.text() and self.lineEdit_9.text() != '':
            # print(filename)
            start_time = time.time()
            frequency = int(self.lineEdit_8.text())
            sampling_rate = int(self.lineEdit_6.text())
            num_samples = int(self.lineEdit_7.text())
            amp = int(self.lineEdit_10.text())
            num_channels = int(self.comboBox_4.currentText())

            sampwidth = int(self.comboBox_3.currentText())

            imageToSound.setWindowTitle("Image to Sound Converter - saving sample...")

            if 999 < sampling_rate < 100001 and num_samples and amp and frequency != 0:
                wav_file = wave.open(filename, 'w')
                wav_file.setparams((num_channels, sampwidth, sampling_rate,
                                    num_samples, comptype, compname))

                sine_wave = [numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) for x in
                             range(num_samples)]
                # print(sine_wave)

                for s in sine_wave:
                    wav_file.writeframes(struct.pack('h', int(s * amp)))

                # print("--- %s seconds ---" % (time.time() - start_time))

                self.save_dialog.showMessage("Sample saved in " + " %s seconds " % round((time.time() - start_time), 4))

            imageToSound.setWindowTitle("Image to Sound Converter")

    def play_sound(self):
        global frequency, sampling_rate, num_samples, amp, num_channels, fq_mod, over, sucess

        if self.lineEdit_2.text() and self.lineEdit_5.text() and self.lineEdit.text() and self.lineEdit_4.text() != '':

            over = False
            sucess = False

            self.pushButton_2.setEnabled(False)
            self.pushButton_5.setEnabled(False)

            fq_mod = float(self.lineEdit_2.text())
            sampling_rate = int(self.lineEdit_5.text())
            num_samples = int(self.lineEdit.text())
            amp = int(self.lineEdit_4.text())
            num_channels = int(self.comboBox_2.currentText())

            self.progress_bar.setRange(0, num_samples)
            self.progress_bar.setValue(0)

            # Setup QThread workers
            self.thread = QThread()
            self.thread2 = QThread()

            self.worker = WorkerI()
            self.worker2 = ProgressBarI()

            # Step 1: Move worker to the thread
            self.worker.moveToThread(self.thread)
            self.worker2.moveToThread(self.thread2)

            # Step 2: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.thread2.started.connect(self.worker2.run)

            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.thread.wait)

            self.worker2.finished.connect(self.thread2.quit)
            self.worker2.finished.connect(self.worker2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)
            self.thread2.finished.connect(self.thread2.wait)

            self.worker2.progress.connect(self.reportprogress)
            self.worker.finished.connect(self.rendertime)

            # Start the threads
            self.thread.start()
            self.thread2.start()

            # reset button

            self.thread.finished.connect(self.enablebuttons)

        else:
            self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                          ' and <b>all of the values should be different from 0</b>.')

    def save_sound(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getSaveFileName(self.centralwidget, "Save sound", "sound.wav",
                                                   "Wave file (*.wav)", options=options)
        if fileNames and self.lineEdit_2.text() and self.lineEdit_5.text() and self.lineEdit.text() and self.lineEdit_4.text() != '':

            imageToSound.setWindowTitle("Image to Sound Converter - saving sound...")

            fq_mod = float(self.lineEdit_2.text())
            sampling_rate = int(self.lineEdit_5.text())
            num_samples = int(self.lineEdit.text())
            amp = int(self.lineEdit_3.text())
            num_channels = int(self.comboBox_2.currentText())

            sampwidth = int(self.comboBox_3.currentText())

            if 999 < sampling_rate < 100001 and num_samples and amp != 0:
                start_time = time.time()

                wav_file = wave.open(fileNames, 'w')
                wav_file.setparams((num_channels, sampwidth, sampling_rate,
                                    num_samples, comptype, compname))
                full_wave = []
                for i in values_list_comp:
                    frequency = i * fq_mod

                    sine_wave = [numpy.sin(2 * numpy.pi * frequency * x / sampling_rate) for x in
                                 range(num_samples)]
                    full_wave.extend(sine_wave)

                for s in full_wave:
                    wav_file.writeframes(struct.pack('h', int(s * amp)))
                # print("--- %s seconds ---" % (time.time() - start_time))
                self.save_dialog.showMessage("Sound saved in " + " %s seconds " % round((time.time() - start_time), 4))

                imageToSound.setWindowTitle("Image to Sound Converter")

            else:
                self.error_dialog.showMessage('The <b>sampling rate</b> should have a value between 1000 and 100000'
                                              ' and <b>all of the values should be different from 0</b>.')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # print(PyQt5.QtWidgets.QStyleFactory.keys())
    app.setStyle("Fusion")
    imageToSound = QtWidgets.QMainWindow()
    ui = ImageToSoundUi()
    imageToSound.show()
    sys.exit(app.exec_())
