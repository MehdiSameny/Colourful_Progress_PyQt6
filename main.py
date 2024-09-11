# ///////////////////////////////////////////////////////////////
# Developer: Mehdi Sameni
# Designer: Mehdi Sameni
# PyQt6
# Python 3.10
# other module : perlin_noise
# ///////////////////////////////////////////////////////////////

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QSlider
from PyQt6.QtGui import QColor
from ColourfulProgress import ColourfulProgress



if __name__ == '__main__':
    import cgitb
    import sys

    cgitb.enable(format='text')
    app = QApplication(sys.argv)

    w = QWidget()
    layout = QGridLayout(w)

    w1 = ColourfulProgress(color=QColor('#85c440'))
    w1.setOrient(Qt.Orientation.Horizontal)
    w1.setMinimumWidth(300)
    w1.setMaximumWidth(300)
    w1.setRange(0, 100)
    layout.addWidget(w1, 0, 0, 1, 1)

    w2 = ColourfulProgress(color=QColor('#f2b63c'))
    w2.setOrient(Qt.Orientation.Horizontal)
    w2.setMinimumWidth(300)
    w2.setMaximumWidth(300)
    w2.setInvertedAppearance(True)
    w2.setRange(0, 100)
    layout.addWidget(w2, 1, 0, 1, 1)

    w3 = ColourfulProgress(color=QColor('#db3a27'))
    w3.setOrient(Qt.Orientation.Vertical)
    w3.setMinimumHeight(300)
    w3.setMaximumHeight(300)
    w3.setRange(0, 100)
    layout.addWidget(w3, 0, 1, 2, 1)

    w4 = ColourfulProgress(color=QColor('#5aaadb'))
    w4.setOrient(Qt.Orientation.Vertical)
    w4.setMinimumHeight(300)
    w4.setMaximumHeight(300)
    w4.setInvertedAppearance(True)
    w4.setRange(0, 100)
    layout.addWidget(w4, 0, 2, 2, 1)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.valueChanged.connect(w1.setValue)
    slider.valueChanged.connect(w2.setValue)
    slider.valueChanged.connect(w3.setValue)
    slider.valueChanged.connect(w4.setValue)
    slider.setValue(50)
    layout.addWidget(slider, 2, 0, 1, 3)

    w.show()

    sys.exit(app.exec())
