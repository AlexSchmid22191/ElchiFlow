class engine:
    """Superclass for all messages emitted by the engine"""

    class answer:
        """Class for all answers to requests from the GUI"""

        class ports:
            """

            """

            def msgDataSpec(ports):
                """
                - ports: dict
                """

        class devices:
            """

            """

            def msgDataSpec(devices):
                """
                - devices: dict
                """

        class valve_state:
            """

            """

            def msgDataSpec(channel, state):
                """
                - channel: int
                - state: bool
                """

        class flow_set:
            """

            """

            def msgDataSpec(channel, flow):
                """
                - channel: int
                - flow: float
                """

        class flow_is:
            """

            """

            def msgDataSpec(channel, flow):
                """
                - channel: int
                - flow: float
                """

        class pressure:
            """

            """

            def msgDataSpec(channel, pressure, runtime):
                """
                - channel: int
                - pressure: float
                - runtime: float
                """

    class status:
        """

        """

        def msgDataSpec(text):
            """
            - text: str
            """

    class error:
        """Superclass for error messages"""

        class connection:
            """

            """

            def msgDataSpec(text):
                """
                - text: str
                """


class gui:
    """Superclass for all messages emitted by the GUI"""

    class con:
        """Everthing relatesd to serial connections"""

        class connect_device:
            """

            """

            def msgDataSpec(device_type, device, port):
                """
                - device_type: str
                - device: str
                - port: str
                """

        class disconnect_device:
            """

            """
            def msgDataSpec(device_type):
                """
                - device_type: str
                """

        class get_ports:
            """

            """

        class get_devices:
            """

            """

    class set:
        """Class for all set command from the GUI (i.e. unidirectional commands without expected repsonse)"""

        class flow:
            """

            """

            def msgDataSpec(channel, flow):
                """
                - channel: int
                - flow: float
                """

        class valve_state:
            """

            """

            def msgDataSpec(channel, state):
                """
                - channel: int
                - state: bool
                """

    class plot:
        """A class for everthing related to plotting/logging"""

        class start:
            """

            """

        class stop:
            """

            """

        class clear:
            """

            """

        class export:
            """

            """

            def msgDataSpec(filepath):
                """
                - filepath: string
                """

    class get:
        """Class for all requests from the gui"""

        class valve_state:
            """

            """

        class flow_is:
            """

            """

        class flow_set:
            """

            """

        class pressure:
            """

            """
