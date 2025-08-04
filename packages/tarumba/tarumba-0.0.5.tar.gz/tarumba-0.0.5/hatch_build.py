from babel.messages.frontend import compile_catalog
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, _version, _build_data):
        cmd = compile_catalog()
        cmd.domain = "tarumba"
        cmd.directory = "src/tarumba/locale"
        cmd.finalize_options()
        cmd.run()
