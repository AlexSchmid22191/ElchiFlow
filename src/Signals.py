from PySide6.QtCore import QObject, Signal

from src.Engine.ThreadDecorators import Signals


class GuiSignals(QObject):
    connect_device = Signal(str, str, str)
    disconnect_device = Signal(str)
    get_ports = Signal()
    get_devices = Signal()
    set_flow = Signal(int, float)
    set_valve_state = Signal(int, bool)
    start_plot = Signal()
    stop_plot = Signal()
    clear_plot = Signal()
    export_plot = Signal(str)
    get_valve_state = Signal()
    get_flow_is = Signal()
    get_flow_set = Signal()
    get_pressure = Signal()


class EngineSignals(QObject):
    answer_ports = Signal(dict)
    answer_devices = Signal(dict)
    valve_state = Signal(int, bool)
    flow_set = Signal(int, float)
    flow_is = Signal(int, float)
    pressure = Signal(int, float, float)


signals_engine = EngineSignals()
signals_gui = GuiSignals()
