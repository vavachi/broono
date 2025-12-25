import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Broono")
    
    # Cerulean Light (Soft Blue) Stylesheet
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #f0f7ff;
            color: #1e3a8a;
        }
        
        QWidget {
            color: #1e3a8a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        QGroupBox {
            border: 1px solid #bcd6f5;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #e0efff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #3b82f6;
            font-weight: 700;
        }

        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 6px;
            padding: 7px 16px;
            color: #ffffff;
            font-weight: 600;
        }
        
        QPushButton:hover {
            background-color: #60a5fa;
        }
        
        QPushButton:pressed {
            background-color: #2563eb;
        }
        
        QPushButton:disabled {
            background-color: #dbeafe;
            color: #93c5fd;
            border: 1px solid #bfdbfe;
        }

        QLineEdit, QTextEdit, QTreeWidget {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 6px;
            color: #0f172a;
            selection-background-color: #bfdbfe;
            selection-color: #1e3a8a;
        }
        
        QLineEdit:focus, QTextEdit:focus, QTreeWidget:focus {
            border: 1px solid #3b82f6;
        }

        QTreeWidget::item:selected {
            background-color: #dbeafe;
            color: #1e3a8a;
            border-radius: 4px;
        }

        QHeaderView::section {
            background-color: #f0f7ff;
            color: #64748b;
            padding: 6px;
            border: none;
            border-bottom: 1px solid #cbd5e1;
            border-right: 1px solid #cbd5e1;
            font-weight: bold;
        }

        QScrollBar:vertical {
            border: none;
            background: #f0f7ff;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            min-height: 20px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }

        QSplitter::handle {
            background-color: #cbd5e1;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            selection-background-color: #dbeafe;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    # print("Application Initialized")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
