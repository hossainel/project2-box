from os import path, system
import sys
import socket
import threading 
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QFileDialog, QMessageBox, QLabel, QProgressBar, QWidget, QSplitter, QSpinBox)
from PyQt5.QtCore import QCoreApplication, Qt

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = 'BOX' #sets window title
        self.left = 200
        self.top = 100
        self.width = 600
        self.height = 400
        self.activeUser = ''
        # self.datafilepath = ''
        self.ip =  str(socket.gethostbyname(socket.gethostname()))
        self.port = 1234
        self.name = 'Bull1'
        self.password = ''
        self.datasize = 1024
        self.dtyp = 'ascii'
        self.tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.setWindowIcon(QIcon('box.jpg'))
        self.mainLayout = QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.loginWidget = QWidget(self)
        self.loginLayout = QVBoxLayout(self)
        self.loginWidget.setLayout(self.loginLayout)
        self.mainLayout.addWidget(self.loginWidget)
        self.loginWidget.show()
        
        self.mainWidget = QWidget(self)
        self.boxBody = QVBoxLayout(self)
        self.mainWidget.setLayout(self.boxBody)
        self.mainLayout.addWidget(self.mainWidget)
        self.mainWidget.hide() #main msg box window
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.progress = QProgressBar(self) #ultimate progress bar
        self.progress.setMinimum(0) #set the minium value

        self.headerFun()
        self.msgReader()
        self.sender()
        self.exito()
        self.loginFun()
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit?', 'Do you want to Exit from BOX?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try: self.tcpClientA.send('**quit'.encode(self.dtyp))
            except: pass
            sys.exit()
            event.accept()
        else: event.ignore()

    def mainClient(self, ip, port, uname, password):  
        # print(ip, port) 
        self.tcpClientA.connect((ip, port))
        unp = uname + '!@!@!' + password + '!@!@!'
        self.tcpClientA.send(unp.encode(self.dtyp))
        self.port = port
        self.clientRunning = True

        def receiveMsg(sock):
            tcpClientAerverDown = False
            while self.clientRunning and (not tcpClientAerverDown):
                try:
                    msg = sock.recv(self.datasize).decode(self.dtyp)
                    if ('!@!@!' in msg) and ('**file' not in msg):
                        # print(msg)
                        msg, self.name = msg.split('!@!@!')
                        l = '<b>IP: </b><u>'+self.ip+'</u> <b>Port:</b> <u>'+str(self.port)+ '</u> <b>User Name:</b> <u>'+self.name+'</u>'
                        self.labelIP.setText(l)

                    if "Number of people online" in msg:
                        # self.activeUser = usr.split('\n')
                        # for i in usr.split('\n'): user = user + i + '\n'
                        self.activeUser = msg
                        sld = str(len(msg.split('\n'))-2)
                        # print('msg, ', msg)
                        # print('px', sld)
                        # print('asdx', self.activeUser)
                        self.actvUsrBtn.setText('Active User ('+ sld +')')
                    elif '**file' in msg: self.fileToRecv(msg)
                    else:
                        try: 
                            msgxd, masgda = msg.split('>>')
                            print(msg)
                        except: msgxd, masgda = 'Error', msg
                        finally: self.msgBox.append('<b>'+msgxd+':</b> '+masgda)
                except:
                    self.msgBox.append("Server is Down. You are now Disconnected.")
                    # print('Server is Down. You are now Disconnected. Press Enter to exit...')
                    tcpClientAerverDown = True

        threading.Thread(target = receiveMsg, args = (self.tcpClientA,)).start()
        self.userlist('window')

    def fileToRecv(self, msg):
        #all in all
        fnx, nx, sxd = msg[6:].split('!@!@!')
        print(fnx, nx, sxd)
        self.msgBox.append('Receving File :<u>{0}</u>, From:<b>{1}</b> Size: {2} bytes'.format(fnx, nx, sxd))
        #recv file
        x, y, z = True, True, True
        with open('recieved/' + fnx, 'wb') as ft:
            print('p>file size,', sxd)
            axx = 0
            while True:
                data = self.tcpClientA.recv(self.datasize)
                axx = axx + self.datasize
                dxx = int(axx*100//int(sxd)) % 100
                if dxx == 25 and x: self.msgBox.append('File Received 25%.'); x = False
                if dxx == 50 and y: self.msgBox.append('File Received 50%.'); y = False
                if dxx == 75 and z: self.msgBox.append('File Received 75%.'); z = False
                #end of file
                if 'TNXATHATMEFINE'.encode(self.dtyp) in data: #file ender
                    #recv last data
                    ft.write(data[:-14])
                    print('file received...')
                    break
                # write data to a file
                ft.write(data)
        ft.close()
        # print('p>file receved '+ sxd + 'Bytes')
        self.msgBox.append('File Received successfully.')

    def loginFun(self):
        #header comment
        tmp1 = "<center><br/><h3>Welcome to <b>BOX</b>!</h3><br/>Fill up the following form to connect or to make a chat-BOX!<br/><br/></center>"
        info = QLabel(tmp1, self)

        #layouts
        btnLayout = QHBoxLayout(self)
        subLayout1 = QVBoxLayout(self)
        subLayout2 = QVBoxLayout(self)

        #labels
        iplbl = QLabel('IP: ', self)
        # iplbl.setAlignment(Qt.AlignRight)
        portlbl = QLabel('PORT: ', self)
        # portlbl.setAlignment(Qt.AlignRight)
        nlbl = QLabel('Name: ', self)
        # nlbl.setAlignment(Qt.AlignRight)
        passlbl = QLabel('Password: ', self)
        # passlbl.setAlignment(Qt.AlignRight)

        #label Layouts
        subLayout1.addWidget(iplbl)
        subLayout1.addWidget(portlbl)
        subLayout1.addWidget(nlbl)
        subLayout1.addWidget(passlbl)

        #lineEdits
        ipLine = QLineEdit(self)
        ipLine.setText(self.ip)
        ipLine.setClearButtonEnabled(True)
        ipLine.setAlignment(Qt.AlignCenter)

        portSpin = QSpinBox(self)
        portSpin.setRange(111, 65535)
        portSpin.setValue(self.port)
        portSpin.setAlignment(Qt.AlignCenter)

        nLine = QLineEdit(self)
        nLine.setText(self.name)
        nLine.setClearButtonEnabled(True)
        nLine.setAlignment(Qt.AlignCenter)

        passLine = QLineEdit(self)
        passLine.setText(self.password)
        passLine.setClearButtonEnabled(True)
        passLine.setAlignment(Qt.AlignCenter)

        #lineEdit Layouts
        subLayout2.addWidget(ipLine)
        subLayout2.addWidget(portSpin)
        subLayout2.addWidget(nLine)
        subLayout2.addWidget(passLine)

        #button functions
        def helpFun(): system("start help/index.html")
        def resetFun():
            ipLine.setText(self.ip)
            portSpin.setValue(self.port)
            nLine.setText(self.name)
            passLine.setText("")
        
        def toMainFun():
            T = True
            try:
                a, b, c, d = ipLine.text().split('.')
                int(a); int(b); int(c); int(d)
            except:
                ipLine.setText('Enter a  Valid IP')
                ipLine.backgroundRole()
                T = False
            if nLine.text() == '' or nLine.text() == 'Enter Name':
                nLine.setText('Enter Name')
                T = False
            if T: 
                self.ip = ipLine.text()
                self.port = portSpin.value()
                self.name = nLine.text()
                self.password = passLine.text()
                # print("Logges out")
                self.mainClient(ipLine.text(), portSpin.value(), nLine.text(), passLine.text())
                # print("Logges in out")
                l = '<b>IP: </b><u>'+self.ip+'</u> <b>Port:</b> <u>'+str(self.port)+ '</u> <b>User Name:</b> <u>'+self.name+'</u>'
                self.labelIP.setText(l)

                self.loginWidget.hide()
                self.mainWidget.show()

        #login, reset, help & exit button
        loginbtn = QPushButton('Log In', self)
        loginbtn.clicked.connect(toMainFun)
        resetbtn = QPushButton('Reset', self) 
        resetbtn.clicked.connect(resetFun)
        helpbtn = QPushButton('Help', self) 
        helpbtn.clicked.connect(helpFun)
        exitbtn = QPushButton('Exit', self)
        exitbtn.clicked.connect(self.CloseApp)

        #button Layout  
        btnLayout.addWidget(exitbtn)
        btnLayout.addWidget(helpbtn)
        btnLayout.addWidget(resetbtn)
        btnLayout.addWidget(loginbtn)

        #spiltters
        spiltter11 = QSplitter(Qt.Vertical, self)
        spiltter12 = QSplitter(Qt.Vertical, self)
        
        spiltter21 = QSplitter(Qt.Horizontal, self)
        spiltter22 = QSplitter(Qt.Horizontal, self)
        spiltter23 = QSplitter(Qt.Horizontal, self)     

        #formlayout
        subMain = QHBoxLayout(self)
        formLayout = QVBoxLayout(self)
        formLayout.addWidget(info)

        subMain.addLayout(subLayout1)
        subMain.addLayout(subLayout2)

        formLayout.addLayout(subMain)        
        formLayout.addLayout(btnLayout)

        #sider
        siderLayout = QHBoxLayout(self)
        siderLayout.addWidget(spiltter21)
        siderLayout.addLayout(formLayout)
        siderLayout.addWidget(spiltter22)

        #footer
        tmp2 = 'Developed By <a href="https://www.google.com/search?q=alzestors"> Alzestors</a>.<br>'
        footer = QLabel(tmp2, self)
        footerLayout = QHBoxLayout(self)
        footerLayout.addWidget(spiltter23)
        footerLayout.addWidget(footer)
        
        #assigning layouts
        self.loginLayout.addWidget(spiltter11)
        self.loginLayout.addLayout(siderLayout)
        self.loginLayout.addWidget(spiltter12)
        self.loginLayout.addLayout(footerLayout)

    def msgReader(self):
        self.msgBox = QTextEdit(self)
        self.msgBox.setReadOnly(True)
        #modification needed
        self.boxBody.addWidget(self.msgBox)
    
    def sender(self):
        self.dataSender = QHBoxLayout(self)
        self.textsFun()
        self.fileFun()
        self.boxBody.addLayout(self.dataSender)
    
    def textsFun(self):
        self.textline = QLineEdit(self)
        self.textline.setClearButtonEnabled(True)
        self.textline.height = 25
        self.textBtn = QPushButton('Send' ,self)
        self.textBtn.clicked.connect(self.Send)
        self.dataSender.addWidget(self.textline)
        self.dataSender.addWidget(self.textBtn)

    def Send(self):
        uname = self.name
        tmpMsg = self.textline.text()
        msgx = '**brodcast' + uname + ">>" + tmpMsg
        if tmpMsg == "": pass
        else:
            self.tcpClientA.send(msgx.encode(self.dtyp))
            self.textline.setText("")
            textFormatted='<b>You: </b>{0}'.format(tmpMsg)
            self.msgBox.append(textFormatted)

    def headerFun(self):
        l = '<b>IP: </b><u>'+self.ip+'</u> <b>Port:</b> <u>'+str(self.port)+ '</u> <b>User Name:</b> <u>'+self.name+'</u>'
        self.labelIP = QLabel(l, self)
        self.headerLayout = QHBoxLayout(self)
        self.headerLayout.addWidget(self.labelIP)

        self.progress.setValue(0)
        self.progress.setFormat(u'No file to send!')
        #self.progress.setFormat(u'Sent: %v Byte, File Size: %m Byte, Sending Progress: %p%.')
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.height = 10
        self.headerLayout.addWidget(self.progress)
        self.boxBody.addLayout(self.headerLayout)
    
    def fileFun(self):
        self.fileBtn = QPushButton('Send File...', self)
        self.fileBtn.clicked.connect(self.openFile)
        self.dataSender.addWidget(self.fileBtn)
    
    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', '')
        if filename[0]:            
            #In the same folder or path is this file running must the file you want to tranfser to be				#sending filename in file
            if filename[0].find('\\') > 0: fx = filename[0].split('\\')[-1] 
            elif filename[0].find('/') > 0: fx = filename[0].split('/')[-1]
            else: fx = filename[0]

            sx = int(path.getsize(filename[0]))
            #sending file size in file
            pkgFile = "**file" + fx + '!@!@!' + self.name + '!@!@!' + str(sx) 
            self.tcpClientA.send(pkgFile.encode(self.dtyp)) 
            print(pkgFile)
            self.msgBox.append("<b>Sending</b> : <u>"+filename[0]+'</u>')
            #progress bar function
            p = 0
            px = sx
            self.progress.setMaximum(px)
            self.progress.setValue(p)

            #self.progress.setFormat(u'Sent: %v Byte, File Size: %m Byte, Sending Progress: %p%.')
            
            self.progress.setFormat(u'Sent: %v Byte (%p%).')

            #sending file
            with open(filename[0],'rb') as f:
                l = f.read(self.datasize)
                while (l):
                    self.tcpClientA.send(l)
                    p = p + 1024
                    self.progress.setValue(p)
                    l = f.read(self.datasize)
            f.close()
            self.tcpClientA.send(b'TNXATHATMEFINE') #end of file EOF
            print('sent')
            p = 0
            self.progress.setFormat(u'File Sent!')
            self.msgBox.append('File Sent successfully.')
            self.progress.setValue(0)
            self.progress.setFormat(u'No file to send!')
            #progress ends here
     
    def exito(self):
        self.activity = QHBoxLayout(self)
        self.exitBtn = QPushButton('Exit', self)
        self.exitBtn.clicked.connect(self.CloseApp)
        self.activity.addWidget(self.exitBtn)

        self.actvUsrBtn = QPushButton('Active User (0)', self)
        self.actvUsrBtn.clicked.connect(self.userlist)
        self.activity.addWidget(self.actvUsrBtn)
        self.boxBody.addLayout(self.activity)

    def userlist(self, wxx=None):
        self.tcpClientA.send('**chatlist'.encode(self.dtyp))
        
        usr = self.activeUser
        sld = str(len(usr.split('\n'))-2)
        if '\n' in usr: pass
        else: usr = usr + '\n'
        self.actvUsrBtn.setText('Active User ('+ sld +')')
        QMessageBox.about(self, 'User(s)', usr)
    
    def CloseApp(self):
        reply = QMessageBox.question(self, 'Exit?', 'Do you want to Exit from BOX?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try: self.tcpClientA.send('**quit'.encode(self.dtyp))
            except: pass
            sys.exit()
        else: pass

    def Close(self):
        QCoreApplication.instance().quit()
