import asyncio
from typing import TYPE_CHECKING, List

from rich.console import Group
from rich.text import Text

from ..message import ToolCall
from ..tui import ColorStyle, CropAboveLive, console, render_dot_status
from ..utils.exception import format_exception

if TYPE_CHECKING:
    from .handler import InterruptHandler
    from .instance import ToolInstance


class ToolDisplayManager:
    """Manages tool execution display and UI."""

    @staticmethod
    def generate_status_text(tool_calls: List[ToolCall]) -> Text:
        running_tool_calls = [tc for tc in tool_calls if tc.status == "processing"]
        """Generate status text for tool execution."""
        if len(running_tool_calls) == 1:
            return Text.assemble(
                "Running ",
                (
                    ToolCall.get_display_tool_name(running_tool_calls[0].tool_name),
                    "bold",
                ),
                " ",
                style=ColorStyle.CLAUDE,
            )
        else:
            tool_counts = {}
            for tc in running_tool_calls:
                tool_counts[tc.tool_name] = tool_counts.get(tc.tool_name, 0) + 1
            tool_names = [
                Text.assemble(
                    (ToolCall.get_display_tool_name(name), "bold"),
                    " * " + str(count) if count > 1 else "",
                    " ",
                )
                for name, count in tool_counts.items()
            ]
            return Text.assemble("Running ", *tool_names, style=ColorStyle.CLAUDE)

    @staticmethod
    def create_live_group(tool_instances: List["ToolInstance"]) -> list:
        """Create the live group for display."""
        live_group = []
        # Sort tool instances: uncompleted first, then completed
        sorted_instances = sorted(tool_instances, key=lambda ti: ti.is_completed())
        for ti in sorted_instances:
            live_group.append("")
            live_group.append(ti.tool_result())
        return live_group

    @staticmethod
    async def live_display(
        tool_instances: List["ToolInstance"],
        tool_calls: List[ToolCall],
        interrupt_handler: "InterruptHandler",
    ):
        try:
            status = render_dot_status(
                status=ToolDisplayManager.generate_status_text(tool_calls)
            )

            with CropAboveLive(
                refresh_per_second=10, console=console.console, transient=True
            ) as live:
                live_group = ToolDisplayManager.create_live_group(tool_instances)
                while (
                    any(ti.is_running() for ti in tool_instances)
                    and not interrupt_handler.interrupted
                ):
                    # TODO: cache optimization for update
                    # status.update(status=ToolDisplayManager.generate_status_text(tool_calls))
                    live.update(Group(*live_group, status))
                    await asyncio.sleep(0.1)
                live.update(Group(*live_group))
            for ti in tool_instances:
                console.print()
                console.print(ti.tool_result())
        except Exception as e:
            console.print(Text.assemble(format_exception(e), style=ColorStyle.ERROR))
            raise e
