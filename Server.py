import socket
import threading
#Main class goes here

from os import system
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDialog,  QGroupBox, QHBoxLayout,
                             QLabel, QMessageBox, QMenu, QPushButton, QSpinBox , QSystemTrayIcon, 
                             QVBoxLayout, QSplitter, QLineEdit)
from PyQt5.QtCore import Qt

class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        self.icon = QIcon('box.jpg')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverRunning = True
        self.ip = str(socket.gethostbyname(socket.gethostname()))
        self.port = 1234
        self.datasize = 1024
        self.clients = {}
        self.dtyp = 'ascii'
        self.welcomeM = "Welcome to Box..."
        self.password = ''

        # self.s.bind((self.ip, self.port))
        # self.s.listen()

        self.title = 'BOX Server' 
        self.left = 200
        self.top = 100
        self.width = 300
        self.height = 150
        self.setWindowIcon(self.icon)

        self.mainLayout = QVBoxLayout() #one down after one
        self.setLayout(self.mainLayout)

        self.TrayIconFun()
        self.TrayIconFun.activated.connect(self.iconActivated)
        self.TrayIconFun.setIcon(self.icon)
        self.TrayIconFun.show()

        self.initUI() #main initfun

    def closeEvent(self, event):
        # self.hide()
        sys.exit()

    def initUI(self):
        self.setWindowTitle(self.title) #sets window Title
        self.setMinimumSize(self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.ipFun()
        self.ppFun()
        self.show()

    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showMessage()    

    def showMessage(self, message = 'Server is Running', time = 5):
        self.TrayIconFun.showMessage('Box', message, self.icon, time)

    def TrayIconFun(self):
        self.quitAction = QAction("&Quit", self,
                triggered=QApplication.instance().quit)
        self.TrayIconFun = QSystemTrayIcon(self)
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)
        self.TrayIconFun.setContextMenu(self.trayIconMenu)
        l = 'Server Running' + '\nIP: <' + self.ip + '>\nPort: <' + str(self.port) + '>\npassword: <' + self.password + '>'
        self.TrayIconFun.setToolTip(l)
        # self.showMessage()
        # self.TrayIconFun.DoubleClick.connected(self.CloseApp)

    def startFun(self): 
        print("Server Ready...")
        self.password = self.passLine.text()
        self.welcomeM = self.wlLine.text()
        self.port = self.portSpin.value()
        print('Password created.')        
        self.s.bind((self.ip, self.port))
        self.s.listen()
        print("IP Address of the server::%s :" % self.ip, self.port)
        l = 'Server Running' + '\nIP: <' + self.ip + '>\nPort: <' + str(self.port) + '>\npassword: <' + self.password + '>'
        self.TrayIconFun.setToolTip(l)
        self.hide()
        def handleClient(client, uname):
            self.clientConnected = True
            self.keys = self.clients.keys()
            self.help = 'There are four commands in Messager\n1::**chatlist\n2::**help\n \
                3::**brodcast\n4::**quit\n5::**file'
            
            while self.clientConnected:
                try:
                    msg = client.recv(self.datasize).decode(self.dtyp)
                    print(msg)
                    response = 'Number of people online\n'
                    if '**chatlist' in msg:
                        clientNo = 0
                        for name in self.keys:
                            clientNo = clientNo + 1
                            response = response + str(clientNo) + '::' + name + '\n'
                        # client.send(response.encode(self.dtyp))
                        for k, v in self.clients.items():
                            v.send(response.encode(self.dtyp))

                        l = 'Server Running' + '\nIP: <' + self.ip + '>\nPort: <' + str(self.port) + '>\npassword: <' + self.password + '>\n' + response
                        self.TrayIconFun.setToolTip(l)
                        self.showMessage(response)
        
                    elif '**help' in msg:
                        client.send(self.help.encode(self.dtyp))
                    elif '**brodcast' in msg:
                        msg = msg.replace('**brodcast', '')
                        for k, v in self.clients.items():
                            if k == msg.split('>>')[0]: print(k+'<<')
                            else: v.send(msg.encode(self.dtyp))
                                
                    elif '**file' in msg:
                        #sending files
                        #recv filenames sender name = nx file size = sx
                        fileName, nx, sx = msg[6:].split('!@!@!')
                        #sending file name by msg
                        for k, v in self.clients.items():
                            if k == nx: pass
                            else: v.send(msg.encode(self.dtyp))
                        #recv file then sending files
                        with open('recieved/tmp.t', 'wb') as f:
                            print('p>file size,', sx)
                            axx = 0
                            while True:
                                print('receiving data', axx, 'byte')
                                #recv file data
                                data = client.recv(self.datasize)
                                axx = axx + self.datasize
                                #end of file
                                if 'TNXATHATMEFINE'.encode(self.dtyp) in data: #file ender
                                    print('noty')
                                    #send last data
                                    for k, v in self.clients.items():
                                        if k == nx: pass
                                        else: v.send(data)
                                    #saving last data
                                    #f.write(data[:-14])
                                    print('file receieved...')
                                    break
                                #send file data
                                for k, v in self.clients.items():
                                    if k == nx: pass
                                    else: v.send(data)
                                # write data to a file
                                #f.write(data)
                        f.close()
                        print('p>file size '+ sx + 'B')
                    elif '**quit' in msg:
                        response = 'Stopping Session and exiting...'
                        client.send(response.encode(self.dtyp))
                        self.clients.pop(uname)
                        print(uname + ' has been logged out.')
                        self.clientConnected = False
                        self.keys = self.clients.keys()
                        response = 'Number of people online\n'
                        clientNo = 0
                        for name in self.keys:
                            clientNo = clientNo + 1
                            response = response + str(clientNo) + '::' + name + '\n'
                        # client.send(response.encode(self.dtyp))
                        for k, v in self.clients.items():
                            v.send(response.encode(self.dtyp))
                            kxxx = 'ROOT>>' + uname + ' has been logged out.'
                            v.send(kxxx.encode(self.dtyp))

                        l = 'Server Running' + '\nIP: <' + self.ip + '>\nPort: <' + str(self.port) + '>\npassword: <' + self.password + '>\n' + response
                        self.TrayIconFun.setToolTip(l)
                        self.showMessage(uname + ' has been logged out.')
        
                    else: client.send('Trying to send message with an invalid option.'.encode(self.dtyp))
                except:
                    self.clients.pop(uname)
                    print(uname + ' has been logged out.')
                    self.clientConnected = False
                    self.keys = self.clients.keys()
                    response = 'Number of people online\n'
                    clientNo = 0
                    for name in self.keys:
                        clientNo = clientNo + 1
                        response = response + str(clientNo) + '::' + name + '\n'
                    # client.send(response.encode(self.dtyp))
                    for k, v in self.clients.items():
                        v.send(response.encode(self.dtyp))
                        kxxx = 'ROOT>>'+ uname + ' has been logged out.'
                        v.send(kxxx.encode(self.dtyp))

                    l = 'Server Running' + '\nIP: <' + self.ip + '>\nPort: <' + str(self.port) + '>\npassword: <' + self.password + '>\n' + response
                    self.TrayIconFun.setToolTip(l)
                    self.showMessage(uname + ' has been logged out.')
        

        while self.serverRunning:
            client, address = self.s.accept()
            uname, password, _ = client.recv(self.datasize).decode(self.dtyp).split('!@!@!')
            #password = client.recv(self.datasize).decode(self.dtyp)
            namesx = self.clients.keys()
            for i in namesx:
                if i == uname: uname = uname + 's'
            print(uname, password)
            print(self.password)
            if password == self.password:
                print("%s connected to the server..." % str(uname))
                #next here will be added a welcome msg
                welcomeMsg = "ROOT>>" + self.welcomeM + '!@!@!' + uname
                client.send(welcomeMsg.encode(self.dtyp))
                print(self.clients)
                print(address)
                if client not in self.clients:
                    self.clients[uname] = client
                    threading.Thread(target = handleClient, args = (client, uname, )).start()
            else:
                print(uname, '>>client terminated') 
                client.send("Worng Passowrd!".encode(self.dtyp))
                #client.close()

    def ppFun(self):
        ly = QHBoxLayout(self)
        ly1 = QVBoxLayout(self)
        ly2 = QVBoxLayout(self)
        #spiltters        
        spiltter21 = QSplitter(Qt.Horizontal, self)
        spiltter22 = QSplitter(Qt.Horizontal, self)
        #port
        pxtLbl = QLabel("Port: ", self)
        ly1.addWidget(pxtLbl)

        self.portSpin = QSpinBox(self)
        self.portSpin.setRange(111, 65535)
        self.portSpin.setValue(self.port)
        self.portSpin.setAlignment(Qt.AlignCenter)
        ly2.addWidget(self.portSpin)

        #WelcomeMsg
        wlLbl = QLabel('Welcome Note: ')
        ly1.addWidget(wlLbl)

        self.wlLine = QLineEdit(self)
        self.wlLine.setText(self.welcomeM)
        self.wlLine.setClearButtonEnabled(True)
        self.wlLine.setAlignment(Qt.AlignCenter)
        ly2.addWidget(self.wlLine)

        #password
        pxs = QLabel('Password: ', self)
        ly1.addWidget(pxs)

        self.passLine = QLineEdit(self)
        self.passLine.setText(self.password)
        self.passLine.setClearButtonEnabled(True)
        self.passLine.setAlignment(Qt.AlignCenter)
        ly2.addWidget(self.passLine)

        #port, wlecomeMsg, pass layout input
        ly.addWidget(spiltter21)
        ly.addLayout(ly1)
        ly.addLayout(ly2)
        ly.addWidget(spiltter22)
        self.mainLayout.addLayout(ly)

        #button functions
        def helpFun(): system("start help/index.html")
        def resetFun():
            self.portSpin.setValue(self.port)
            self.wlLine.setText(self.welcomeM)
            self.passLine.setText("")
        
        # def toStartFun():
        #     threading.Thread(target = self.startFun).start()
            

        #buttons
        ly3 = QHBoxLayout(self)
        resetbtn = QPushButton('Reset', self) 
        resetbtn.clicked.connect(resetFun)
        startbtn = QPushButton('Start', self) 
        startbtn.clicked.connect(self.startFun)
        helpbtn = QPushButton('Help', self) 
        helpbtn.clicked.connect(helpFun)
        exitbtn = QPushButton('Exit', self)
        exitbtn.clicked.connect(self.CloseApp)
        ly3.addWidget(exitbtn)
        ly3.addWidget(helpbtn)
        ly3.addWidget(resetbtn)
        ly3.addWidget(startbtn)

        self.mainLayout.addLayout(ly3)
    
    def ipFun(self):
        ix = '<h2>IP ADDRESS: <u><i>' + self.ip + '</u></i></h2>'
        ipLbl = QLabel(ix, self)
        ipLbl.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(ipLbl)

    def aboutApp(self):
        QMessageBox.about(self, 'About BOX', "<h3>BOX</h3> BOX is a communication server. \
                          It usually used to do a secret communication.\
                          We hope you will give us some more ideas to use it with\na batter \
                          way. <br>It's open for you all to use. For anything else, \
                          you can connect with us through \
                          <strong><a href='https://www.google.com/search?q=alzestors'>Alzestors</a></strong>.")
 
    def CloseApp(self):
        # self.hide()
        sys.exit()

    def visiblity(self, visible):
        super(Window, self).visiblity(visible)

App = QApplication(sys.argv)
window = Window()   
window.exec()
sys.exit(App.exec())