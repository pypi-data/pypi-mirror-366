"""Base implementation of code generator."""

from pathlib import Path
from typing import TYPE_CHECKING

from pbreflect.log import get_logger
from pbreflect.pbgen.errors import GenerationFailedError, NoProtoFilesError
from pbreflect.pbgen.generators.protocols import GeneratorStrategy
from pbreflect.pbgen.utils.command import CommandExecutorImpl
from pbreflect.pbgen.utils.file_finder import ProtoFileFinderImpl

# Using TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from pbreflect.pbgen.generators.factory import GeneratorFactoryImpl


class BaseGenerator:
    """Base implementation of code generator."""

    def __init__(
        self,
        proto_finder: ProtoFileFinderImpl,
        command_executor: CommandExecutorImpl,
        generator_factory: "GeneratorFactoryImpl",
    ) -> None:
        """Initialize the base generator.

        Args:
            proto_finder: File finder for proto files
            command_executor: Command executor for running protoc
            generator_factory: Factory for creating generator strategies
        """
        self.proto_finder = proto_finder
        self.command_executor = command_executor
        self.generator_factory = generator_factory
        self.logger = get_logger(__name__)

    def generate(self, output_dir: str, generator_strategy: GeneratorStrategy) -> None:
        """Generate code using the specified generator strategy.

        Args:
            output_dir: Directory to output generated code
            generator_strategy: Strategy to use for generation

        Raises:
            NoProtoFilesError: If no proto files are found
            GenerationFailedError: If code generation fails
        """
        self.logger.info("Starting generation python code...")

        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Find proto files
        proto_files = self.proto_finder.find_proto_files()
        if not proto_files:
            raise NoProtoFilesError("No proto files found")

        # Generate code for each proto file
        for proto_file in proto_files:
            self.logger.info(f"Generating code for proto: {proto_file}...")

            # Format command arguments with placeholders
            command_args = []
            for arg_template in generator_strategy.command_template:
                formatted_arg = arg_template.format(
                    include=self.proto_finder.proto_dir,
                    output=output_dir,
                    proto=proto_file,
                )
                command_args.append(formatted_arg)

            # Execute command
            exit_code, stderr = self.command_executor.execute(command_args)
            if exit_code != 0:
                error_message = f"Failed to generate code for {proto_file}: {stderr}"
                self.logger.error(error_message)
                raise GenerationFailedError(error_message)

        self.logger.info("Generation completed!")
