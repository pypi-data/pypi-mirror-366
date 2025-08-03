__version__ = "1.0.4"  # Должно совпадать с версией в setup.py
version = "1.0.4"      # Для обратной совместимости

# Явно экспортируем нужные модули
from .xlizard import *
from .combined_metrics import CombinedMetrics
from .sourcemonitor_metrics import SourceMonitorMetrics

__all__ = ['xlizard', 'CombinedMetrics', 'SourceMonitorMetrics']