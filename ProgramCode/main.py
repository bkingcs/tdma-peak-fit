"""
The main entry point of the program
"""
# External Packages
import datetime
import logging
import os
import PySide2.QtCore as Qc
import PySide2.QtGui as Qg
import PySide2.QtWidgets as Qw
import sys
import webbrowser

# Internal Packages
import controller
import custom.central_widget as c_central_widget
import custom.docker_widget as c_dock_widget
import custom.modal_dialogs as c_modal_dialogs
import graphs

##############
# Setup Code #
##############

# Determine if running in pyinstaller bundle or python environment
#   Debugger
#      If frozen, log to both black box and a log file
#      If running in nomal environment, only display in console
#   Test Environment
#      If frozen, do not show any testing features
#      If running in nomal environment, preset folders and allow exporting of data
# if getattr(sys, 'frozen', False):  # we are running in a |PyInstaller| bundle
#     logging_config.configure_logger_frz("Chemicslog-" + datetime.datetime.now().strftime("%Y-%m-%d--%H.%M") + ".log")
#     isTest = False
# else:  # we are running in a normal Python environment
#     logging_config.configure_logger_env()
#     isTest = True
#
# logger = logging.getLogger("main")

########
# Main #
########


class MainView(Qw.QMainWindow):  # REVIEW Code Class
    """
    Initialzes the main window of the program.
    """

    def __init__(self, main_app):
        # Initalize the window
        Qw.QMainWindow.__init__(self)
        # Basic window settings
        self.setWindowTitle('HTDMA')
        self.font = Qg.QFont("Calibri")
        main_app.setFont(self.font)
        # Create the controller that handles all of the functionalities of the program
        self.controller = controller.Controller(self)
        # Create graph objects
        self.first_graph = graphs.FirstGraph()
        self.second_graph = graphs.SecondGraph()
        self.third_graph = graphs.ThirdGraph()
        self.fourth_graph = graphs.FourthGraph()


        # Commenting out to use later
        #self.kappa_graph = graphs.KappaGraph()

        # create left dock widget for information related stuff
        [self.scaninfo_docker, self.sigmoid_docker, self.kappa_docker] = self.create_left_docker()
        self.scaninfo_docker_widget = self.scaninfo_docker.widget()
        self.sigmoid_docker_widget = self.sigmoid_docker.widget()
        self.kappa_docker_widget = self.kappa_docker.widget()
        # set options for left doc
        dock_options = Qw.QMainWindow.VerticalTabs | Qw.QMainWindow.AnimatedDocks | Qw.QMainWindow.ForceTabbedDocks
        self.setDockOptions(dock_options)
        # create central widget
        [self.stacked_central_widget, self.central_widget_alignscan,
         self.central_widget_kappa] = self.create_central_widget()
        # create menu bar
        # self.file_menu, self.action_menu, self.window_menu = self.create_menus()
        self.file_menu = self.action_menu = self.window_menu = Qw.QMenu("&Temp")
        self.set_menu_bar_by_stage()
        # create progress bar
        self.progress_dialog = self.create_progress_bar()
        self.close_progress_bar()
        # showMaximized must be at end of init
        self.showMaximized()
        self.reset_view()
        # if isTest:  # TEST
        #     self.open_files()

    ########
    # Menu #
    ########

    def create_menus(self):
        """
        Creates the menu bar for the main view

        :returns:
            - **file_menu** - Qw.QMenu object that allows the user to open and save files and projects.
            - **action_menu** - Qw.QMenu object that allows the user to preform actions on the data
            - **window_menu** -  Qw.QMenu object that allows the user to turn windows on and off
            - **help_menu** - Qw.QMenu object that allows the user to access settings and help information
        """
        # Add file menu
        file_menu = Qw.QMenu("&File")
        new_action = Qw.QAction('&New Project from Files...', self, shortcut="Ctrl+N", triggered=self.open_files)
        open_action = Qw.QAction('&Open Existing Project...', self, triggered=self.open_project)
        save_action = Qw.QAction('&Save Project', self, shortcut="Ctrl+S", triggered=self.save_project)
        save_as_action = Qw.QAction('Save Project &As', self, triggered=self.save_project_as)
        #export_data_action = Qw.QAction('Export &Kappa Data', self, triggered=self.export_project_data)
        exit_action = Qw.QAction('&Exit', self, shortcut="Ctrl+E", triggered=self.closeEvent )
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        file_menu.addActions([open_action, save_action, save_as_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        self.menuBar().addMenu(file_menu)

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
        return file_menu, action_menu, window_menu

    def set_menu_bar_by_stage(self):
        """
        Enables and Disables file menu items based on the stage that the :class:`~controller.Controller` is in.
        """
        # clear old menu
        self.menuBar().clear()
        # recreate menu
        self.file_menu, self.action_menu, self.window_menu = self.create_menus()
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

    ##############
    # MENU ITEMS #
    ##############

    # File menu items

    def open_files(self):
        # """
        # Opens data files and begins the scan alignment process
        # """
        # if isTest:  # TEST
        #     open_dir = "../../ChemicsTestData/Penn State 19 - Full Data Set/"
        # else:
        #     open_dir = ""
        # # noinspection PyCallByClass
        # files = Qw.QFileDialog.getOpenFileNames(self, "Open files", open_dir, "Data files (*.csv *.txt)")[0]
        # if files:
        #     # read in new files
        #     self.controller.start(files)
        #     self.setWindowTitle("Chemics: " + self.controller.get_project_name())
        pass

    def open_project(self):
        # """
        # Opens a previously saved project and load the information that was stored at the time.
        #
        # See :class:`~controller.Controller.save_project` in the Controller class.
        # """
        # if isTest:  # TEST
        #     open_dir = "../../TestData/Saved Chemics Files"
        # else:
        #     open_dir = ""
        # # noinspection PyCallByClass
        # run_file = Qw.QFileDialog.getOpenFileName(self, "Open file", open_dir, "Project files (*.chemics)")[0]
        # if run_file:
        #     # read in new files
        #     self.controller.load_project(run_file)
        #     self.setWindowTitle("Chemics: " + self.controller.get_project_name())
        pass

    def save_project(self):
        # """
        # Saves the current open project to the disk
        # """
        # self.controller.save_project()
        pass

    def save_project_as(self):
        # """
        # Allows the user to select a save name and saves the current open project to the disk
        # """
        # # Get file name
        # file_name = self.controller.project_folder + "/"
        # file_name += self.controller.get_project_name() + ".chemics"
        # # noinspection PyCallByClass
        # project_file = Qw.QFileDialog.getSaveFileName(self, "Save file", file_name, "Project files (*.chemics)")[0]
        # if project_file:
        #     # append file extention if neccessary
        #     if not project_file.endswith(".chemics"):
        #         project_file += ".chemics"
        #     # Save files
        #     self.controller.set_save_name(project_file)
        #     self.controller.save_project()
        pass

    def closeEvent(self, event: Qg.QCloseEvent):
        """
        Creating the event when force quitting wasn't used the window
        """
        # Setting up the reply question when clicking on the exit button
        reply = Qw.QMessageBox.question(self, 'Message', 'Are you sure you want to quit?',
                                        Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)

        # Receives the response makes a decision
        if reply == Qw.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def set_font(self, font, size):
        """
        Sets the font and font size desired.

        :param PySide.QtGui.QFont font: The new font style.
        :param int size: The new font size
        """
        # noinspection PyUnresolvedReferences
        self.font = Qg.QFont(font.family(), size)
        app.setFont(self.font)


if __name__ == "__main__":
    # setup debugger
    # logger.info("=================================================")
    # logger.info("=================================================")
    # logger.debug("HTDMA started")
    print("=================================================")
    print("=================================================")
    print("HTDMA started")

    app = Qw.QApplication(sys.argv)
    main_window = MainView(app)
    main_window.show()

    sys.exit(app.exec_())
