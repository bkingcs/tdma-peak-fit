from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame


class TitleHLine(QWidget):
    """
    Creates a widget that can be used to create a title that is centered with a horizontal line on
    both sides of it.

    :param str title: The title to appear centered between the horizontal lines
    """
    def __init__(self, title):
        super(self.__class__, self).__init__()
        h_layout = QHBoxLayout()
        h_layout.addWidget(HLineRaised())
        h_layout.addWidget(QLabel(title))
        h_layout.addWidget(HLineRaised())
        self.setLayout(h_layout)

class VLineSunk(QFrame):
    """
    Creates a vertical line QFrame.
    """
    def __init__(self):
        super(VLineSunk, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class HLineRaised(QFrame):
    """
    Creates a widget that can be used to create a horizontal line
    """
    def __init__(self):
        super(HLineRaised, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Raised)