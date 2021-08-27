import abc


class AbstractValveController(abc.ABC):
    @abc.abstractmethod
    def switch_valve(self, channel, state):
        pass

    @abc.abstractmethod
    def read_valve_state(self, channel):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class AbstractMassFlowController(abc.ABC):
    @abc.abstractmethod
    def set_flow(self, channel, flow):
        pass

    @abc.abstractmethod
    def read_is_flow(self, channel):
        pass

    @abc.abstractmethod
    def read_set_flow(self, channel):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class AbstractPressureSensor(abc.ABC):
    @abc.abstractmethod
    def read_pressure(self, channel):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @property
    @abc.abstractmethod
    def channels(self):
        pass
