from __future__ import annotations
from datetime import datetime
import json

from rich.json import JSON
from rich.text import Text

from textual.app import ComposeResult
from textual.containers import ScrollableContainer

from textual.widget import Widget
from textual.widgets import Label, Static, TextArea
from textual.widgets.text_area import TextAreaTheme


class LineDisplay(Widget):
    DEFAULT_CSS = """
    LineDisplay {        
        padding: 0 1;
        margin: 1 0;
        width: auto;
        height: auto;        
        Label {
            width: 1fr;
        }  
        .json {
            width: auto;        
        }
        .nl {
            width: auto;
        }  
    }
    """

    def __init__(self, line: str, text: Text, timestamp: datetime | None) -> None:
        self.line = line
        self.text = text
        self.timestamp = timestamp
        super().__init__()

    def process_json(self, data):
        """Recursively process JSON to convert escaped newlines to actual newlines."""
        if isinstance(data, dict):
            return {k: self.process_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.process_json(item) for item in data]
        elif isinstance(data, str):
            # First replace escaped newlines, then literal newlines
            return data.encode().decode("unicode-escape")
        return data

    def compose(self) -> ComposeResult:
        try:
            # Try to parse as JSON
            json_data = json.loads(self.line)
            # Process JSON to handle newlines
            processed_json = self.process_json(json_data)
            # Pretty print the JSON with indentation
            formatted_json = json.dumps(processed_json, indent=2, ensure_ascii=False)
            # Create a TextArea with enhanced JSON highlighting
            text_area = TextArea(
                formatted_json.encode().decode(
                    "unicode-escape"
                ),  # Handle any remaining escapes
                language="json",  # Enable JSON syntax highlighting
                theme="monokai",  # Use monokai theme which has good JSON support
                read_only=True,  # Make it read-only since it's for display
                soft_wrap=True,  # Enable word wrapping
                tab_behavior="focus",  # Allow tabbing out of the textarea
                show_line_numbers=False,  # Hide line numbers for cleaner display
            )
            yield text_area
        except json.JSONDecodeError:
            # If not JSON, show plain text
            text_area = TextArea(
                str(self.text), read_only=True, soft_wrap=True, show_line_numbers=False
            )
            yield text_area


class LinePanel(ScrollableContainer):
    DEFAULT_CSS = """
    LinePanel {
        background: $panel;        
        overflow-y: auto;
        overflow-x: auto;
        border: blank transparent;                
        scrollbar-gutter: stable;
        &:focus {
            border: heavy $accent;
        }
    }
    """

    async def update(self, line: str, text: Text, timestamp: datetime | None) -> None:
        with self.app.batch_update():
            await self.query(LineDisplay).remove()
            await self.mount(LineDisplay(line, text, timestamp))
