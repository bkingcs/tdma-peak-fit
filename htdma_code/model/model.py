"""
Model
"""

import htdma_code.model.setup
import htdma_code.model.run
import htdma_code.model.dma1
import htdma_code.model.scan

class Model:
    """
    This is the main class that encapsulates pretty much everything for a complete run

    Attributes:
        setup - an instance of the Setup class
        run_of_scans - an instance of Run, which represents all of the scans of a given run
        dma1 - an instance of DMA_1, which represents the configuation of DMA_1
    """
    def __init__(self):
        self.setup = htdma_code.model.setup.Setup()
        self.run_of_scans = htdma_code.model.run.Run()
        self.dma1 = htdma_code.model.dma1.DMA_1(debug=False)
        self.current_scan: htdma_code.model.scan.Scan = None
        self.current_scan_num: int = None

    def process_new_file(self, filename):
        self.setup.read_file(filename)
        self.run_of_scans.read_file(filename)
        self.dma1.update_from_setup_and_run(self.setup, self.run_of_scans)
        self.current_scan_num = 0
        self._update_selected_scan_in_model()

    def select_scan_num(self, scan_num: int) -> bool:
        """
        Select a specified scan number

        :return: True if the scan could be selected, False if it was out of range
        """
        if scan_num >= 0 and scan_num < self.run_of_scans.get_num_scans():
            self.current_scan_num = scan_num
            self._update_selected_scan_in_model()
            return True
        else:
            return False

    def select_next_scan_num(self) -> bool:
        """
        Select the next scan from the collection of scans contained in the model.

        :return: True if the next scan was selected successfully, False if there were no
        more scans that could be selected
        """
        if self.current_scan_num + 1 == self.run_of_scans.get_num_scans():
            return False
        else:
            self.current_scan_num += 1
            self._update_selected_scan_in_model()
            return True

    def select_prev_sample_num(self) -> bool:
        """
        Select the previous scan from the collection of scans contained in the model.

        :return True if the previous scan was selected successfully, False if the current
        scan is already the first one
        """
        if self.current_scan_num == 0:
            return False
        else:
            self.current_scan_num -= 1
            self._update_selected_scan_in_model()
            return True

    def _update_selected_scan_in_model(self):
        """
        Retrieve a scan from all of the scans based on the internal value of
        self.current_scan_num. This is not to be called outside of this class.
        """
        self.current_scan = self.run_of_scans.get_scan(self.current_scan_num)


