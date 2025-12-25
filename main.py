import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MSSQL Schema Compare")
    
    window = MainWindow()
    window.show()
    
    # print("Application Initialized")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
