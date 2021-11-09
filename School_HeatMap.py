import grequests
from PyQt5 import QtWidgets
import folium
from folium.plugins.heat_map_withtime import HeatMapWithTime
import numpy as np
from folium.plugins import HeatMap
from PyQt5.QtWidgets import QFrame
import io
import sys
import time
import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread,pyqtSignal,QDateTime,QObject,QTimer
from PyQt5.QtWidgets import QApplication,QDialog,QLineEdit,QLabel, QVBoxLayout
from PyQt5 import QtWebEngineWidgets,sip
from PyQt5.QtWidgets import QLabel
import pandas as pd
import pprint
import Take_data
import campus_data_monitor
cdm =Take_data.CampusDataMonitor()
cdm2 = campus_data_monitor.CampusDataMonitor()
layout=QVBoxLayout()
#多線程實作主程式
class TakeData_Thread(QThread):
    trigger=pyqtSignal(list,list)#the signal type is two list
    time_cost_HeatMap=0
    time_cost_loc=0
    def __int__(self):
        # initialize
        super(TakeData_Thread, self).__init__()
    def receive_time_from_Init(self,time,time2):
        #從主線程獲取初始化時取資料的時間
        self.time_cost_HeatMap=time
        self.time_cost_loc=time2
    def run(self):
        while(True):
            # Take data完傳送訊號給主線程
            time.sleep(30-self.time_cost_HeatMap-self.time_cost_loc)
            data ,self.time_cost_HeatMap=Take_data.Take_Data_Now(cdm)#Heat map data
            data2,self.time_cost_loc = campus_data_monitor.Take_Data_Now(cdm2)#cumulative number of people
            self.trigger.emit(data,data2)
class Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("People_Heat_Map")
        self.resize(640, 480)
        self.setLayout(layout)
        #initialize map data  *************************************************************************
        data ,time_cost_HeatMap =Take_data.Take_Data_Now(cdm)
        data2,time_cost_loc = campus_data_monitor.Take_Data_Now(cdm2)
        #*********************************************************************************************

        #input data to folium's map pakage and set some Marker******************************************
        fmap = folium.Map(location=[22.996363580424514, 120.21903238440177], zoom_start=17)
        HeatMap(data,min_opacity=0.4,blur=50,radius=50).add_to(fmap)

        html =   '''<font face="微軟正黑體"><font size="4">雲平大樓:</font>
                    ''' + str(data2[0][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m0 = folium.Marker(location=[22.99891110398634, 120.21723168980603],popup=popup)

        html =   '''<font face="微軟正黑體"><font size="4">資工系館:</font>
                    ''' + str(data2[1][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m1 = folium.Marker(location=[22.99726633629006, 120.2212997328783],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">修齊大樓:</font>
                    ''' + str(data2[2][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m2 = folium.Marker(location=[23.00085204740406, 120.21786248420196],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">計網中心:</font>
                    ''' + str(data2[3][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m3 = folium.Marker(location=[22.99811369711759, 120.2184468855774],popup=popup)

        html =   '''<font face="微軟正黑體"><font size="4">光復機車:</font>
                    ''' + str(data2[4][1])
        iframe = folium.IFrame(html,width=160,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m4 = folium.Marker(location=[22.99677295694284, 120.2164651939948],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">光一舍:</font>
                    ''' + str(data2[5][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m5 = folium.Marker(location=[22.999008047465647, 120.21451704980048],popup=popup)

        fmap.add_child(child=m0)
        fmap.add_child(child=m1)
        fmap.add_child(child=m2)
        fmap.add_child(child=m3)
        fmap.add_child(child=m4)
        fmap.add_child(child=m5)

        data_for_webView = io.BytesIO()
        fmap.save(data_for_webView,close_file=False)
        webView=QtWebEngineWidgets.QWebEngineView()
        webView.setHtml(data_for_webView.getvalue().decode())
        layout.addWidget(webView)

        #setup Thread***************************************************
        self.work=TakeData_Thread()
        self.work.receive_time_from_Init(time_cost_HeatMap,time_cost_loc)
        self.work.start()
        self.work.trigger.connect(self.Display)
        #****************************************************************
        QtWidgets.QApplication.processEvents()
    def Display(self,data,data2):
        layout.takeAt(0).widget().deleteLater()#delete previous map

        #input data to folium's map pakage and set some Marker******************************************
        fmap = folium.Map(location=[22.996363580424514, 120.21903238440177], zoom_start=17)
        HeatMap(data,min_opacity=0.4,blur=50,radius=50).add_to(fmap)

        html =   '''<font face="微軟正黑體"><font size="4">雲平大樓:</font>
                    ''' + str(data2[0][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m0 = folium.Marker(location=[22.99891110398634, 120.21723168980603],popup=popup)

        html =   '''<font face="微軟正黑體"><font size="4">資工系館:</font>
                    ''' + str(data2[1][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m1 = folium.Marker(location=[22.99726633629006, 120.2212997328783],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">修齊大樓:</font>
                    ''' + str(data2[2][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m2 = folium.Marker(location=[23.00085204740406, 120.21786248420196],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">計網中心:</font>
                    ''' + str(data2[3][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m3 = folium.Marker(location=[22.99811369711759, 120.2184468855774],popup=popup)

        html =   '''<font face="微軟正黑體"><font size="4">光復機車:</font>
                    ''' + str(data2[4][1])
        iframe = folium.IFrame(html,width=160,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m4 = folium.Marker(location=[22.99677295694284, 120.2164651939948],popup=popup)
        html =   '''<font face="微軟正黑體"><font size="4">光一舍:</font>
                    ''' + str(data2[5][1])
        iframe = folium.IFrame(html,width=150,height=40)
        popup = folium.Popup(iframe,show=True,max_width=200,max_height=200)
        m5 = folium.Marker(location=[22.999008047465647, 120.21451704980048],popup=popup)

        fmap.add_child(child=m0)
        fmap.add_child(child=m1)
        fmap.add_child(child=m2)
        fmap.add_child(child=m3)
        fmap.add_child(child=m4)
        fmap.add_child(child=m5)
        #***********************************************************************************
        data_for_webView = io.BytesIO()
        fmap.save(data_for_webView,close_file=False)
        webView=QtWebEngineWidgets.QWebEngineView()
        webView.setHtml(data_for_webView.getvalue().decode())
        layout.addWidget(webView)
        QtWidgets.QApplication.processEvents()
        
if __name__=='__main__':
    app = QApplication(sys.argv)
    w=Window()
    w.show()
    w.showMaximized()
    sys.exit(app.exec_())
    