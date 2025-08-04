"""PbReflect generator strategy."""

from typing import Optional

from pbreflect.pbgen.generators.protocols import GeneratorStrategy


class PbReflectGeneratorStrategy(GeneratorStrategy):
    """PbReflect generator strategy."""

    def __init__(self, async_mode: bool = True, template_dir: Optional[str] = None) -> None:
        """Initialize the PbReflect generator strategy.

        Args:
            async_mode: Whether to generate async client code (True) or sync client code (False)
            template_dir: Optional path to custom templates directory
        """
        self.async_mode = async_mode
        self.template_dir = template_dir

    @property
    def command_template(self) -> list[str]:
        """Get the command template for code generation.

        Returns:
            Command template as a list of arguments
        """
        plugin_options = []

        if not self.async_mode:
            plugin_options.append("async=false")
            
        if self.template_dir:
            plugin_options.append(f"t={self.template_dir}")

        plugin_params = ",".join(plugin_options)
        plugin_out = f"--pbreflect_out={plugin_params}:" + "{output}" if plugin_params else "--pbreflect_out={output}"

        return [
            "python",
            "-m",
            "grpc_tools.protoc",
            "--proto_path={include}",
            "--python_out={output}",
            "--mypy_out=readable_stubs,quiet:{output}",
            plugin_out,
            "{proto}",
        ]
