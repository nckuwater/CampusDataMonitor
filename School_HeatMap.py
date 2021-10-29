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
class Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("People_Heat_Map")
        self.resize(640, 480)
        self.setLayout(layout)
        data =Take_data.Take_Data_Now(cdm)
        data2 = campus_data_monitor.Take_Data_Now(cdm2)
        fmap = folium.Map(location=[22.996363580424514, 120.21903238440177], zoom_start=17)
        HeatMap(data,min_opacity=0.4,blur=50,radius=50).add_to(fmap)
        fmap.save("test.html")
        #folium.Marker(location=[22.99891110398634, 120.21723168980603],popup='<i>雲平大樓：<i>').add_to(fmap)


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
        fmap.add_child(child=m0)
        fmap.add_child(child=m1)
        fmap.add_child(child=m2)
        fmap.add_child(child=m3)


        data2 = io.BytesIO()
        fmap.save(data2,close_file=False)
        webView=QtWebEngineWidgets.QWebEngineView()
        webView.setHtml(data2.getvalue().decode())
        layout.addWidget(webView)
        self.Update()
        QtWidgets.QApplication.processEvents()

    def Update(self):
        self.timer=QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(15000)
        QtWidgets.QApplication.processEvents()
    def run(self):
        Data =Take_data.Take_Data_Now(cdm)
        data2 = campus_data_monitor.Take_Data_Now(cdm2)
        
        fmap = folium.Map(location=[22.996363580424514, 120.21903238440177], zoom_start=17)
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
        fmap.add_child(child=m0)
        fmap.add_child(child=m1)
        fmap.add_child(child=m2)
        fmap.add_child(child=m3)

        HeatMap(Data,min_opacity=0.4,blur=50,radius=50).add_to(fmap)
        data2 = io.BytesIO()
        fmap.save(data2,close_file=False)
        webView=QtWebEngineWidgets.QWebEngineView()
        webView.setHtml(data2.getvalue().decode())
        layout.takeAt(0).widget().deleteLater()
        layout.addWidget(webView)
        QtWidgets.QApplication.processEvents()
        
if __name__=='__main__':
    app = QApplication(sys.argv)
    w=Window()
    w.show()
    w.showMaximized()
    sys.exit(app.exec_())
    

    
