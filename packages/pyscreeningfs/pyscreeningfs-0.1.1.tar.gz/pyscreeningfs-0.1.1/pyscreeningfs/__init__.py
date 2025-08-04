
from . import fsonline

from .online_screening import online_screening


__version__ = "0.1.1" 

# Optional: You can make specific functions/classes available directly
# by importing them here. Users can then call `fsonline.online_screenign(...)`
# instead of `fsonline.online_screening.online_screenign(...)`.
__all__ = ["online_screening"] # Or list all public functions you want to expose
