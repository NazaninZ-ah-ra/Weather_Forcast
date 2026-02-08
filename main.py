from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import requests
from datetime import datetime,timedelta
from time import sleep
from urllib.parse import quote



class Ui_MainWindow(QMainWindow):

    def __init__(self,):
        super().__init__()
        self.appid = "f2f238852603acca0c878c17215c1d12"
        self.city_user = ""
        self.utc= datetime.utcnow()


    def mySignals(self):
        self.pushButton_Search.clicked.connect(self.search)

    def search(self):
        self.city_user = self.lineEdit_Search.text().strip()
        if self.city_user == "":
            self.label_statusMsg.setText("Pls Enter a City")
            return

        self.label_statusMsg.setText("Loading...")
        QApplication.processEvents()

        try:
            self.weather_mission()
            self.label_statusMsg.setText("Loaded")
            self.lineEdit_Search.setText("")
            
        except requests.exceptions.ConnectionError as r:
            self.label_statusMsg.setText("🌐  Netwrok Error")
           
        except Exception as e:     
            self.label_statusMsg.setText("City not Found!")
            print(e)

    def clock(self,timezone):
        while True :
            local_t = self.utc + timedelta(seconds=timezone) # Gets local time 
            local_t = local_t + timedelta(seconds=1)
            sleep(1)
            return self.label_Time.setText(local_t.strftime("%H:%M:%S")) # Updates

    def weather_mission(self):
        encoded_city = quote(self.city_user) # Making it usable for formats other than English 
        myurl = f"http://api.openweathermap.org/geo/1.0/direct?q={encoded_city}&appid={self.appid}"
        response = requests.get(myurl)

        if response.status_code == 200:
            loc_data = response.json()
            self.lat = loc_data[0]["lat"]
            self.lon = loc_data[0]["lon"]
            city = loc_data[0]["name"]
            country = loc_data[0]["country"]

            my_url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.appid}&units=metric"
            response = requests.get(my_url)

            if response.status_code == 200:
                w_info_data = response.json()
                w = w_info_data['weather'][0]['description'] 
                mytimezone =  w_info_data["timezone"]
                
                self.label_City.setText(f"{city}, {country}")
                self.label_Temp.setText(f"{int(w_info_data['main']['temp'])} °C")
                self.label_Weather.setText(w.title())

                self.label_Sunset.setText("🌇 sunset:")
                self.label_Sunrise.setText("🌅 sunrise:")

                tp_rise = w_info_data['sys']['sunrise'] # tp : timestamp
                utc_rise = datetime.fromtimestamp(tp_rise)
                local_t = utc_rise + timedelta(seconds=mytimezone)
                self.label_RiseTime.setText(local_t.strftime("%H:%M:%S"))

                tp_set = w_info_data['sys']['sunset'] # tp : timestamp
                utc_set = datetime.fromtimestamp(tp_set)
                local_t = utc_set + timedelta(seconds=mytimezone)
                self.label_SetTime.setText(local_t.strftime("%H:%M:%S"))

                self.now = datetime.now()
                self.label_date.setText(self.now.strftime("%A, %d %B %Y"))
               
                self.time = QTimer()
                self.time.timeout.connect(lambda : self.clock(timezone=mytimezone))
                self.time.start(100)
                
                

                icon = self.get_icon(w)
                self.label_imag.setPixmap(QPixmap(f"icons/{icon}.png"))
                self.get_forcast()
            else:
                self.label_statusMsg.setText("Failed to fetch Weather Info")
        else:
            self.label_statusMsg.setText("Failed to fetch City Info")

        

            

    def get_forcast(self):
        f_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.appid}&units=metric"
        f_response = requests.get(f_url)
        if f_response.status_code == 200 :
            data = f_response.json()
            forecast_list = data["list"]
            daily_forcast = {}

            for item in forecast_list :
                dt = datetime.fromtimestamp(item["dt"])
                day_name = dt.strftime("%a")
            
                if dt.hour == 12 :
                    daily_forcast[day_name] ={
                        "temp" : int(item["main"]["temp"] ),
                        "weather" : item['weather'][0]['description'].lower()
                    }
            w_info = []
            temp = []
            days = list(daily_forcast.keys())
            
            for day,info in daily_forcast.items():
                w = info.get("weather")
                t = str(info.get("temp"))

                w_info.append(w)
                temp.append(t)
       
            
            for i,(w,t) in enumerate (zip(w_info,temp)):
                getattr(self,f"label_Temp_{i+1}").setText(f"{str(t)}°C")
                getattr(self,f"label_Day_{i+1}").setText(str(days[i]))
                icons = self.get_icon(w)
                getattr(self,f"label_Pic_{i+1}").setPixmap(QPixmap(f"icons/{icons}.png"))
                getattr(self,f"label_Pic_{i+1}").setScaledContents(True)
                    
    def get_icon (self,weather_info ):
        w = weather_info.lower()
       
   
        if "snow" in w or "snowy" in w:
            return "snowy"
        elif "clear" in w:
            return "clear"
        elif "cloud" in w:
            return "cloudy"
        elif "mist" in w or "fog" in w or "haze" in w:
            return "mist_fog"
        elif "rain" in w:
            return "rain"
        elif "sunny" in w and "sunset" not in w and "sunrise" not in w:
            return "sunny"
        elif "tornado" in w:
            return "tornado"
        else:
            return "generall"
        


    def setupUi(self):
        self.setObjectName("self")
        self.resize(800, 600)
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.setFont(font)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.lineEdit_Search = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_Search.setGeometry(QtCore.QRect(20, 50, 581, 20))
        self.lineEdit_Search.setObjectName("lineEdit_Search")
        self.label_Title = QtWidgets.QLabel(self.centralwidget)
        self.label_Title.setGeometry(QtCore.QRect(300, 10, 181, 21))
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_Title.setFont(font)
        self.label_Title.setObjectName("label_Title")
        self.pushButton_Search = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Search.setGeometry(QtCore.QRect(620, 50, 131, 23))
        self.pushButton_Search.setObjectName("pushButton_Search")
        self.groupBox_Info = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Info.setGeometry(QtCore.QRect(20, 70, 731, 261))
        self.groupBox_Info.setObjectName("groupBox_Info")
        self.label_imag = QtWidgets.QLabel(self.groupBox_Info)
        self.label_imag.setGeometry(QtCore.QRect(220, 80, 131, 171))
        self.label_imag.setText("")
        self.label_imag.setObjectName("label_imag")
        self.label_City = QtWidgets.QLabel(self.groupBox_Info)
        self.label_City.setGeometry(QtCore.QRect(300, 20, 600, 40))
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_City.setFont(font)
        self.label_City.setText("")
        self.label_City.setObjectName("label_City")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_Info)
        self.layoutWidget.setGeometry(QtCore.QRect(360, 79, 171, 181))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_Temp = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(26)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_Temp.setFont(font)
        self.label_Temp.setText("")
        self.label_Temp.setObjectName("label_Temp")
        self.verticalLayout.addWidget(self.label_Temp)
        self.label_Weather = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_Weather.setFont(font)
        self.label_Weather.setText("")
        self.label_Weather.setObjectName("label_Weather")
        self.verticalLayout.addWidget(self.label_Weather)
        self.label_Sunset = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(14)
        font.setItalic(False)
        self.label_Sunset.setFont(font)
        self.label_Sunset.setObjectName("label_Sunset")
        self.verticalLayout.addWidget(self.label_Sunset)
        self.label_Sunrise = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(14)
        font.setItalic(False)
        self.label_Sunrise.setFont(font)
        self.label_Sunrise.setObjectName("label_Sunrise")
        self.verticalLayout.addWidget(self.label_Sunrise)
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox_Info)
        self.layoutWidget1.setGeometry(QtCore.QRect(540, 190, 67, 64))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_SetTime = QtWidgets.QLabel(self.layoutWidget1)
        self.label_SetTime.setMinimumSize(QtCore.QSize(0, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_SetTime.setFont(font)
        self.label_SetTime.setText("")
        self.label_SetTime.setObjectName("label_SetTime")
        self.verticalLayout_2.addWidget(self.label_SetTime)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.label_RiseTime = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_RiseTime.setFont(font)
        self.label_RiseTime.setText("")
        self.label_RiseTime.setObjectName("label_RiseTime")
        self.verticalLayout_2.addWidget(self.label_RiseTime)
        self.layoutWidget2 = QtWidgets.QWidget(self.groupBox_Info)
        self.layoutWidget2.setGeometry(QtCore.QRect(210, 50, 431, 22))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_date = QtWidgets.QLabel(self.layoutWidget2)
        self.label_date.setMinimumSize(QtCore.QSize(250, 0))
        font = QtGui.QFont()
        font.setFamily("Mongolian Baiti")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_date.setFont(font)
        self.label_date.setText("")
        self.label_date.setObjectName("label_date")
        self.horizontalLayout_2.addWidget(self.label_date)
        self.label_Time = QtWidgets.QLabel(self.layoutWidget2)
        self.label_Time.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setFamily("Mongolian Baiti")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_Time.setFont(font)
        self.label_Time.setText("")
        self.label_Time.setObjectName("label_Time")
        self.horizontalLayout_2.addWidget(self.label_Time)
        self.groupBox_Forcast = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Forcast.setGeometry(QtCore.QRect(20, 349, 740, 201))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setItalic(True)
        self.groupBox_Forcast.setFont(font)
        self.groupBox_Forcast.setObjectName("groupBox_Forcast")
        self.widget_forcast_1 = QtWidgets.QWidget(self.groupBox_Forcast)
        self.widget_forcast_1.setGeometry(QtCore.QRect(60, 20, 111, 171))
        self.widget_forcast_1.setObjectName("widget_forcast_1")
        self.label_Day_1 = QtWidgets.QLabel(self.widget_forcast_1)
        self.label_Day_1.setGeometry(QtCore.QRect(30, 0, 47, 31))
        self.label_Day_1.setText("")
        self.label_Day_1.setObjectName("label_Day_1")
        self.label_Temp_1 = QtWidgets.QLabel(self.widget_forcast_1)
        self.label_Temp_1.setGeometry(QtCore.QRect(30, 122, 47, 31))
        self.label_Temp_1.setText("")
        self.label_Temp_1.setObjectName("label_Temp_1")
        self.label_Pic_1 = QtWidgets.QLabel(self.widget_forcast_1)
        self.label_Pic_1.setGeometry(QtCore.QRect(16, 42, 81, 61))
        self.label_Pic_1.setText("")
        self.label_Pic_1.setObjectName("label_Pic_1")
        self.widget_Forcast_2 = QtWidgets.QWidget(self.groupBox_Forcast)
        self.widget_Forcast_2.setGeometry(QtCore.QRect(190, 20, 111, 171))
        self.widget_Forcast_2.setObjectName("widget_Forcast_2")
        self.label_Day_2 = QtWidgets.QLabel(self.widget_Forcast_2)
        self.label_Day_2.setGeometry(QtCore.QRect(30, 0, 47, 31))
        self.label_Day_2.setText("")
        self.label_Day_2.setObjectName("label_Day_2")
        self.label_Temp_2 = QtWidgets.QLabel(self.widget_Forcast_2)
        self.label_Temp_2.setGeometry(QtCore.QRect(30, 122, 47, 31))
        self.label_Temp_2.setText("")
        self.label_Temp_2.setObjectName("label_Temp_2")
        self.label_Pic_2 = QtWidgets.QLabel(self.widget_Forcast_2)
        self.label_Pic_2.setGeometry(QtCore.QRect(16, 42, 81, 61))
        self.label_Pic_2.setText("")
        self.label_Pic_2.setObjectName("label_Pic_2")
        self.widget_Forcast_3 = QtWidgets.QWidget(self.groupBox_Forcast)
        self.widget_Forcast_3.setGeometry(QtCore.QRect(320, 20, 111, 171))
        self.widget_Forcast_3.setObjectName("widget_Forcast_3")
        self.label_Day_3 = QtWidgets.QLabel(self.widget_Forcast_3)
        self.label_Day_3.setGeometry(QtCore.QRect(30, 0, 47, 31))
        self.label_Day_3.setText("")
        self.label_Day_3.setObjectName("label_Day_3")
        self.label_Temp_3 = QtWidgets.QLabel(self.widget_Forcast_3)
        self.label_Temp_3.setGeometry(QtCore.QRect(30, 122, 47, 31))
        self.label_Temp_3.setText("")
        self.label_Temp_3.setObjectName("label_Temp_3")
        self.label_Pic_3 = QtWidgets.QLabel(self.widget_Forcast_3)
        self.label_Pic_3.setGeometry(QtCore.QRect(16, 42, 81, 61))
        self.label_Pic_3.setText("")
        self.label_Pic_3.setObjectName("label_Pic_3")
        self.widget_Forcast_4 = QtWidgets.QWidget(self.groupBox_Forcast)
        self.widget_Forcast_4.setGeometry(QtCore.QRect(450, 20, 111, 171))
        self.widget_Forcast_4.setObjectName("widget_Forcast_4")
        self.label_Day_4 = QtWidgets.QLabel(self.widget_Forcast_4)
        self.label_Day_4.setGeometry(QtCore.QRect(30, 0, 47, 31))
        self.label_Day_4.setText("")
        self.label_Day_4.setObjectName("label_Day_4")
        self.label_Temp_4 = QtWidgets.QLabel(self.widget_Forcast_4)
        self.label_Temp_4.setGeometry(QtCore.QRect(30, 122, 47, 31))
        self.label_Temp_4.setText("")
        self.label_Temp_4.setObjectName("label_Temp_4")
        self.label_Pic_4 = QtWidgets.QLabel(self.widget_Forcast_4)
        self.label_Pic_4.setGeometry(QtCore.QRect(16, 42, 81, 61))
        self.label_Pic_4.setText("")
        self.label_Pic_4.setObjectName("label_Pic_4")
        self.widget_Forcast_5 = QtWidgets.QWidget(self.groupBox_Forcast)
        self.widget_Forcast_5.setGeometry(QtCore.QRect(590, 20, 111, 171))
        self.widget_Forcast_5.setObjectName("widget_Forcast_5")
        self.label_Day_5 = QtWidgets.QLabel(self.widget_Forcast_5)
        self.label_Day_5.setGeometry(QtCore.QRect(30, 0, 47, 31))
        self.label_Day_5.setText("")
        self.label_Day_5.setObjectName("label_Day_5")
        self.label_Temp_5 = QtWidgets.QLabel(self.widget_Forcast_5)
        self.label_Temp_5.setGeometry(QtCore.QRect(30, 122, 47, 31))
        self.label_Temp_5.setText("")
        self.label_Temp_5.setObjectName("label_Temp_5")
        self.label_Pic_5 = QtWidgets.QLabel(self.widget_Forcast_5)
        self.label_Pic_5.setGeometry(QtCore.QRect(16, 42, 81, 61))
        self.label_Pic_5.setText("")
        self.label_Pic_5.setObjectName("label_Pic_5")
        self.layoutWidget3 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget3.setGeometry(QtCore.QRect(26, 329, 171, 31))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_Status = QtWidgets.QLabel(self.layoutWidget3)
        self.label_Status.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(True)
        self.label_Status.setFont(font)
        self.label_Status.setObjectName("label_Status")
        self.horizontalLayout.addWidget(self.label_Status)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_statusMsg = QtWidgets.QLabel(self.layoutWidget3)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_statusMsg.setFont(font)
        self.label_statusMsg.setObjectName("label_statusMsg")
        self.horizontalLayout.addWidget(self.label_statusMsg)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.mySignals()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, ):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Naxi Weather🌦❄️"))
        self.label_Title.setText(_translate("self", "MY WEATHER"))
        self.pushButton_Search.setText(_translate("self", "🔍 Get Forecast"))
        self.groupBox_Info.setTitle(_translate("self", "INFO:"))
        self.groupBox_Forcast.setTitle(_translate("self", "Forcast"))
        self.label_Status.setText(_translate("self", "Status:"))
  


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.setupUi()
    ui.show()
    sys.exit(app.exec_())
