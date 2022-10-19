"""
Model
"""
from htdma_code.model.setupmods.setup import Setup
from htdma_code.model.dma1 import DMA_1
from htdma_code.model.scan import Scan
from htdma_code.model.scans import Scans
from htdma_code.model.results_table import ResultsTableModel

class Model:
    """
    This is the main class that encapsulates pretty much everything for a complete run

    Attributes:
        setup - an instance of the Setup class
        scans - an instance of Scans, which represents all of the scans of a given run
        dma1 - an instance of DMA_1, which represents the configuation of DMA_1
    """
    def __init__(self):
        self.setup = Setup()
        self.scans = Scans()
        self.dma1 = None

        self.current_scan: Scan = None
        self.current_scan_index: int = None
        self.total_results_table = None

    def process_new_file(self, filename):
        """
        This handles the initialization of everything needed to start analyzing a new file of scans.
        """
        self.setup.read_file(filename)
        self.scans.read_file(filename)

        # Now, initialize various setup structures
        self.dma1 = DMA_1(self.setup)
        self.current_scan_index = 0
        self._update_selected_scan_in_model()
        self.total_results_table = ResultsTableModel()

    def select_scan(self, scan_index: int) -> bool:
        """
        Select a specified scan number

        :return: True if the scan could be selected, False if it was out of range
        """
        if scan_index >= 0 and scan_index < self.scans.get_num_scans():
            self.current_scan_index = scan_index
            self._update_selected_scan_in_model()
            return True
        else:
            return False

    def select_next_scan(self) -> bool:
        """
        Select the next scan from the collection of scans contained in the model.

        :return: True if the next scan was selected successfully, False if there were no
        more scans that could be selected
        """
        if self.current_scan_index + 1 == self.scans.get_num_scans():
            return False
        else:
            self.current_scan_index += 1
            self._update_selected_scan_in_model()
            return True

    def select_prev_scan(self) -> bool:
        """
        Select the previous scan from the collection of scans contained in the model.

        :return True if the previous scan was selected successfully, False if the current
        scan is already the first one
        """
        if self.current_scan_index == 0:
            return False
        else:
            self.current_scan_index -= 1
            self._update_selected_scan_in_model()
            return True

    def _update_selected_scan_in_model(self):
        """
        Retrieve a scan from all of the scans based on the internal value of
        self.current_scan_index. This is not to be called outside of this class.
        """
        self.current_scan = self.scans.get_scan(scan_index=self.current_scan_index)
        self.setup.update_scan_params(self.current_scan_index)


