"""
The main entry point of the program
"""
# External Packages

# GUI packages

import PySide2.QtGui as Qg
import PySide2.QtWidgets as Qw

# Internal Packages
from PySide2.QtGui import QKeySequence

from OLD.view.widgets import central_widget as c_central_widget
from code.model import model as model
import OLD.view.graphs

########
# Main #
########


class MainView(Qw.QMainWindow):  # REVIEW Code Class
    """
    Initialzes the main window of the program.
    """

    def __init__(self, main_app, model: model.Model):
        # Initalize the window
        Qw.QMainWindow.__init__(self)

        # Basic window settings
        self.setWindowTitle('HTDMA')
        self.font = Qg.QFont("Calibri")
        self.main_app = main_app
        self.main_app.setFont(self.font)

        self.model = model

        # Create the controller that handles all of the functionalities of the program
        # self.controller = controller.Controller(self,model)

        # Create graph objects
        self.dma1_graph = OLD.view.graphs.FirstDMA(dma1=model.dma1)
        self.second_graph = OLD.view.graphs.SecondGraph()
        self.third_graph = OLD.view.graphs.ThirdGraph()
        self.fourth_graph = OLD.view.graphs.FourthGraph()


        # Commenting out to use later
        #self.kappa_graph = graphs.KappaGraph()

        # create left dock widget for information related stuff
        self.scaninfo_docker = self.create_left_docker()
        # self.sigmoid_docker_widget = self.sigmoid_docker.widget()
        self.scaninfo_docker_widget = self.scaninfo_docker.widget()
        # self.kappa_docker_widget = self.kappa_docker.widget()
        # # set options for left doc
        dock_options = Qw.QMainWindow.VerticalTabs | Qw.QMainWindow.AnimatedDocks | Qw.QMainWindow.ForceTabbedDocks
        self.setDockOptions(dock_options)
        # # create central widget
        [self.stacked_central_widget, self.central_widget_alignscan] = self.create_central_widget()
        # create menu bar
        self.create_menus()
        self.set_menu_bar_by_stage()

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.

        # create progress bar
        # self.progress_dialog = self.create_progress_bar()
        # self.close_progress_bar()
        # showMaximized must be at end of init
        self.showMaximized()
        # self.reset_view()
        # if isTest:  # TEST
        #     self.open_files()

    ########
    # Menu #
    ########

    def create_menus(self):
        """
        Creates the menu bar for the main view
            - **file_menu** - Qw.QMenu object that allows the user to open and save files and projects.
            - **action_menu** - Qw.QMenu object that allows the user to preform actions on the data
            - **window_menu** -  Qw.QMenu object that allows the user to turn windows on and off
            - **help_menu** - Qw.QMenu object that allows the user to access settings and help information
        """
        # Create a file menu
        self.file_menu = Qw.QMenu("&File")

        # Add items to File menu
        self.new_action = Qw.QAction('&New Project from Files...', self)
        self.new_action.setShortcut(QKeySequence.New)

        # Add the individual actions to the file menu
        self.file_menu.addAction(self.new_action)

        # Add the file menu to the meny bar
        self.menuBar().addMenu(self.file_menu)

        # self.open_action = Qw.QAction('&Open Existing Project...', self, triggered=self.open_project)
        # self.save_action = Qw.QAction('&Save Project', self, shortcut="Ctrl+S", triggered=self.save_project)
        # self.save_as_action = Qw.QAction('Save Project &As', self, triggered=self.save_project_as)
        #export_data_action = Qw.QAction('Export &Kappa Data', self, triggered=self.export_project_data)
        # self.exit_action = Qw.QAction('&Exit', self, shortcut="Ctrl+E", triggered=self.closeEvent )
        # file_menu.addSeparator()
        # file_menu.addActions([open_action, save_action, save_as_action])
        # file_menu.addSeparator()
        # file_menu.addAction(exit_action)


        # Add action menu
        action_menu = Qw.QMenu("&Actions")
        # preview_all_action = Qw.QAction('&Preview all scans', self, triggered=self.preview_all_scans)
        # auto_align_action = Qw.QAction('Auto &Shift', self, triggered=self.show_auto_align_dialog)
        # correct_charges = Qw.QAction('Correct Charges &All Scans', self, triggered=self.correct_charges)
        # correct_charges_one = Qw.QAction('Correct Charges &One Scan', self, triggered=self.correct_charges_one)
        # auto_fit_action = Qw.QAction('Auto &Fit Sigmoid All Scans', self, triggered=self.show_auto_fit_sigmoid_dialog)
        # auto_fit_one_action = Qw.QAction('Auto F&it Sigmoid One Scan', self, triggered=self.auto_fit_sigmoid_one)
        # cal_kappa_action = Qw.QAction('&Calculate Kappa', self, triggered=self.show_kappa_params_dialog)
        # action_menu.addAction(preview_all_action)
        # action_menu.addSeparator()
        # action_menu.addActions([auto_align_action, correct_charges, correct_charges_one,
        #                         auto_fit_action, auto_fit_one_action])
        # action_menu.addSeparator()
        # action_menu.addAction(cal_kappa_action)
        self.menuBar().addMenu(action_menu)

        # Add window menu
        window_menu = Qw.QMenu("&Windows")
        # window_menu.addAction(self.scaninfo_docker.toggleViewAction())
        # window_menu.addAction(self.sigmoid_docker.toggleViewAction())
        # window_menu.addAction(self.kappa_docker.toggleViewAction())
        # show_window_action = Qw.QAction("&Show Alignment Graphs", self, triggered=self.switch_central_widget)
        # show_window_action.setCheckable(True)
        # window_menu.addAction(show_window_action)
        self.menuBar().addMenu(window_menu)

        # Add Help menu
        help_menu = Qw.QMenu("&Help")
        # setting_action = Qw.QAction('&Settings', self, triggered=self.show_setting_dialog)
        # TODO issues/23 User Manual help menu item
        # user_manual_action = Qw.QAction('&User Manual', self, triggered=self.open_user_manual)
        # about_action = Qw.QAction('&About', self, triggered=self.open_about)
        # TODO issues/23 Feedback help menu item
        # help_menu.addActions([setting_action, user_manual_action])
        # help_menu.addSeparator()
        # help_menu.addAction(about_action)
        self.menuBar().addMenu(help_menu)

        # Add Test menu
        test_menu = Qw.QMenu("&Test")
        # if isTest:  # TEST
        #     export_scans = Qw.QAction('Export Scans', self, triggered=self.export_scans)
        #     test_menu.addAction(export_scans)
        self.menuBar().addMenu(test_menu)       # indent back into if statement when uncommented
        return

    def set_menu_bar_by_stage(self):
        """
        Enables and Disables file menu items based on the stage that the :class:`~controller.Controller` is in.
        """
        # clear old menu
        self.menuBar().clear()
        # recreate menu
        self.create_menus()
        # disable by stage
        # if self.controller.stage == "init":
        #     # file menu
        #     file_action_list = self.file_menu.actions()  # TODO - Find better way to reference
        #     file_action_list[3].setDisabled(True)  # Disable Save Project
        #     file_action_list[4].setDisabled(True)  # Disable Save Project As
        #     file_action_list[5].setDisabled(True)  # Disable Export Kappa Data
        #     # action menu
        #     self.action_menu.setDisabled(True)
        #     # window menu
        #     self.window_menu.setDisabled(True)
        # elif self.controller.stage == "align":
        #     # file menu - none disabled
        #     # action menu
        #     action_list = self.action_menu.actions()  # TODO - Find better way to reference
        #     action_list[4].setDisabled(True)  # Disable Correct charges one scan
        #     action_list[5].setDisabled(True)  # Disable Autofit sigmoid
        #     action_list[8].setDisabled(True)  # Disable calculate Kappa
        #     # window menu - none disable
        # elif self.controller.stage == "sigmoid":
        #     # file menu - none disabled
        #     # action menu - none disabled
        #     # window menu - none disable
        #     pass
        # elif self.controller.stage == "kappa":
        #     # file menu - none disabled
        #     # action menu - none disabled
        #     # window menu - none disable
        #     pass
        # TODO Delete this once smoothing algo has been expanded


    def set_font(self, font, size):
        """
        Sets the font and font size desired.

        :param PySide.QtGui.QFont font: The new font style.
        :param int size: The new font size
        """
        # noinspection PyUnresolvedReferences
        self.font = Qg.QFont(font.family(), size)
        self.main_app.setFont(self.font)

    ##############################
    # Create Widgets and Dockers #
    ##############################

    def create_left_docker(self):
        """
        Creates the left docker screen and adds menu options to the Window menu bar section

        :returns:

            - **scaninfo_docker** - Qw.QDockWidget object that represents the Scan Information screen
            - **scan_docker_widget** - c_dock_widget.DockerScanInformation object that contains the lay out for the
              Scan Information screen
            - **sigmoid_docker** - Qw.QDockWidget object that represents the Sigmoid Parameters screen
            - **sigmoid_docker_widget** - c_dock_widget.DockerSigmoidWidget object that contains the lay out for the
              Sigmoid Parameters screen
            - **kappa_docker** - Qw.QDockWidget object that represents the Kappa Values screen
            - **kappa_docker_widget** - c_dock_widget.DockerKappaWidget object that contains the lay out for the Kappa
              Values screen
        """
        # create left docker
        scaninfo_docker = Qw.QDockWidget("Scan &Information", self)
        # scan_docker_widget = c_dock_widget.DockerScanInformation(self.controller)
        # scaninfo_docker.setWidget(scan_docker_widget)
        # scaninfo_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        # scaninfo_docker.setFeatures(Qw.QDockWidget.DockWidgetMovable | Qw.QDockWidget.DockWidgetClosable)
        # self.addDockWidget(Qc.Qt.LeftDockWidgetArea, scaninfo_docker)

        # create sigmoid docker
        # sigmoid_docker = Qw.QDockWidget("Sigmoid &Parameters", self)
        # sigmoid_docker_widget = c_dock_widget.DockerSigmoidWidget(self.controller)
        # sigmoid_docker.setWidget(sigmoid_docker_widget)
        # sigmoid_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        # sigmoid_docker.setFeatures(Qw.QDockWidget.DockWidgetMovable | Qw.QDockWidget.DockWidgetClosable)
        # self.addDockWidget(Qc.Qt.LeftDockWidgetArea, sigmoid_docker)
        #self.tabifyDockWidget(scaninfo_docker)
        # create kappa docker
        # kappa_docker = Qw.QDockWidget("&Kappa Values", self)
        # kappa_docker_widget = c_dock_widget.DockerKappaWidget(self.controller, self.kappa_graph)
        # kappa_docker.setWidget(kappa_docker_widget)
        # kappa_docker.setAllowedAreas(Qc.Qt.RightDockWidgetArea | Qc.Qt.LeftDockWidgetArea)
        # kappa_docker.setFeatures(Qw.QDockWidget.DockWidgetMovable | Qw.QDockWidget.DockWidgetClosable)
        # self.addDockWidget(Qc.Qt.LeftDockWidgetArea, kappa_docker)
        return scaninfo_docker

    def create_central_widget(self):
        """
        Creates the central widget that appear in the main area.
        The central widget includes the widgets for the align scans and kappa sections.

        :returns:

            - **stacked_central_widget** - Qw.QStackedWidget object that represents where the center widgets appear
            - **central_widget_alignscan** - c_central_widget.CentralWidgetScans object that represents
              the four graphs that are displayed during the alignment phase
            - **central_widget_kappa** - c_central_widget.CentralWidgetKappa object that represents the kappa graph.

        """
        # create alignment central widget
        central_widget_alignscan = c_central_widget.CentralWidgetScans(self)
        # central_widget_kappa = c_central_widget.CentralWidgetKappa(self)
        stacked_central_widget = Qw.QStackedWidget()
        stacked_central_widget.addWidget(central_widget_alignscan)
        #stacked_central_widget.addWidget(central_widget_kappa)
        # lock out the menus that we will not use
        self.setCentralWidget(stacked_central_widget)
        return central_widget_alignscan, stacked_central_widget

    def switch_central_widget(self):  # RESEARCH How code works after controller.start is added
        """
        Toggles graph display in middle of screen between Alighment Graphs and Kappa Graphs
        """
        # TODO issues/36  This is a strange way of switching
        new_index = self.stacked_central_widget.count() - self.stacked_central_widget.currentIndex() - 1
        self.stacked_central_widget.setCurrentIndex(new_index)

    def closeEvent(self, event):
        """
        This method is overriding the default method as defined in QMainWindow class
        """
        # Setting up the reply question when clicking on the exit button
        reply = Qw.QMessageBox.question(self, 'Message', 'Are you sure you want to quit?',
                                        Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)

        # Receives the response makes a decision
        if reply == Qw.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
