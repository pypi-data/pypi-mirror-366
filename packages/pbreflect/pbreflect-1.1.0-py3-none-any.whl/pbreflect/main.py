import pathlib
import tempfile
from typing import Literal, cast

import click

from pbreflect.pbgen.runner import run
from pbreflect.protorecover.recover_service import RecoverService


@click.group()
def cli() -> None:
    pass


@click.command("get-protos")
@click.option("-h", "--host", type=str, required=True, help="Destination host")
@click.option("-o", "--output", type=str, default="protos", help="Output directory")
@click.option("--use-tls", is_flag=True, help="Use TLS/SSL for connection")
@click.option(
    "--root-cert",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to root certificate file (CA certificate)",
)
@click.option(
    "--private-key",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to private key file",
)
@click.option(
    "--cert-chain",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to certificate chain file",
)
def get_protos(
    host: str,
    output: str,
    use_tls: bool,
    root_cert: pathlib.Path | None,
    private_key: pathlib.Path | None,
    cert_chain: pathlib.Path | None,
) -> None:
    """Recover proto files from a gRPC server using reflection.

    This command connects to a gRPC server, retrieves proto descriptors using the reflection API,
    and generates .proto files that can be used for client development.
    """
    output_dir = pathlib.Path(output)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate TLS parameters
    if root_cert or private_key or cert_chain:
        use_tls = True
        click.echo("TLS certificates provided, enabling TLS mode")

    if use_tls:
        click.echo("Using secure connection (TLS)")

    with RecoverService(
        host,
        output_dir,
        use_tls=use_tls,
        root_certificates_path=root_cert,
        private_key_path=private_key,
        certificate_chain_path=cert_chain,
    ) as service:
        try:
            saved_files = service.recover_proto_files()
            if saved_files:
                click.echo(f"Successfully recovered {len(saved_files)} proto files to {output_dir}")
                for file_path in saved_files:
                    click.echo(f"  - {file_path.name}: {file_path}")
            else:
                click.echo("No proto files were recovered")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort() from e


@click.command("generate")
@click.option(
    "-p",
    "--proto-dir",
    "proto_dir",
    required=True,
    help="Directory with proto files",
)
@click.option(
    "-o",
    "--output-dir",
    "output_dir",
    required=True,
    help="Directory where to generate code",
)
@click.option(
    "-t",
    "--gen-type",
    "gen_type",
    required=False,
    default="pbreflect",
    type=click.Choice(["default", "mypy", "betterproto", "pbreflect"]),
    help="Type of generator",
)
@click.option("-r", "--refresh", "refresh", required=False, is_flag=True, help="Clear output directory")
@click.option(
    "--async-mode",
    "async_mode",
    type=click.Choice(["true", "false"]),
    default="false",
    help="Generate async (true) or sync (false) client code (only for pbreflect generator)",
)
@click.option(
    "--template-dir",
    "template_dir",
    required=False,
    help="Custom directory with templates (only for pbreflect generator)",
)
def gen(
    proto_dir: str,
    output_dir: str,
    gen_type: str = "pbreflect",
    refresh: bool = False,
    async_mode: str = "false",
    template_dir: str | None = None,
) -> None:
    """Command to generate code.

    Args:
        proto_dir: Directory with proto files
        output_dir: Directory where to generate code
        gen_type: Type of generator
        refresh: Clear output directory
        async_mode: Generate async (true) or sync (false) client code (only for pbreflect generator)
        template_dir: Custom directory with templates (only for pbreflect generator)
    """
    gen_type_literal = cast(Literal["default", "mypy", "betterproto", "pbreflect"], gen_type)
    run(
        proto_dir,
        output_dir,
        gen_type_literal,
        refresh,
        async_mode=async_mode.lower() == "true",
        template_dir=template_dir,
    )


@click.command("reflect")
@click.option("-h", "--host", type=str, required=True, help="Destination host")
@click.option("-o", "--output", type=str, default="clients", help="Output directory")
@click.option("--use-tls", is_flag=True, help="Use TLS/SSL for connection")
@click.option(
    "--root-cert",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to root certificate file (CA certificate)",
)
@click.option(
    "--private-key",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to private key file",
)
@click.option(
    "--cert-chain",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to certificate chain file",
)
@click.option(
    "-t",
    "--gen-type",
    "gen_type",
    required=False,
    default="pbreflect",
    type=click.Choice(["default", "mypy", "betterproto", "pbreflect"]),
    help="Type of generator",
)
@click.option(
    "--async-mode",
    "async_mode",
    type=click.Choice(["true", "false"]),
    default="false",
    help="Generate async (true) or sync (false) client code (only for pbreflect generator)",
)
@click.option(
    "--template-dir",
    "template_dir",
    required=False,
    help="Custom directory with templates (only for pbreflect generator)",
)
@click.option("-r", "--refresh", "refresh", required=False, is_flag=True, help="Clear output directory")
def generate_from_server(
    host: str,
    output: str,
    use_tls: bool,
    root_cert: pathlib.Path | None,
    private_key: pathlib.Path | None,
    cert_chain: pathlib.Path | None,
    gen_type: str = "pbreflect",
    async_mode: str = "false",
    template_dir: str | None = None,
    refresh: bool = False,
) -> None:
    """Generate client code directly from a gRPC server.

    This command connects to a gRPC server, retrieves proto descriptors using the reflection API,
    generates temporary .proto files, and then uses them to generate client code.
    The temporary proto files are automatically deleted after code generation.
    """
    output_dir = pathlib.Path(output)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate TLS parameters
    if root_cert or private_key or cert_chain:
        use_tls = True
        click.echo("TLS certificates provided, enabling TLS mode")

    if use_tls:
        click.echo("Using secure connection (TLS)")

    # Create a temporary directory for proto files
    with tempfile.TemporaryDirectory() as temp_proto_dir:
        temp_proto_path = pathlib.Path(temp_proto_dir)
        click.echo(f"Created temporary directory for proto files: {temp_proto_path}")

        # Step 1: Recover proto files from server
        click.echo(f"Connecting to gRPC server at {host} to retrieve proto files...")
        with RecoverService(
            host,
            temp_proto_path,
            use_tls=use_tls,
            root_certificates_path=root_cert,
            private_key_path=private_key,
            certificate_chain_path=cert_chain,
        ) as service:
            try:
                saved_files = service.recover_proto_files()
                if saved_files:
                    click.echo(f"Successfully recovered {len(saved_files)} proto files")
                    for file_path in saved_files:
                        click.echo(f"  - {file_path.name}")
                else:
                    click.echo("No proto files were recovered")
                    return
            except Exception as e:
                click.echo(f"Error recovering proto files: {e}", err=True)
                raise click.Abort() from e

        # Step 2: Generate client code from the recovered proto files
        click.echo(f"Generating {gen_type} client code in {output_dir}...")
        try:
            gen_type_literal = cast(Literal["default", "mypy", "betterproto", "pbreflect"], gen_type)
            run(
                str(temp_proto_path),
                str(output_dir),
                gen_type_literal,
                refresh,
                async_mode=async_mode.lower() == "true",
                template_dir=template_dir,
            )
            click.echo(f"Successfully generated client code in {output_dir}")
        except Exception as e:
            click.echo(f"Error generating client code: {e}", err=True)
            raise click.Abort() from e

        click.echo("Temporary proto files will be automatically deleted")


cli.add_command(get_protos)
cli.add_command(gen)
cli.add_command(generate_from_server)

if __name__ == "__main__":
    cli()
