from ..client import OPNClient

class Diagnostics:
    def __init__(self, client: OPNClient):
        self._client = client

        # Cache the different diagnostics modules
        self._activity = None
        self._cpu_usage = None
        self._interface = None
        self._system = None

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def interface(self):
        if self._interface is None:
            from ..controllers import Interface
            self._interface = Interface(self)

        return self._interface

    @property
    def system(self):
        if self._system is None:
            from ..controllers import System
            self._system = System(self)

        return self._system

    @property
    def cpu_usage(self):
        if self._cpu_usage is None:
            from ..controllers import CPU_Usage
            self._cpu_usage = CPU_Usage(self)

        return self._cpu_usage

    @property
    def activity(self):
        if self._activity is None:
            from ..controllers import Activity
            self._activity = Activity(self)

        return self._activity
