import time
import threading
import src.Drivers.AbstractBaseClasses as base


class TestValveController(base.AbstractValveController):
    def __init__(self, port):
        self.com_lock = threading.Lock()
        self.valve_states = {channel: channel > 2 for channel in range(1, 5)}
        print(f'Test Controller connected at port {port}')

    def switch_valve(self, channel, state):
        with self.com_lock:
            self.valve_states[channel] = state
            print(f'Test Valve Controller: Set channel {channel} to {state}')

    def read_valve_state(self, channel):
        with self.com_lock:
            time.sleep(0.01)
            return self.valve_states[channel]

    def close(self):
        print('Test Controller closed!')


class TestMFC(base.AbstractMassFlowController):
    def __init__(self, port):
        self.com_lock = threading.Lock()
        self.flow_set = {channel: int(time.time() % 100) for channel in range(1, 5)}
        print(f'Test Controller connected at port {port}')

    def set_flow(self, channel, flow):
        self.flow_set[channel] = flow
        print(f'Test Mass Flow Controller: Set channel {channel} to {flow}')

    def read_is_flow(self, channel):
        with self.com_lock:
            time.sleep(0.01)
            return self.flow_set[channel] + (time.time() % 0.01) * 10

    def read_set_flow(self, channel):
        with self.com_lock:
            time.sleep(0.01)
            return self.flow_set[channel]

    def close(self):
        print('Test Controller closed!')


class TestPressureSensor(base.AbstractPressureSensor):
    def __init__(self, port):
        self.com_lock = threading.Lock()
        print(f'Test Controller connected at port {port}')

    def read_pressure(self, channel):
        return time.time() % (10 ** int(time.time() % 3))

    def close(self):
        pass

    @property
    def channels(self):
        return 2
