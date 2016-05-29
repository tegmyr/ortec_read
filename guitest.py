#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 15:48:20 2016

 TODO: read_chn reads the .chn file header correctly. The number of channels 
       can now be accessed and used instead of being set manually. This is not  
       done yet though.
 
 TODO: The find_peak function does not find all peaks. Find better way to 
       determine  what is a peak. 
       
 TODO: Implement peakfitting and background subtraction from peaks. 
 
 Idea for end guesser. 
 I want to create the functionality that given peak areas, efficiency curve 
 and connectivity to DB, get a fairly good guess what kind of nuclide and thus 
 also the activity. 
 
 





@author: Oscar Tegmyr
oscar.tegmyr@gmail.com
"""
import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import spectrum_analysis as sa
import fit_peak
import read_chn
import numpy as np
# ==== parameters, these will be stored in a separate file === 
color_hist = 'b'
color_bg_hist = 'r'
filled_hist = False
filled_bg_hist = False
spectrum_cal_slope = 1
spectrum_cal_offset = 0
bg_cal_slope = 1
bg_cal_offset = 0

# ================















def load_spec(fname):    
    spec_obj    = read_chn.gamma_data(fname)
    spec_array  = spec_obj.hist_array
    spec_time   = spec_obj.real_time   
    spec_array_step = np.append(0,spec_array)
    x = np.arange(len(spec_array))
    x_step = np.arange(len(spec_array)+1)-0.5   
    en = x*spec_obj.en_slope + spec_obj.en_zero_inter + x**2*spec_obj.en_quad
    en_step = x_step*spec_obj.en_slope + spec_obj.en_zero_inter + x_step**2*spec_obj.en_quad
    return spec_array, spec_array_step, en, en_step, spec_time

class MyMplCanvas(FigureCanvas):
    #Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    def __init__(self, parent=None, width=20, height=4, dpi=100):
        fig         = Figure(figsize=(width, height), dpi=dpi)
        self.axes   = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        
    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    def compute_initial_figure(self):    
        self.axes.plot()
        
       


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #=== Menubar === 
        self.setup_menu_bar()
        # Setup actions! 
        peak_find_action = QtGui.QAction('Find Peaks',self)      
        peak_find_action.setShortcut('Ctrl+f')
        peak_find_action.triggered.connect(self.find_roi)
        
        zoom_out_action = QtGui.QAction('Zoom Out',self) 
        zoom_out_action.triggered.connect(self.zoom_out)
        
        zoom_action =  QtGui.QAction('Zoom',self) 
        zoom_action.setShortcut('z')
        zoom_action.triggered.connect(self.activate_zoom)
        
        toggle_lin_log_action = QtGui.QAction('Log',self)
        toggle_lin_log_action.triggered.connect(self.logarithmic)

        self.toolbar = self.addToolBar('Find peak')
        self.toolbar.addAction(peak_find_action)
        self.toolbar.addAction(zoom_out_action)
        self.toolbar.addAction(zoom_action)
        self.toolbar.addAction(toggle_lin_log_action)
        self.main_widget    = QtGui.QWidget(self)
        l                   = QtGui.QHBoxLayout(self.main_widget)
        self.sc             = MyStaticMplCanvas(self.main_widget, width=100, height=6, dpi=100)
        self.slider         = QtGui.QSlider(self.main_widget)
        l.addWidget(self.sc)
        l.addWidget(self.slider)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.ymax = 5000 
        self.x_limits=[0,8192]
        self.y_limits=[0.1,]
           
           
           
         
#    def setup_toolbar(self):
    def setup_menu_bar(self):
        self.menuBar        = QtGui.QMenuBar()
        self.file_menu      = QtGui.QMenu('&File', self)
        self.settings_menu  = QtGui.QMenu('&Settings', self)
        self.analysis_menu  = QtGui.QMenu('&Analysis', self)
        self.help_menu      = QtGui.QMenu('&Help', self)
        self.menuBar.addMenu(self.file_menu)
        self.menuBar.addMenu(self.settings_menu)
        self.menuBar.addMenu(self.analysis_menu)
        self.menuBar.addMenu(self.help_menu)
        self.file_menu.addAction('&Load spectrum', self.file_load_spec)
        self.file_menu.addAction('&Export spectrum', self.file_load_spec)
        self.analysis_menu.addAction('&Zoom', self.activate_zoom)
        self.analysis_menu.addAction('&Find Roi', self.find_roi)
        self.analysis_menu.addAction('&Load background spectrum', self.file_load_background)      
        self.analysis_menu.addAction('&Logartihmic', self.logarithmic)
        
        
        
        
    def file_load_spec(self):
        self.file_name  = QtGui.QFileDialog.getOpenFileName(self,"Load Spectrum File", "/home","Spectrum Files (*.chn *.bin)");           
        self.array,self.array_step, self.en, self.en_step, self.spectrum_time  = load_spec(self.file_name)
        self.x_limits   = [0,self.en_step[-1]]
        self.y_limits   = [0.1, np.max(self.array)*1.2 ]
        self.draw_spectrums()

        
    def file_load_background(self):
        self.file_name_bg           = QtGui.QFileDialog.getOpenFileName(self,"Load Spectrum File", "/home","Spectrum Files (*.chn *.bin)");    
        self.bg_spec, self.bg_time  = load_spec(self.file_name_bg)
        self.ymax                   = np.max(self.bg_spec)      
        self.draw_spectrums()
        
    def draw_spectrums(self):     
        if hasattr(self,'bg_spec') and hasattr(self,'array')  :
            x_bg        = np.arange(len(self.bg_spec))
            time_factor = self.spectrum_time/float(self.bg_time)
            self.sc.axes.step(x_bg,1.2*time_factor*self.bg_spec,c=color_bg_hist)#TODO: Make sure the step setup is okey! 
            self.sc.axes.hold(True)
            print self.bg_time
        if hasattr(self,'array') :  
            self.sc.axes.step(self.en_step,self.array_step,c=color_hist)#TODO: Make sure the step setup is okey! 
            print self.spectrum_time
        self.sc.axes.set_xlim(self.x_limits[0],self.x_limits[1])
        self.sc.axes.set_ylim(self.y_limits[0], self.y_limits[1])        
        self.sc.draw()

    def activate_zoom(self): 
        #TODO: Draw rectangle when zooming   
        self.cid_click = self.sc.mpl_connect('button_press_event', self.on_click)
        self.cid_release = self.sc.mpl_connect('button_release_event', self.on_release)
   
    def on_click(self, click) :
        self.sc.zoom_point1 = [click.xdata,click.ydata]
        
    def on_release(self, release):
        self.sc.zoom_point2 = [release.xdata,release.ydata]
        #Put control for too small values 
        if np.abs(self.sc.zoom_point2[0]-self.sc.zoom_point1[0]) > 10 and np.abs(self.sc.zoom_point2[1]-self.sc.zoom_point1[1])>10:
            self.zoom(np.sort([self.sc.zoom_point2[0],self.sc.zoom_point1[0]]),np.sort([self.sc.zoom_point2[1],self.sc.zoom_point1[1]]))
        self.sc.mpl_disconnect(self.cid_click)
        self.sc.mpl_disconnect(self.cid_release)


    def logarithmic(self):
        self.sc.axes.set_yscale('log')
        self.sc.draw()  
    def zoom_out(self):
        self.zoom([0,self.en_step[-1]],[0.1, np.max(self.array)*1.2 ])
        
    def zoom(self,xlimits, ylimits):
        self.x_limits = xlimits
        self.y_limits = ylimits
        print self.x_limits 
        self.draw_spectrums()
        
    def find_roi(self):
        #The Second time you activate this the plot disappears
        self.rois = sa.peak_finder(self.array)
        self.sc.axes.hold()
        self.sc.axes.scatter(self.en[self.rois], self.array[self.rois],marker='x',c='r',s=40)
        self.draw_spectrums()
        
    def fit_peak(self, en_low, en_high):
        rang = np.linspace(en_low,en_high)
        plt.figure(3)
        plt.scatter(rang,self.array[rang])
        plt.ylim(ymin=1)
        print fit_peak.fit_the_peak(rang,self.array[rang])
        coeff, var_matrix, hist_fit = fit_peak.fit_the_peak(rang,self.array[rang])
        plt.plot(rang, hist_fit)
        plt.show()
        
        





qApp    = QtGui.QApplication(sys.argv)
aw      = ApplicationWindow()
aw.setWindowTitle('Ortec GUI')
aw.show()
sys.exit(qApp.exec_())
