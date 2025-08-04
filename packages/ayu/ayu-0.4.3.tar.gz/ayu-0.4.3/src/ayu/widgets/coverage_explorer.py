from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ayu.app import AyuApp

from textual import on, work
from textual.binding import Binding
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, DataTable, TextArea

from ayu.utils import EventType, build_bar


class CoverageExplorer(Vertical):
    app: "AyuApp"

    coverage_dict: reactive[dict] = reactive({})
    selected_file: reactive[str] = reactive("")
    selected_line: reactive[list] = reactive([])

    def on_mount(self):
        self.display = False

        self.app.dispatcher.register_handler(
            event_type=EventType.COVERAGE,
            handler=lambda msg: self.update_coverage_dict(msg),
        )

    def compose(self):
        yield CoverageLabel("[bold]Test Coverage[/]")
        with Vertical():
            with Horizontal():
                yield CoverageTable(id="table_coverage").data_bind(
                    CoverageExplorer.coverage_dict
                )
                yield MissingLinesTable(id="table_lines").data_bind(
                    coverage_dict=CoverageExplorer.coverage_dict,
                    selected_file=CoverageExplorer.selected_file,
                )
            yield CoverageFilePreview("Preview").data_bind(
                selected_file=CoverageExplorer.selected_file,
                selected_line=CoverageExplorer.selected_line,
            )

    def watch_disabled(self, disabled: bool) -> None:
        return super().watch_disabled(disabled)

    def update_coverage_dict(self, msg):
        self.coverage_dict = msg["coverage_dict"]

    @on(DataTable.RowHighlighted, "#table_coverage")
    def update_selected_file(self, event: DataTable.RowHighlighted):
        if event.row_key:
            file_name = self.query_one(CoverageTable).get_row(event.row_key)[0]
            self.selected_file = file_name

    @on(DataTable.RowHighlighted, "#table_lines")
    # use an exclusive worker here to support holding down j/k
    # which would otherwise give a IndexError
    @work(thread=True, exclusive=True, description="Update Selected Line")
    def update_selected_line(self, event: DataTable.RowHighlighted):
        if event.row_key:
            if isinstance(self.app.focused, CoverageTable):
                self.selected_line = self.coverage_dict[self.selected_file][
                    "lines_missing"
                ][0]
            else:
                line = self.query_one(MissingLinesTable).get_row(event.row_key)[0]
                self.selected_line = line


class CoverageLabel(Label):
    "Label for Coverage Explorer"


class CoverageTable(DataTable):
    """General Table for Coverage Information"""

    BINDINGS = [
        Binding("j, down", "cursor_down", "down", key_display="j/↓"),
        Binding("k, up", "cursor_up", "up", key_display="k/↑"),
        Binding("l, right", "go_to_lines", "to lines"),
    ]

    coverage_dict: reactive[dict] = reactive({})
    COLUMNS = ["Name", "Statements", "Missing", "Covered", ""]

    def on_mount(self):
        self.cursor_type = "row"
        self.border_title = "Coverage Report"

        for column in self.COLUMNS:
            self.add_column(label=column, width=None if column else 10)

    # Go to first row, when navigating down on last row
    def action_cursor_down(self) -> None:
        if self.cursor_coordinate.row == (self.row_count - 1):
            self.move_cursor(row=0)
            return
        return super().action_cursor_down()

    # Go to last row, when navigating up on first row
    def action_cursor_up(self) -> None:
        if self.cursor_coordinate.row == 0:
            self.move_cursor(row=self.row_count - 1)
            return
        return super().action_cursor_up()

    def watch_coverage_dict(self):
        if not self.coverage_dict:
            return

        current_line = self.cursor_row or 0
        self.clear()

        for module_name, module_dict in self.coverage_dict.items():
            self.add_row(
                module_name,
                module_dict["n_statements"],
                module_dict["n_missed"],
                f"{module_dict['percent_covered']:05.2f}%",
                build_bar(module_dict["percent_covered"]),
                key=module_name,
            )

        # go to last known cursor position
        self.move_cursor(row=current_line)

    @on(DataTable.RowSelected)
    def test(self, event: DataTable.RowSelected): ...

    def action_go_to_lines(self):
        self.app.action_focus_next()


class MissingLinesTable(DataTable):
    """Table for Missing Lines"""

    BINDINGS = [
        Binding("j, down", "cursor_down", "down", key_display="j/↓"),
        Binding("k, up", "cursor_up", "up", key_display="k/↑"),
        Binding("h, left", "back_to_coverage", "to cov table"),
    ]
    coverage_dict: reactive[dict] = reactive({})
    selected_file: reactive[str] = reactive("")

    def on_mount(self):
        self.cursor_type = "row"
        self.add_columns(
            "Missing Lines",
        )

    # Go to first row, when navigating down on last row
    def action_cursor_down(self) -> None:
        if self.cursor_coordinate.row == (self.row_count - 1):
            self.move_cursor(row=0)
            return
        return super().action_cursor_down()

    # Go to last row, when navigating up on first row
    def action_cursor_up(self) -> None:
        if self.cursor_coordinate.row == 0:
            self.move_cursor(row=self.row_count - 1)
            return
        return super().action_cursor_up()

    def watch_selected_file(self):
        if not self.selected_file:
            return

        self.clear()

        for missing_lines in self.coverage_dict[self.selected_file]["lines_missing"]:
            self.add_row(missing_lines)

    def action_back_to_coverage(self):
        self.app.action_focus_previous()


class CoverageFilePreview(TextArea):
    """Preview of Lines in source file"""

    selected_file: reactive[str] = reactive("")
    selected_line: reactive[int] = reactive(0)

    def on_mount(self):
        self.language = "python"
        self.show_line_numbers = True
        self.read_only = True
        self.border_title = "File Preview"

    def watch_selected_file(self):
        if self.selected_file:
            with open(self.selected_file, "r") as file:
                self.text = file.read()
            self.border_title = self.selected_file

    def watch_selected_line(self):
        if self.selected_line:
            self.move_cursor(location=(self.selected_line - 1, 0))

            self.scroll_to(
                y=self.selected_line - 5,  # 4 rows space on top
                animate=True,
                duration=0.1,
                force=True,
            )
