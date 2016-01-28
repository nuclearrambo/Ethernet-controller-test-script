# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ethernet.ui'
#
# Created: Mon Jan 18 16:33:27 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!
import struct

import time
from PySide import QtCore, QtGui
import sys
import socket
import binascii
import os

OFF = "OFF"
ON = "ON"

relay0status = OFF

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
    BITE_IP = '192.168.1.32'
    BITE_PORT = 2223    
    signal = QtCore.Signal(str)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
    def setupUi(self,Form):
        global temperatureValue
        Form.setObjectName("Form")
        Form.resize(300, 150)
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()    

        #Font
        font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        #Set up large label that displays temperature and humidity
        self.temperatureTextView = QtGui.QLabel()
        self.temperatureTextView.setText(str("#1 T:"))
        self.temperatureTextView.setFont(font)
        self.humidityTextView = QtGui.QLabel()
        self.humidityTextView.setText(str("#1 H:"))
        self.humidityTextView.setFont(font)

        #Relay 0 command button
        self.relay0 = QtGui.QPushButton(Form)
        self.relay0.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.relay0.setObjectName("relay0")

        #DDS Command button
        self.DDS1 = QtGui.QPushButton(Form)
        self.DDS1.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.DDS1.setObjectName("DDS1Button")

        #Start UDP server
        self.threadclass = ThreadClass()
        self.threadclass.start()
        self.threadclass.signalTemperature.connect(self.updateTemperature)
        self.threadclass.signalHumidity.connect(self.updateHumidity)

        vbox.addWidget(self.temperatureTextView)
        vbox.addWidget(self.humidityTextView)
        hbox.addWidget(self.relay0)
        hbox.addWidget(self.DDS1)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("BITE Control panel", "BITE Command center", None, QtGui.QApplication.UnicodeUTF8))
        self.relay0.setText(str("Relay 0 OFF"))
        self.DDS1.setText(str("Upload -> DDS1"))
        self.relay0.clicked.connect(self.relay0handler)
        self.DDS1.clicked.connect(self.uploadToDDS1)
        
#       self.startUDPServer.setText(str("Start UDP Server"))
#       self.startUDPServer.clicked.connect(self.udpServer)
        
    def uploadToDDS1(self):
        #Debug variables
        reconstructed = ""

        print "Uploading to DDS #1"
        ddsFileName = 'nlfm_DDS_13us_5MHz.bin'
        ddsFileStats = os.stat(ddsFileName)
        chunks = ddsFileStats.st_size/1024
        print "File will be split in", chunks
        ddsFile = open(ddsFileName, 'rb')
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(('192.168.1.32', 2223))
            #contents = ddsFile.read()
            #ddsFile = open(ddsFileName, 'rb')
            for i in range(0, chunks+1):
                ddsFileContent = ddsFile.read(1024)
                client_socket.send("DDS1:"+str(i)+":"+str(chunks+1)+":"+ddsFileContent)
                time.sleep(0.5)
                reconstructed += ddsFileContent
                print "Checksum: "+str(sum(bytearray(reconstructed)))
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

    def updateHumidity(self, humidityValue):
        self.humidityTextView.setText("#1 H= "+humidityValue+"%")

    
class ThreadClass(QtCore.QThread):

    signalTemperature = QtCore.Signal(str)
    signalHumidity = QtCore.Signal(str)

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
                data = binascii.hexlify(d[0].strip())
                #addr = d[1]
                split_data = [data[i:i+8] for i in range(0, len(data), 8)]
                if not data: 
                    break
            
                for i in range(0, 4):
                    if split_data[i][0:5] == '00005':
                        humidityValue1 = str(int(split_data[i][6:8], 16))
                        print ('HUMIDITY #1\t\t' + humidityValue1)
                        self.signalHumidity.emit(humidityValue1)
                    elif split_data[i][0:5] == '00006':
                        temperatureValue1 = str(int(split_data[i][6:8], 16))
                        print ('TEMPERATURE #1\t\t' + temperatureValue1)
                        self.signalTemperature.emit(temperatureValue1)
                    elif split_data[i][0:5] == '0000b':
                        print ('POWER MONITOR #1\t' + split_data[i][6:8])
                    elif split_data[i][0:5] == '0000c':
                        print ('POWER MONITOR #2\t' + split_data[i][6:8])
                        print ('-----------------------------------------------------------\n')
            
            
                        
                #print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data + '\n'
                f.write('' + data + '\n')
                
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
