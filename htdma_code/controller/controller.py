
from PySide2.QtWidgets import QFileDialog
import PySide2.QtWidgets as Qw

from htdma_code.model.model import Model
from htdma_code.view.main_window import MainWindow

class Controller:
    def __init__(self,model: Model,main_view: MainWindow):
        self.model = model
        self.main_view = main_view
        self.status_bar = main_view.statusBar()

        # Set up the menu bindings
        self.main_view.file_open_action.triggered.connect(self.menu_file_open_action)

        # Voltage for dma 1
        self.main_view.dma_1_form.voltage_lineedit.returnPressed.connect(self.dma1_voltage_action)
        self.main_view.dma_1_form.voltage_slider.sliderReleased.connect(self.dma1_voltage_sliderReleased)

        # scan selections
        self.main_view.scan_form.prev_scan_button.clicked.connect(self.prev_scan_button_clicked)
        self.main_view.scan_form.next_scan_button.clicked.connect(self.next_scan_button_clicked)
        self.main_view.scan_form.rh_dspinbox.valueChanged.connect(self.rh_changed)

        # Peak fitting
        self.main_view.scan_form.peak_fit_button.clicked.connect(self.peak_fit_button_clicked)

        self.main_view.docker_tabs.currentChanged.connect(self.tab_changed)

    def menu_file_open_action(self):
        # """
        # Opens data files and begins the scan alignment process
        # """
        open_dir = "./data"
        # noinspection PyCallByClass
        files = QFileDialog.getOpenFileNames(self.main_view, "Open files", open_dir, "Data files (*.csv *.txt)")[0]
        if files:
            # read in the new file
            self.model.process_new_file(files[0])
            self.status_bar.showMessage("Read in file {}".format(files[0]))

            # Update the view
            self.main_view.update_from_model()
            # self.main_view.update_dma1_widget_views_from_model()
            # self.main_view.update_scan_widget_views_from_model()

    def dma1_voltage_action(self):
        """
        User pressed enter on a new value for voltage for DMA 1. Thus, update the model, then update the entire
        display
        """
        voltage = float(self.main_view.dma_1_form.voltage_lineedit.text())
        self.model.dma1.update_voltage(voltage)
        self.main_view.update_from_model()

        # self.main_view.update_dma1_widget_views_from_model()

    def dma1_voltage_sliderReleased(self):
        """
        User moved the slider to adjust the voltage
        """
        voltage = self.main_view.dma_1_form.voltage_slider.value()
        self.model.dma1.update_voltage(voltage)
        # self.main_view.update_dma1_widget_views_from_model()
        self.main_view.update_from_model()

    def prev_scan_button_clicked(self):
        if not self.model.current_scan:
            Qw.QMessageBox.warning(self.main_view,"No scans loaded!","Please load a file first")
        elif not self.model.select_prev_scan():
            Qw.QMessageBox.warning(self.main_view,"Warning!","No more scans available!")
        else:
            # self.main_view.update_scan_widget_views_from_model()
            self.main_view.update_from_model()

    def next_scan_button_clicked(self):
        if not self.model.current_scan:
            Qw.QMessageBox.warning(self.main_view,"No scans loaded!","Please load a file first")
        elif not self.model.select_next_scan():
            Qw.QMessageBox.warning(self.main_view,"Warning!","No more scans available!")
        else:
            # self.main_view.update_scan_widget_views_from_model()
            self.main_view.update_from_model()

    def peak_fit_button_clicked(self):
        if not self.model.current_scan:
            Qw.QMessageBox.warning(self.main_view,"No scans loaded!","Please load a file first")
        else:
            self.model.current_scan.fit(num_peaks_desired=self.main_view.scan_form.scan_fit_num_peaks_spinbox.value())
            self.main_view.update_from_model()
            # self.main_view.update_scan_widget_views_from_model()

    def tab_changed(self,new_index):
        print("Changed to " + str(new_index))
        self.main_view.update_center_widget()

    def rh_changed(self):
        if not self.model.setup.run_params:
            Qw.QMessageBox.warning(self.main_view,"No scans loaded!","Please load a file first")
        else:
            self.model.setup.run_params.set_rh(self.main_view.scan_form.rh_dspinbox.value())