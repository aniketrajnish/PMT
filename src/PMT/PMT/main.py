import sys
from PyQt5.QtWidgets import *
from gui import PMTWindow

#-----------------------------------------------------------------------------------
# The main function that runs the PMT application
#-----------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    pmt = PMTWindow()    
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()  