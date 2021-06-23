from re import S
from PyQt5 import QtWidgets, uic, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from pyqtgraph.functions import disconnect
import globals
from avaspec import *
import time
import math
from ui_functions import *
from ui_main import Ui_MainWindow
import json 

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        ## LOAD THE UI PAGE
        ######################################################################## 
        uic.loadUi('ui_main.ui', self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## TOGGLE/BURGUER MENU
        ########################################################################
        self.ui.Btn_Toggle.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_page_1.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_1))
        self.ui.connectButton.clicked.connect(self.connectButton_clicked)

        # PAGE 2
        self.ui.btn_page_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_2))

        # PAGE 3
        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_3))


        # makes sure that the inital page that the GUI displays is page 1. 
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)


        ## initalize the inital globals
        ########################################################################
        globals.integration_time = 10
        globals.averages = 5
        globals.first = True 

        # set all the buttons that should be enabled or not
        # self.startStopButton.setEnabled(False)
        # self.darkButton.setEnabled(False)
        # self.configButton.setEnabled(False)
        # self.refButton.setEnabled(False)

        # make all the connections
        #######################################################################
        self.ui.connectButton.clicked.connect(lambda: self.connectButton_clicked)
        self.ui.startStopButton.clicked.connect(self.startStopButton_clicked)
        self.ui.darkButton.clicked.connect(self.darkButton_clicked)
        self.ui.refButton.clicked.connect(self.refButton_clicked)
        self.ui.configButton.clicked.connect(self.configButton_clicked)
        self.ui.stopButton.clicked.connect(self.stopButton_clicked)
        self.ui.scopeModeButton.clicked.connect(self.scope)
        self.ui.scopeMinDarkButton.clicked.connect(self.scopeMinDarkButton_clicked)
        self.ui.absButton.clicked.connect(self.absButton_clicked)
        self.ui.reflectButton.clicked.connect(self.reflectButton_clicked)
        self.ui.saveButton.clicked.connect(self.saveButton_clicked)
        self.ui.transButton.clicked.connect(self.transButton_clicked)
        self.ui.collectButton_2.clicked.connect(self.startStopButton_clicked)
        self.ui.scaleButton.clicked.connect(self.scaleButton_clicked)
        self.ui.absIrrButton.clicked.connect(self.absIrrButton_clicked)
        self.ui.relIrrButton.clicked.connect(self.relIrrButton_clicked)

        # show the screen
        #######################################################################
        self.show()



    #   Adding all the clicked button functionality 
    #
    #
    #
    #
    @pyqtSlot()
    def absIrrButton_clicked(self):
        print("abs Irr")

    @pyqtSlot()
    def relIrrButton_clicked(self):
        print("rel Irr")

    @pyqtSlot()
    def scaleButton_clicked(self):
        print("scale")
        print("this doesnt work")
        return
        self.ui.graphWidget.ViewBox()
        self.ui.graphWidget_2.ViewBox()


    @pyqtSlot()
    def transButton_clicked(self):
        globals.visGraph = 4
        y_value = []
        y_label = "Percentage (%)"
        title = "Transmission Mode"
        for x in range(0, len(globals.spectraldata)-2):
            y_value.append(100*((globals.spectraldata[x]-globals.darkData[x])/(globals.refData[x]-globals.darkData[x])))
        self.plot(y_value, y_label, title)

    @pyqtSlot()
    def absButton_clicked(self):
        globals.visGraph = 3
        y_value = []
        y_label = "Absorbance (A.U.)"
        title = "Absorbance Mode"
        for x in range(0, len(globals.spectraldata)-2):
            # seems that im grabbing outside pixels making the end of the graph bad... will have to look into it. 
            if math.fabs(globals.refData[x]-globals.darkData[x]) == 0:
                y_value.append(5)
                print("divide by zero")
            elif (math.fabs(globals.spectraldata[x]-globals.darkData[x]))/(math.fabs(globals.refData[x]-globals.darkData[x])) <= 0:
                y_value.append(5)
                print("domain = 0")
            else:
                y_value.append( -1 * math.log((math.fabs(globals.spectraldata[x]-globals.darkData[x]))/(math.fabs(globals.refData[x]-globals.darkData[x])),10))

        self.plot(y_value, y_label, title)

    @pyqtSlot()
    def reflectButton_clicked(self):
        globals.visGraph = 5
        y_value = []
        y_label = "Percent (%)"
        title = "Reflectance Mode"
        for x in range(0,len(globals.spectraldata)-2):
            y_value.append( 100*((globals.spectraldata[x]-globals.darkData[x])/(globals.refData[x]-globals.darkData[x])) )
        self.plot(y_value, y_label, title)


    @pyqtSlot()
    def darkButton_clicked(self):
        globals.darkData = globals.spectraldata
        print("darkData now saved")

    @pyqtSlot()
    def stopButton_clicked(self):
        AVS_Done()
        # self.startStopButton.setEnabled(False)
        # self.connectButton.setEnabled(True)
        # self.darkButton.setEnabled(False)
        # self.configButton.setEnabled(False)
        # self.refButton.setEnabled(False)
        print("disconnected")

    @pyqtSlot()
    def refButton_clicked(self):
        globals.refData = globals.spectraldata
        print("reference data now saved")


    ############################################################################################    
    # this is a little glitchy 
    # this is a little glitchy 
    # this is a little glitchy
    # this is a little glitchy
    # seems that the dark reading is just noise and increasing the integration time has no effect on it
    # not sure how to solve this just yet
    # if it continues on without stopping or coming out of the loop the device needs to be disconnected and then reconnected
    # the above should get fixed
    @pyqtSlot()
    def configButton_clicked(self):
        print("configuration")

        largest_pixel = 0
        count = 0
        increment = 5
        if globals.integration_time <= 5 and globals.integration_time > 1:
            increment = 1
        elif globals.integration_time <= 1 and globals.integration_time > 0.2:
            increment = 0.5
        while( largest_pixel > 60000 or largest_pixel < 55000 ):
            largest_pixel = 0
            for x in range(0, len(globals.spectraldata)-2):
                if(globals.spectraldata[x] > largest_pixel):
                    largest_pixel = globals.spectraldata[x]
    
            if globals.integration_time <= 0:
                globals.integration_time = math.fabs(globals.integration_time)

            if globals.integration_time - increment <= 0:
                increment = increment / 2

            if(largest_pixel > 60000):
                # lower the integration time:
                globals.integration_time = globals.integration_time - increment

            if(largest_pixel < 55000):
                # increase integration time: 
                globals.integration_time = globals.integration_time + increment

            QtWidgets.QApplication.processEvents()                                        # This works. however ew. 
            count += 1
            if count == 100:
                break
            self.startStopButton_clicked()
        print(largest_pixel)
        globals.max = largest_pixel
        
        count = 0
        cycle_time = globals.integration_time * globals.averages
        while( cycle_time > 580 or cycle_time < 420):
            cycle_time = globals.integration_time * globals.averages
            if cycle_time > 550: 
                globals.averages -= 1 
            if cycle_time < 450: 
                globals.averages += 1
            self.startStopButton_clicked()
            count += 1 
            if count >= 50:
                break
        print("done with configuration")
        print(globals.integration_time)
        print(globals.averages)
        

    @pyqtSlot()
    def startStopButton_clicked(self):
        # self.startStopButton.setEnabled(False)
        self.repaint()                                                                      # gets rid of old data on the screen
        ret = AVS_UseHighResAdc(globals.dev_handle, True)                                   # sets the spectrometer to use 16 bit resolution instead of 14 bit
        measconfig = MeasConfigType()
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = globals.pixels - 1
        measconfig.m_IntegrationTime = globals.integration_time                                                    # variables that will get changed
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = globals.averages                                                         # variables that will get changed
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 0.0
        measconfig.m_Control_m_StoreToRam = 0
        ret = AVS_PrepareMeasure(globals.dev_handle, measconfig)
        nummeas = 1                                                                         # variables that will get changed

        scans = 0                                                                           # counter
        globals.stopscanning = False                                                        # dont want to stop scanning until we say so
        while (globals.stopscanning == False):                                              # keep scanning until we dont want to anymore
            ret = AVS_Measure(globals.dev_handle, 0, 1)                                     # tell it to scan
            dataready = False                                                               # while the data is false
            while (dataready == False):
                dataready = (AVS_PollScan(globals.dev_handle) == True)                      # get the status of data
                time.sleep(0.001)
            if dataready == True:
                ret = AVS_GetScopeData(globals.dev_handle)
                globals.spectraldata = ret[1]
                scans = scans + 1
                if (scans >= nummeas):
                    globals.stopscanning = True  
            # self.app.processEvents()                          ##########################################      look into this line
            time.sleep(0.001)  

        # self.darkButton.setEnabled(True)
        # self.configButton.setEnabled(True)
        # self.refButton.setEnabled(True)
        # self.startStopButton.setEnabled(True)
        globals.measureType = measconfig

        # while globals.first == True:
        #     self.plot_scope()
        #     globals.first = False

        # if globals.visGraph == 1:
        #     print()
        #     self.scope()
        # elif globals.visGraph == 2:
        #     print()
        #     self.scopeMinDarkButton()
        # elif globals.visGraph == 3:
        #     print()
        #     self.absButton()
        # elif globals.visGraph == 4:
        #     print()
        #     self.transButton()
        # elif globals.visGraph == 5:
        #     print()
        #     self.refButton()
        # elif globals.visGraph == 6:
        #     print()
        # elif globals.visGraph == 7:
        #     print()
        # else:
        #     print()
        self.scope()    

        return   

    @pyqtSlot()
    def connectButton_clicked(self):
        print("connected")
        # initialize the usb... were not gonna care about eithernet for now only usb
        ret = AVS_Init(0)                                                                                   # init(0) means were using a USB
                                                                                                            # will return the number of devices on success this should be 1 

        ret = AVS_GetNrOfDevices()                                                                          # will check the list of connected usb devices and returns the number attached   
        mylist = AvsIdentityType()                                                                          # pretty sure these do the same thing but whatever you know it works
        mylist = AVS_GetList(1)          
        globals.identity = mylist                                                                   
        # may need to come back and see what this function does

        # displaying information on the serial number and working with it
        serienummer = str(mylist[0].SerialNumber.decode("utf-8"))


        # this activates the spectrometer for communication
        globals.dev_handle = AVS_Activate(mylist[0])

        # gets all the information about the spectrometer
        devcon = DeviceConfigType()
        devcon = AVS_GetParameter(globals.dev_handle, 63484)
        globals.pixels = devcon.m_Detector_m_NrPixels
        globals.wavelength = AVS_GetLambda(globals.dev_handle)
        # for x in globals.wavelength:
        #     print(x)

        # change if the button should be able to be used or not 
        # self.startStopButton.setEnabled(True)
        # self.connectButton.setEnabled(False)

        return

    @pyqtSlot()
    def scopeMinDarkButton_clicked(self):
        globals.visGraph = 2
        y_value = []
        title = "Scope Minus Dark"
        y_label = "Counts"
        for x in range(0, len(globals.spectraldata)-2):
            y_value.append(globals.spectraldata[x]-globals.darkData[x])
        self.plot(y_value, y_label, title)

    @pyqtSlot()
    def saveButton_clicked(self):
        print("Save Button clicked")
        # may need to add a path variable so you can choose where the file gets saved. 
        # would like to open another window to get all the infromation that is need when saving basically the name
        # need to save to the right file extension depending on the graph they want
        #
        #
        #
        ########################################## 

        data = {
            "length": 0, 
            "seqnum": 0, 
            "measmode": 0, 
            "bitness": 0,
            "SDmarker": 0, 
            "identity": AvsIdentityType(),
            "measconf": MeasConfigType(),
            "timestamp": 0,
            "SPCfiledate": 0,
            "detectortemp": 0,
            "boardtemp": 0,
            "NTC2volt": 0, 
            "ColorTemp": 0,
            "CalIntTime": 0,
            "fitdata": 0, 
            "comment": 0, 
            "xcoord": 0, 
            "scope": 0,
            "dark": 0,
            "reference": 0,
            "mergegroup": 0,
            "straylightconf": 0,
            "nonlinconf": 0,
            "CustomReflectance": 0, 
            "CustomWhiteRefValue": 0,
            "CustomDarkRefValue": 0
        }

        ##########################################
        #
        #
        #

        fileName = "saveFile"
        extension = ""
        measureMode = ""
        choice = 0
        if(choice == 0):
            extension = ".raw8"
            measureMode = "00000000"
        elif choice == 1:
            extension = ".rwd8"
            measureMode = "00000010"
        elif choice == 2:
            extension = ".abs8"
            measureMode = "00000001"
        elif choice == 3:
            extension = ".trm8"
            measureMode = "00000011"
        elif choice == 4:
            extension = ".irr8"
            measureMode = "00000101"
        elif choice == 5:
            extension = ".rfl8"
            measureMode = "00000100"
        elif choice == 6:
            extension = ".rir8"
            measureMode = "00000110"
        else:
            extension = ".raw8"
            measureMode = "00000000"
            print("ERROR: DIDN'T FIND FILE TYPE SPECIFIED")

        with open(fileName + extension, "w") as file:
            # Marker
            file.write("\\")
            file.write("01000001")
            file.write("01010110")
            file.write("01010011")
            file.write("00111000")
            file.write("00110100")
            # Number of spectra 
            file.write("\\")
            file.write("00000001")
            # length
            # seqnum
            file.write("\\")
            file.write("00000000")
            file.write("\\")
            # measure mode 
            file.write(measureMode)
            file.write("\\")
            # bitness
            file.write("00000001")
            file.write("\\")
            #SDmarker
            file.write("00000000")
            file.write("\\")
            #identity                                                                          # this may need to be 10 long intead of 9
                #serial number
            for x in range(0, len(globals.identity[0].SerialNumber)):
                # print(eightBits(str(decimalToBinary(globals.identity[0].SerialNumber[x]))))
                file.write(eightBits(str(decimalToBinary(globals.identity[0].SerialNumber[x]))))
                    # has to print 
                # user friendly name
            for x in range(0,64):
                if x < 10:
                    if x < len(globals.identity[0].UserFriendlyName):
                        file.write(decimalToBinary(globals.identity[0].UserFriendlyName[x]))
                    else:
                        file.write("00000000")
                else:
                    file.write("00000000")
                # status
            file.write("\\")
            for x in globals.identity[0].Status:
                # print(eightBits(decimalToBinary(x)))
                file.write(eightBits(decimalToBinary(x)))
            #meascong
            # file.write(decimalToBinary(int(globals.MeasConfigType.m_StartPixel)))
            print()
            x = (json.decoder(globals.MeasConfigType.m_StartPixel))
            print(x)

            print()
            # file.write(decimalToBinary(globals.MeasConfigType.m_StopPixel))
            print(globals.MeasConfigType.m_StopPixel)
            # file.write(decimalToBinary(globals.MeasConfigType.m_IntegrationTime))
            print(globals.MeasConfigType.m_IntegrationTime)
            # file.write(decimalToBinary(globals.MeasConfigType.m_IntegrationDelay))
            print(globals.MeasConfigType.m_IntegrationDelay)
            # file.write(decimalToBinary(globals.MeasConfigType.m_NrAverages))
            print(globals.MeasConfigType.m_NrAverages)
            # file.write(decimalToBinary(globals.MeasConfigType.m_CorDynDark_m_Enable))
            print(globals.MeasConfigType.m_CorDynDark_m_Enable)
            # file.write(decimalToBinary(globals.MeasConfigType.m_Smoothing_m_SmoothPix))
            print(globals.MeasConfigType.m_Smoothing_m_SmoothPix)
            # file.write(decimalToBinary(globals.MeasConfigType.m_SaturationDetection))
            print(globals.MeasConfigType.m_SaturationDetection)
            # file.write(decimalToBinary(globals.MeasConfigType.m_Trigger_m_Mode))
            print(globals.MeasConfigType.m_Trigger_m_Mode)
            # file.write(decimalToBinary(globals.MeasConfigType.m_Control_m_StrobeControl))
            print(globals.MeasConfigType.m_Control_m_StrobeControl)

            #timestamp
            #SPCfiledate
            #detectortemp
            #boardtemp
            #NTC2volt
            #colorTemp
            #calIntTime
            #fitdata
            #comment
            #xcoord
            #scope
            #dark
            #reference
            #mergegroup
            #straylightconf
            #nonlincong
            #customReflectance
            #customWhiteRefValue
            #customDarkRefValue


    #   clicked button functionality
    #
    #
    #
    #   

    def scope(self):
        # get the values
        globals.visGraph = 1
        y_value = []
        for x in range(0,len(globals.spectraldata)-2):                                  # dropping off the last two data points
            y_value.append(globals.spectraldata[x])
        self.plot(y_value, "Scope (ADC Counts)", "Scope Mode")

    def plot(self, y_value, y_label, title):
        # get the values
        x_value = []
        for x in range(0,len(globals.wavelength)-2):                                    # not sure if this is going to effect it but dropping off the last two data points
            x_value.append(globals.wavelength[x])
        
        # Set the label for x axis
        self.ui.graphWidget.setLabel('bottom', 'Wavelength (nm)')
        self.ui.graphWidget_2.setLabel('bottom', 'Wavelength (nm)')


        # Set the label for y-axis
        self.ui.graphWidget.setLabel('left', y_label)
        self.ui.graphWidget_2.setLabel('left', y_label)

        # Set the title of the graph
        self.ui.graphWidget.setTitle(title)
        self.ui.graphWidget_2.setTitle(title)

        self.ui.graphWidget.clear()
        self.ui.graphWidget.plot(x_value, y_value)

        self.ui.graphWidget_2.clear()
        self.ui.graphWidget_2.plot(x_value, y_value)



#
#
#   This function takes the input and converts it to binary 
#
#

def decimalToBinary(n):
    # this thing returns a string
    return bin(n).replace("0b", "")

def eightBits(n):
    if len(n) == 1:
        n = "0000000" + n
    elif len(n) == 2:
        n = "000000" + n
    elif len(n) == 3:
        n = "00000" + n
    elif len(n) == 4:
        n = "0000" + n
    elif len(n) == 5:
        n = "000" + n
    elif len(n) == 6:
        n = "00" + n
    elif len(n) == 7:
        n = "0" + n
    else:
        print("fell into the else")
        return n
    return n

#
#
#
#

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
