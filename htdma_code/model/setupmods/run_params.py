
class RunParams:
    """
    RunParams - a simple class used to encapsulate all of the parameters for a given run

    Attributes:
        * mu_gas_viscosity_Pa_sec
        * gas_density
        * mean_free_path_m
        * temp_k
        * pres_kPa

    """
    def __init__(self,
                 mu_gas_viscosity_Pa_sec=0.0,
                 gas_density=0.0,
                 mean_free_path_m=0.0,
                 temp_k=20+273.15,
                 pres_kPa=101.3):
        self.mu_gas_viscosity_Pa_sec = mu_gas_viscosity_Pa_sec
        self.gas_density = gas_density
        self.mean_free_path_m = mean_free_path_m
        self.temp_k = temp_k
        self.pres_kPa = pres_kPa
        if mu_gas_viscosity_Pa_sec == 0.0 or gas_density == 0.0 or mean_free_path_m == 0.0:
            self._is_initialized_ = False
        else:
            self._is_initialized_ = True

    def set_params(self,mu_gas_viscosity_Pa_sec,gas_density,mean_free_path_m,temp_k,pres_kPa):
        """
        A basic setter method to set the parameters that were used for the run
        """
        self.mu_gas_viscosity_Pa_sec = mu_gas_viscosity_Pa_sec
        self.gas_density = gas_density
        self.mean_free_path_m = mean_free_path_m
        self.temp_k = temp_k
        self.pres_kPa = pres_kPa
        self._is_initialized_ = True

    def __repr__(self):
        s = "RunParams:\n"
        if not self._is_initialized_:
            s += "  NOT INITIALIZED\n"
        else:
            s += "  gas viscosity: {}\n".format(self.mu_gas_viscosity_Pa_sec)
            s += "  gas density: {}\n".format(self.gas_density)
            s += "  mean free path: {}\n".format(self.mean_free_path_m)
            s += "  temp (K): {}\n".format(self.temp_k)
            s += "  pres (kPa): {}\n".format(self.pres_kPa)
        return s
