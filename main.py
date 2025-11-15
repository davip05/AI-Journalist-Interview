# main.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from main_window import ElectionSimulator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 249, 255))
    palette.setColor(QPalette.WindowText, QColor(40, 44, 52))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 245, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(40, 44, 52))
    palette.setColor(QPalette.Text, QColor(40, 44, 52))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(40, 44, 52))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = ElectionSimulator()
    window.show()
    sys.exit(app.exec_())