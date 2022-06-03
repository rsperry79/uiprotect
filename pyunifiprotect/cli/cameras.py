from dataclasses import dataclass
from typing import Optional

import typer

from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.cli import base
from pyunifiprotect.data import Camera

app = typer.Typer()

ARG_DEVICE_ID = typer.Argument(None, help="ID of camera to select for subcommands")


@dataclass
class CameraContext(base.CliContext):
    devices: dict[str, Camera]
    device: Camera | None = None


ALL_COMMANDS, DEVICE_COMMANDS = base.init_common_commands(app)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, device_id: Optional[str] = ARG_DEVICE_ID) -> None:
    """
    UniFi Protect Camera CLI.

    Returns full list of Cameras without any arguments passed.
    """

    protect: ProtectApiClient = ctx.obj.protect
    context = CameraContext(
        protect=ctx.obj.protect, device=None, devices=protect.bootstrap.cameras, output_format=ctx.obj.output_format
    )
    ctx.obj = context

    if device_id is not None and device_id not in ALL_COMMANDS:
        if (device := protect.bootstrap.cameras.get(device_id)) is None:
            typer.secho("Invalid camera ID", fg="red")
            raise typer.Exit(1)
        ctx.obj.device = device

    if not ctx.invoked_subcommand:
        if device_id in ALL_COMMANDS:
            ctx.invoke(ALL_COMMANDS[device_id], ctx)
            return

        if ctx.obj.device is not None:
            base.print_unifi_obj(ctx.obj.device)
            return

        base.print_unifi_dict(ctx.obj.devices)
