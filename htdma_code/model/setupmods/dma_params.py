from enum import Enum, auto

TSI_3080 = {
    "length_cm" : 44.44,
    "radius_in_cm" : 0.937,
    "radius_out_cm" : 1.958
}

class DMA_config_enum(Enum):
    DMA_TSI_3080 = auto()

class DMAParams:
    """
    DMAParams

    DMA encapsulates all hardware settings for a DMA.

    Attributes:
        * length_cm - the length of the charge rod (cm)
        * radius_in_cm - the inner radius of the charge rod (cm)
        * radius_out_cm - the outer radius of the DMA housing (cm)
    """

    def __init__(self,length_cm=0,radius_in_cm=0,radius_out_cm=0) -> None:
        """
        Initialize a new DMA object. The defaults are based on a TSI 3080.
        """

        self.length_cm = length_cm
        self.radius_in_cm = radius_in_cm
        self.radius_out_cm = radius_out_cm
        if length_cm == 0 or radius_in_cm == 0 or radius_out_cm == 0:
            self._is_initialized_ = False
        else:
            self._is_initialized_ = True

    def __repr__(self) -> str:
        s = "DMA:\n"
        if self._is_initialized_ > 0:
            s += "  r_in_cm: {:.3f}\n".format(self.radius_in_cm)
            s += "  r_out_cm: {:.3f}\n".format(self.radius_out_cm)
            s += "  length_cm: {:.3f}\n".format(self.length_cm)
        else:
            s += "  NOT INITIALIZED\n"
        return s

    def set_params(self,length_cm,radius_in_cm,radius_out_cm) -> None:
        """
        Set up the parameters for the DMA

        Params:
        * length_cm - Length of the charged rod in the DMA
        * radius_in_cm - radius of the rod
        * radius_out_cm - outer radius of the DMA housing
        """
        self.length_cm = length_cm
        self.radius_in_cm = radius_in_cm
        self.radius_out_cm = radius_out_cm
        self._is_initialized_ = True

    def set_params_from_dma_config(self, dma_config : DMA_config_enum) -> None:
        """
        Set up the parameters for the dma based on a specified known
        DMA configuration hard-coded in this program
        """
        if dma_config is DMA_config_enum.DMA_TSI_3080:
            self.length_cm = TSI_3080["length_cm"]
            self.radius_in_cm = TSI_3080["radius_in_cm"]
            self.radius_out_cm = TSI_3080["radius_out_cm"]
            self._is_initialized_ = True
        else:
            raise ValueError("Unknown dma_config")
