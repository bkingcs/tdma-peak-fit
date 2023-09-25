from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QSlider
)

from htdma_code.view.helper_widgets import TitleHLine
import htdma_code.model.model as model_pkg

class DMA_1_Form(QFormLayout):
    """
    Our primary container for showing the DMA 1 tab
    """

    def __init__(self, parent, model: model_pkg.Model):
        super().__init__(parent)

        self.model = model

        self._create_form_widgets()
        self._add_widgets_to_form()

    def _create_form_widgets(self):
        self.dma_1_name_label = QLabel()
        self.dma_1_name_label.setText("-- not loaded --")
        self.dma_1_name_label.setStyleSheet("border: 1px solid black")
        self.q_sh_lineedit = QLineEdit()
        self.q_sh_lineedit.setText("0.0")

        self.q_aIn_lineedit = QLineEdit()
        self.q_aIn_lineedit.setText("0.0")

        self.q_aOut_lineedit = QLineEdit()
        self.q_aOut_lineedit.setText("0.0")

        self.q_excess_lineedit = QLineEdit()
        self.q_excess_lineedit.setText("0.0")

        self.voltage_lineedit = QLineEdit()
        self.voltage_lineedit.setText("0")

        self.voltage_slider = QSlider(Qt.Horizontal)
        self.voltage_slider.setMinimum(0)
        self.voltage_slider.setMaximum(10000)
        self.voltage_slider.setValue(0)
        self.voltage_slider.setTickPosition(QSlider.TicksBelow)
        self.voltage_slider.setTickInterval(2500)

        self.dp_center_label = QLabel("0")
        self.dp_range_label = QLabel("[ 0 - 0 ]")
        self.dp_spread_label = QLabel("0")

    def _add_widgets_to_form(self):
        """
        Add all of the widgets that were already created to the form
        """
        # Start adding info
        self.addRow("Name", self.dma_1_name_label)
        self.addRow(TitleHLine("Flow settings"))
        self.addRow("Sheath Flow", self.q_sh_lineedit)
        self.addRow("Aerosol In", self.q_aIn_lineedit)
        self.addRow("Aerosol Out", self.q_aOut_lineedit)
        self.addRow("Excess Out", self.q_excess_lineedit)
        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Voltage"))
        self.addRow("Voltage", self.voltage_lineedit)
        self.addRow(self.voltage_slider)
        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Theoretical dP Distribution"))
        self.addRow("dP (nm)", self.dp_center_label)
        self.addRow("dP range", self.dp_range_label)
        self.addRow("dp spread", self.dp_spread_label)


    def update_from_model(self):
        """
        Update all of the widgets based on the current values in
        the model
        """
        super().update()
        self.dma_1_name_label.setText(self.model.setup.basefilename)
        self.q_sh_lineedit.setText("{:.1f}".format(self.model.dma1.q_sh_lpm))
        self.q_aIn_lineedit.setText("{:.1f}".format(self.model.dma1.q_aIn_lpm))
        self.q_aOut_lineedit.setText("{:.1f}".format(self.model.dma1.q_aOut_lpm))
        self.q_excess_lineedit.setText("{:1f}".format(self.model.dma1.q_excess_lpm))
        self.voltage_lineedit.setText("{:.0f}".format(self.model.dma1.voltage))
        self.voltage_slider.setValue(self.model.dma1.voltage)

        self.dp_center_label.setText("{:.1f}".format(self.model.dma1.dp_dist_center))
        self.dp_range_label.setText("[ {:.1f} - {:.1f} ]".format(self.model.dma1.dp_dist_left_bottom, self.model.dma1.dp_dist_right_bottom))
        self.dp_spread_label.setText("{:.1f}".format(self.model.dma1.dp_dist_right_bottom - self.model.dma1.dp_dist_left_bottom))
