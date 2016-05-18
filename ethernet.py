# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ethernet.ui'
#
# Created: Mon Jan 18 16:33:27 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!
import struct

import time

from cStringIO import StringIO
from PySide import QtCore, QtGui
import sys
import socket
import binascii
import numpy as np
import os

OFF = "OFF"
ON = "ON"

relay0status = OFF
eik_running_status = OFF

file = ""

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context,text)

class Ui_Form(QtGui.QWidget):
    BITE_IP = '192.168.1.33'
    BITE_PORT = 2223    
    signal = QtCore.Signal(str)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
    def setupUi(self,Form):
        global temperatureValue
        Form.setObjectName("Form")
        Form.resize(500, 200)
        hbox = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        topHbox = QtGui.QHBoxLayout()
        adcVbox = QtGui.QVBoxLayout()

        #Font
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        #Set up large label that displays temperature and humidity
        self.temperatureTextView = QtGui.QLabel()
        self.temperatureTextView.setText(str("#1 T:"))
        self.temperatureTextView.setFont(font)
        self.humidityTextView = QtGui.QLabel()
        self.humidityTextView.setText(str("#1 H:"))
        self.humidityTextView.setFont(font)
        self.humidityTextView2 = QtGui.QLabel()
        self.humidityTextView2.setText(str("#2 H:"))
        self.humidityTextView2.setFont(font)
        self.temperatureTextView2 = QtGui.QLabel()
        self.temperatureTextView2.setText(str("#2 T:"))
        self.temperatureTextView2.setFont(font)
        self.humidityTextView3 = QtGui.QLabel()
        self.humidityTextView3.setText(str("#3 H:"))
        self.humidityTextView3.setFont(font)
        self.temperatureTextView3 = QtGui.QLabel()
        self.temperatureTextView3.setText(str("#3 T:"))
        self.temperatureTextView3.setFont(font)

        #Set up Operation status text view
        self.opStatusTextView = QtGui.QLabel()
        self.opStatusTextView.setText(str("OP STATUS:"))
        self.opStatusTextView.setFont(font)

        #ADC Status Text view
        self.ADC1AstatusTextView = QtGui.QLabel()
        self.ADC1AstatusTextView.setText(str("ADC1A STATUS"))
        self.ADC1AstatusTextView.setFont(font)
        self.ADC2AstatusTextView = QtGui.QLabel()
        self.ADC2AstatusTextView.setText(str("ADC2A STATUS"))
        self.ADC2AstatusTextView.setFont(font)
        self.ADC3AstatusTextView = QtGui.QLabel()
        self.ADC3AstatusTextView.setText(str("ADC3A STATUS"))
        self.ADC3AstatusTextView.setFont(font)

        #EIK Operation status text view
        self.EIKStatusTextView = QtGui.QLabel()
        self.EIKStatusTextView.setText(str("mod_fault: xmtr_temp: sync_fault: pwr_valid: fil_delay: fault_sum: "))
        self.EIKStatusTextView.setFont(font)

        #Relay 0 command button
        self.relay0 = QtGui.QPushButton(Form)
        self.relay0.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.relay0.setObjectName("relay0")

        #PWR MODR command button
        self.eik_start = QtGui.QPushButton(Form)
        self.eik_start.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.eik_start.setObjectName("eik_start_btn")

        #DDS Command button
        self.DDS1 = QtGui.QPushButton(Form)
        self.DDS1.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.DDS1.setObjectName("DDS1Button")

        #DDS Command button
        self.DDS2 = QtGui.QPushButton(Form)
        self.DDS2.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.DDS2.setObjectName("DDS2Button")

        #DDS Command button
        self.DDS1FileSelect = QtGui.QPushButton(Form)
        self.DDS1FileSelect.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.DDS1FileSelect.setObjectName("selectDDS1FileButton")

        #DDS Command button
        self.DDS2FileSelect = QtGui.QPushButton(Form)
        self.DDS2FileSelect.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.DDS2FileSelect.setObjectName("selectDDS2FileButton")

        #Start UDP server
        #Connect the thread signals to UI thread objects
        self.threadclass = ThreadClass()
        self.threadclass.start()
        self.threadclass.signalTemperature.connect(self.updateTemperature)
        self.threadclass.signalTemperature2.connect(self.updateTemperature2)
        self.threadclass.signalTemperature3.connect(self.updateTemperature3)
        self.threadclass.signalHumidity.connect(self.updateHumidity)
        self.threadclass.signalHumidity2.connect(self.updateHumidity2)
        self.threadclass.signalHumidity3.connect(self.updateHumidity3)
        self.threadclass.signalADC1A.connect(self.updateADC1AView)
        self.threadclass.signalADC2A.connect(self.updateADC2AView)
        self.threadclass.signalADC3A.connect(self.updateADC3AView)
        self.threadclass.signalEIKStatus.connect(self.updateEIKStatusView)

        vbox.addWidget(self.temperatureTextView)
        vbox.addWidget(self.temperatureTextView2)
        vbox.addWidget(self.temperatureTextView3)
        vbox.addWidget(self.humidityTextView)
        vbox.addWidget(self.humidityTextView2)
        vbox.addWidget(self.humidityTextView3)
        vbox.addWidget(self.opStatusTextView)
        vbox.addWidget(self.eik_start)
        topHbox.addLayout(vbox)
        topHbox.addLayout(adcVbox)
        adcVbox.addWidget(self.ADC1AstatusTextView)
        adcVbox.addWidget(self.ADC2AstatusTextView)
        adcVbox.addWidget(self.ADC3AstatusTextView)

        #hbox.addWidget(self.relay0)
        hbox.addWidget(self.DDS1)
        hbox.addWidget(self.DDS2)
        hbox2.addWidget(self.DDS1FileSelect)
        hbox2.addWidget(self.DDS2FileSelect)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox)
        vbox.addWidget(self.EIKStatusTextView)
        self.setLayout(topHbox)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("BITE Control panel", "BITE Command center", None, QtGui.QApplication.UnicodeUTF8))
        self.relay0.setText(str("Relay 0 OFF"))
        self.eik_start.setText(str("EIK START"))
        self.DDS1.setText(str("Upload -> DDS1"))
        self.DDS2.setText(str("Upload -> DDS2"))
        self.DDS1FileSelect.setText(str("Select DDS1 File"))
        self.DDS2FileSelect.setText(str("Select DDS2 File"))
        self.relay0.clicked.connect(self.relay0handler)
        self.eik_start.clicked.connect(self.eik_start_handler)
        self.DDS1.clicked.connect(self.uploadToDDS1)
        self.DDS2.clicked.connect(self.uploadToDDS2)
        self.DDS1FileSelect.clicked.connect(self.DDS1FileDialog)
        self.DDS2FileSelect.clicked.connect(self.DDS2FileDialog)
#       self.startUDPServer.setText(str("Start UDP Server"))
#       self.startUDPServer.clicked.connect(self.udpServer)

    def DDS1FileDialog(self):
        global file
        self.fileDialog = QtGui.QFileDialog(self)
        self.fileDialog.setWindowTitle('Select DDS1 config file')
        self.fileDialog.setDefaultSuffix('.bin')
        self.files = self.fileDialog.getOpenFileName(parent=self,
                                                     dir='C:\Users\jason\PycharmProjects\Ethernet GUI\Ethernet-controller-test-script')[0]
        file = self.files


    def DDS2FileDialog(self):
        global file
        self.fileDialog = QtGui.QFileDialog(self)
        self.fileDialog.setWindowTitle('Select DDS2 config file')
        self.fileDialog.setDefaultSuffix('.bin')
        self.files = self.fileDialog.getOpenFileName(parent=self, dir=os.getenv("HOME"))[0]
        file = self.files


    def eik_start_handler(self):
        global eik_running_status
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.BITE_IP, self.BITE_PORT));
        client.send("EIKASTART:");
        client.close();
        eik_running_status = "START INITIATED"
        
    def uploadToDDS1(self):
        global file
        #Debug variables
        reconstructed = ""

        print "Uploading to DDS #1"
        ddsFileName = file#'barker_code_13us_dds1.bin'
        print ddsFileName
        ddsFileStats = os.stat(ddsFileName)
        chunks = ddsFileStats.st_size/1024
        print "File will be split in", chunks
        ddsFile = open(ddsFileName, 'rb')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client_socket.setblocking(0)
        try:
            client_socket.connect(('192.168.1.32', 2223))
            #contents = ddsFile.read()
            #ddsFile = open(ddsFileName, 'rb')
            for i in range(0, chunks+1):
                ddsFileContent = ddsFile.read(1024)
                client_socket.send("DDS1:"+str(i)+":"+str(chunks+1)+":"+ddsFileContent)
                time.sleep(1)
                reconstructed += ddsFileContent
                print "Checksum: "+str(sum(bytearray(reconstructed)))

            startTime = time.time()
            while 1:
                if time.time()-startTime > 2:
                    break

                response =  client_socket.recv(20)
                self.opStatusTextView.setText(str("OPSTATUS: ")+response)
                break
            client_socket.close()

        except socket.error, (value, message):
            print "Error connecting. Please reset the board. Error message\n"+message

    def uploadToDDS2(self):
        global file
        #Debug variables
        reconstructed = ""

        print "Uploading to DDS #2"
        ddsFileName = file#'nlfm_5mhz_13us_dds1_ethernet_frame.bin'
        ddsFileStats = os.stat(ddsFileName)
        chunks = ddsFileStats.st_size/1024
        print "File will be split in", chunks
        ddsFile = open(ddsFileName, 'rb')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client_socket.setblocking(0)
        try:
            client_socket.connect(('192.168.1.32', 2223))
            #contents = ddsFile.read()
            #ddsFile = open(ddsFileName, 'rb')
            for i in range(0, chunks+1):
                ddsFileContent = ddsFile.read(1024)
                client_socket.send("DDS2:"+str(i)+":"+str(chunks+1)+":"+ddsFileContent)
                time.sleep(2)
                reconstructed += ddsFileContent
                print "Checksum: "+str(sum(bytearray(reconstructed)))

            startTime = time.time()
            while 1:
                if time.time()-startTime > 2:
                    break

            response =  client_socket.recv(20)
            self.opStatusTextView.setText(str("OPSTATUS: ")+response)
            client_socket.close()

        except socket.error, (value, message):
            print "Error connecting. Please reset the board. Error message\n"+message

    def relay0handler(self):
        global relay0status
        if relay0status == OFF:
            print("RELAY O ON")        
            self.relay0.setText(QtGui.QApplication.translate("Dialog", "Relay 0 ON", None, QtGui.QApplication.UnicodeUTF8))
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.BITE_IP, self.BITE_PORT));
            client.send("RELAY0_ON");
            client.close();
            relay0status = ON
        else:
            print("RELAY O OFF")        
            self.relay0.setText(QtGui.QApplication.translate("Dialog", "Relay 0 OFF", None, QtGui.QApplication.UnicodeUTF8))
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.BITE_IP, self.BITE_PORT));
            client.send("RELAY0_OFF");
            client.close()
            relay0status = OFF


    def updateTemperature(self, temperatureValue):
        self.temperatureTextView.setText("#1 T= "+temperatureValue+"C")

    def updateTemperature2(self, temperatureValue):
        self.temperatureTextView2.setText("#2 T= "+temperatureValue+"C")

    def updateTemperature3(self, temperatureValue):
        self.temperatureTextView3.setText("#3 T= "+temperatureValue+"C")

    def updateHumidity(self, humidityValue):
        self.humidityTextView.setText("#1 H= "+humidityValue+"%")

    def updateHumidity2(self, humidityValue):
        self.humidityTextView2.setText("#2 H= "+humidityValue+"%")

    def updateHumidity3(self, humidityValue):
        self.humidityTextView3.setText("#3 H= "+humidityValue+"%")

    def updateADC1AView(self, ADCValue):
        self.ADC1AstatusTextView.setText("ADC1A = "+ADCValue)

    def updateADC2AView(self, ADCValue):
        self.ADC2AstatusTextView.setText("ADC2A = "+ADCValue)

    def updateADC3AView(self, ADCValue):
        self.ADC3AstatusTextView.setText("ADC3A = "+ADCValue)

    def updateEIKStatusView(self, EIKStatusString):
        str("mod_fault: xmtr_temp: sync_fault: pwr_valid: fil_delay: fault_sum: ")
        self.EIKStatusTextView.setText(str("mod_fault: "+EIKStatusString[0]+"\nxmtr_temp: "+EIKStatusString[1]+"\nsync_fault: "+EIKStatusString[2]+"\npwr_valid: "+EIKStatusString[3]+"\nfil_delay: "+EIKStatusString[4]+"\nfault_sum: "+EIKStatusString[5]))

    
class ThreadClass(QtCore.QThread):

    signalTemperature = QtCore.Signal(str)
    signalTemperature2 = QtCore.Signal(str)
    signalTemperature3 = QtCore.Signal(str)
    signalHumidity = QtCore.Signal(str)
    signalHumidity2 = QtCore.Signal(str)
    signalHumidity3 = QtCore.Signal(str)
    signalADC1A = QtCore.Signal(str)
    signalADC2A = QtCore.Signal(str)
    signalADC3A = QtCore.Signal(str)
    signalEIKStatus = QtCore.Signal(str)

    def __init__(self, parent = None):
        super(ThreadClass, self).__init__(parent)
        
    def run(self):
        while 1:
            HOST = ''   # Symbolic name meaning all available interfaces
            PORT = 2222 # Arbitrary non-privileged port
            
            f = open('BITE_LOG.txt', 'a')
            
            # Datagram (udp) socket
            try :
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print ('Socket created')
            except socket.error as msg :
                print ('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()
             
             
            # Bind socket to local host and port
            try:
                s.bind((HOST, PORT))
            except socket.error as msg:
                print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                sys.exit()
                 
            print ('Socket bind complete')
             
            #now keep talking with the client
            while 1:
                # receive data from client (data, addr)
                d = s.recvfrom(2222)
                data = binascii.hexlify(d[0])
                #print data

                i=0
                j=0
                split_data = [data[i:i+4] for i in range(0, len(data), 4)]
                #print split_data

                for byte in range(0, 8):

                    if split_data[byte][:2] == '80':
                        humidityValue1 = split_data[byte][2:4]
                        self.signalHumidity.emit(str(int(str(humidityValue1), 16)))
                    elif split_data[byte][:2] == '90':
                        temperatureValue1 = split_data[byte][2:4]
                        self.signalTemperature.emit(str(int(str(temperatureValue1), 16)))
                        #print split_data[byte]
                    elif split_data[byte][:2] == 'a0':
                        humidityValue2 = split_data[byte][2:4]
                        #print split_data[byte][0]
                        self.signalHumidity2.emit(str(int(str(humidityValue2), 16)))
                    elif split_data[byte][:2] == 'b0':
                        temperatureValue2 = split_data[byte][2:4]
                        self.signalTemperature2.emit(str(int(str(temperatureValue2), 16)))
                    elif split_data[byte][:2] == 'c0':
                        humidityValue3 = split_data[byte][2:4]
                        #print humidityValue3
                        self.signalHumidity3.emit(str(int(str(humidityValue3), 16)))
                    elif split_data[byte][:2] == 'd0':
                        temperatureValue3 = split_data[byte][2:4]
                        self.signalTemperature3.emit(str(int(str(temperatureValue3), 16)))
                    elif split_data[byte][:2] == '10':
                        ADC1AValue = split_data[byte][2:4]
                        self.signalADC1A.emit(str(int(str(ADC1AValue), 16)))
                    elif split_data[byte][:2] == '30':
                        ADC2AValue = split_data[byte][2:4]
                        self.signalADC2A.emit(str(int(str(ADC2AValue), 16)))
                    elif split_data[byte][:2] == '60':
                        ADC3AValue = split_data[byte][2:4]
                        self.signalADC3A.emit(str(int(str(ADC3AValue), 16)))
                    elif split_data[byte][:2] == '70':
                        EIKStatusBinaryString = split_data[byte][2:4]
                        EIKBinary = format(int(str(EIKStatusBinaryString), 16), '08b')
                        self.signalEIKStatus.emit(EIKBinary)


                    #print split_data[byte]
                #print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data + '\n'
                #f.write('' + data + '\n')
                
            s.close()
            f.close()
        
        
if __name__ == '__main__':
    try:
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()
    ex = Ui_Form()
    ex.show()
    sys.exit(app.exec_())
