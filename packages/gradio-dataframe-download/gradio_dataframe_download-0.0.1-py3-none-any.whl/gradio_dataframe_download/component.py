"""gr.Button() component."""
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gradio.components.base import Component
from gradio.events import Events
from gradio_client.documentation import document
from narwhals import from_native
from narwhals.dataframe import DataFrame
from narwhals.typing import IntoFrame

if TYPE_CHECKING:
    from gradio.components import Timer

@document()
class DataFrameDownload(Component):
    """Download button component for client-side DataFrame download as CSV.

    A DataFrame is passed as `value` to this component, serialized to JSON,
    and sent to the frontend. The frontend JavaScript converts the JSON data
    into a CSV string and triggers a download.
    """
    EVENTS = [Events.click]

    def __init__(
        self,
        label: str = "Download DataFrame",
        value: IntoFrame | Callable | None = None,
        *,
        variant: Literal["primary", "secondary", "stop"] = "secondary",
        visible: bool = True,
        size: Literal["sm", "md", "lg"] = "lg",
        icon: str | Path | None = None,
        scale: int | None = None,
        min_width: int | None = None,
        interactive: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
    ):
        """Initialises `DataFrameDownload` button component.

        Args:
            label: Component label text.

            value: A DataFrame to be serialised for download or a callable.

            variant: Style variant; 'primary', 'secondary' or 'stop'.

            visible: Component visibility flag.

            size: Size of the button; 'sm', 'md' or 'lg'.

            icon: URL or path to the icon file to display within the button.

            scale: Relative size compared to adjacent Components.

            min_width: Minimum pixel width (if sufficient screen space).

            interactive: Component interactivity flag.

            elem_id: Optional string assigned as component ID in the HTML DOM.

            elem_classes: CSS classes assigned to component in HTML DOM.

            render: `Blocks` context render flag.
        """
        super().__init__(
            value=value,
            label=label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render
        )

        self.icon = self.serve_static_file(icon)
        self.variant = variant
        self.size = size

    def postprocess(self, value: IntoFrame | None = None) -> str | None:
        """Convert the value returned by a `Gradio` function to JSON.

        Args:
            value: A DataFrame object.
        
        Returns:
            A DataFrame serialized as JSON in 'split' orientation, or None.
        """
        nwdata = from_native(value, pass_through=True)
        if isinstance(nwdata, DataFrame):
            # non-serializable types converted to str - we export to CSV anyway
            return json.dumps(
                {
                    "columns": nwdata.columns,
                    "data": nwdata.to_numpy().tolist()
                },
                default=str
            )
        return

    def preprocess(self, _: str | None = None) -> None:
        """Convert the frontend value to a python-native data structure.

        The function is not used as `DataFrameDownload` does not pass values
        from the frontend.

        _: Not used.

        Returns:
            None.
        """
        return None
    
    def api_info(self) -> dict[str, str]:
        """Provides information for the API documentation."""
        return {
            "type": "string",
            "description": "A JSON string representing the DataFrame."
        }
    
    def example_inputs(self) -> None:
        return None

