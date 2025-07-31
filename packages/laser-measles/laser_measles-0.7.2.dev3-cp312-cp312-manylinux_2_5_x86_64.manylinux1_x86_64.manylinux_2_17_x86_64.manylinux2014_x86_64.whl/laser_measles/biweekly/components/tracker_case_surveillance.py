from laser_measles.components import BaseCaseSurveillanceParams
from laser_measles.components import BaseCaseSurveillanceTracker


class CaseSurveillanceParams(BaseCaseSurveillanceParams): ...


class CaseSurveillanceTracker(BaseCaseSurveillanceTracker):
    """Tracks detected cases in the model."""
