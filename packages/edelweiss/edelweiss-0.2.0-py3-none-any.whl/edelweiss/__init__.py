__author__ = "Silvan Fischbacher"
__email__ = "silvanf@phys.ethz.ch"
__credits__ = "ETH Zurich, Institute for Particle Physics and Astrophysics"

__version__ = "0.2.0"


from .compatibility_utils import apply_sklearn_compatibility_patches

apply_sklearn_compatibility_patches()
