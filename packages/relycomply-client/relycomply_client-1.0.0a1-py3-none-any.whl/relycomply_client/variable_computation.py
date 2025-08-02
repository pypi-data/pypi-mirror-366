from .configuration_sources import ConfigurationLoader


class VariableComputer:
    def __init__(self, configuration: ConfigurationLoader):
        self.configuration = configuration

    def variables(self):
        return self.configuration.items()
