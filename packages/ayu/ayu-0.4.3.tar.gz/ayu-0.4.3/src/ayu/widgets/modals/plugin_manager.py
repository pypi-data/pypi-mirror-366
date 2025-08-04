from typing import TYPE_CHECKING, Any
import json


if TYPE_CHECKING:
    from ayu.app import AyuApp

from textual import on, work
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Footer,
    Label,
    Switch,
    Select,
    Input,
    Collapsible,
    Rule,
    DataTable,
)
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual_autocomplete import AutoComplete, TargetState, DropdownItem

from ayu.utils import OptionType, run_plugin_collection
from ayu.constants import OPTIONS_TO_DISABLE, PLUGIN_JSON_FILE, PLUGIN_JSON_PATH
from ayu.plugin_list_fetcher import get_plugin_list
from ayu.command_builder import Plugin, build_command


class ModalPlugin(ModalScreen):
    app: "AyuApp"
    available_plugin_list: list[str] = reactive([], init=False)
    """Plugins loaded from PyPi"""
    plugin_option_dict: reactive[dict] = reactive({}, init=False)
    """Dict of available plugins {plugin_name: plugin_dict}"""
    selected_options_dict: reactive[dict] = reactive({}, init=False)
    """Dict of active options {optionname:value}"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close", show=True),
    ]

    # @work(thread=True, description="Collect Plugins")
    async def on_mount(self):
        # Load Plugins on first Load
        if not PLUGIN_JSON_FILE.exists():
            self.update_plugins()
        else:
            self.load_plugins()

    def compose(self):
        with Vertical():
            yield Footer()

            # self.button.loading = True
            yield Button("Refresh plugin list", id="button_refresh_plugin")
            yield PluginInput(id="input_plugin_list")
            yield PluginAutoComplete(
                target="#input_plugin_list",
            ).data_bind(available_plugin_list=ModalPlugin.available_plugin_list)

            with VerticalScroll():
                for plugin, plugin_dict in self.app.plugin_option_dict.items():
                    yield PluginEntry(
                        plugin_name=plugin, plugin_dict=plugin_dict, installed=True
                    )

    def watch_plugin_option_dict(self):
        # self.notify(f"modal: {self.plugin_option_dict.keys()}", markup=False)
        # Refresh like this turns all other settings to default
        # self.refresh(recompose=True)
        for plugin, plugin_dict in self.plugin_option_dict.items():
            if plugin not in self.loaded_plugins:
                vs = self.query_one(VerticalScroll)
                vs.mount(PluginEntry(plugin_name=plugin, plugin_dict=plugin_dict))

    def watch_available_plugin_list(self):
        if self.available_plugin_list:
            # self.notify(f"{len(self.available_plugin_list)}", markup=False)
            self.query_one("#input_plugin_list", Input).display = True
            self.query_one(
                "#input_plugin_list", Input
            ).placeholder = (
                f"Type to search for plugins (found {len(self.available_plugin_list)})"
            )
            self.query_one("#button_refresh_plugin", Button).loading = False
        else:
            self.query_one("#input_plugin_list", Input).display = False
            self.query_one("#button_refresh_plugin", Button).loading = True

    def watch_selected_options_dict(self): ...

    @on(Button.Pressed, "#button_refresh_plugin")
    def refresh_plugin_list(self, event: Button.Pressed):
        # TODO Make Loading work on refresh
        self.update_plugins()

    @work(thread=True, description="Refresh Plugins")
    async def update_plugins(self):
        # Create Pluginfolder and load plugin_dict
        PLUGIN_JSON_PATH.mkdir(exist_ok=True, parents=True)
        PLUGIN_JSON_FILE.touch(exist_ok=True)
        await self.fetch_plugin_list()
        with open(PLUGIN_JSON_FILE, "w") as json_file:
            json.dump(self.available_plugin_list, json_file)

    def load_plugins(self):
        """load preloaded pluginlist from file"""
        with open(PLUGIN_JSON_FILE, "r") as json_file:
            self.available_plugin_list = json.load(json_file)

    # @work(thread=True)
    async def fetch_plugin_list(self):
        self.available_plugin_list = await get_plugin_list()
        self.notify(f"found {len(self.available_plugin_list)} plugins", timeout=1)

    @on(Input.Submitted, "#input_plugin_list")
    @work(thread=True, description="Load new PluginInfos")
    async def load_plugin_into_options(self, event: Input.Submitted):
        new_plugin_name = event.input.value
        if new_plugin_name not in self.available_plugin_list:
            self.notify(
                title="Error", message="plugin not in pluginlist", severity="warning"
            )
        else:
            new_plugin = Plugin(name=new_plugin_name, is_installed=False, options=[])
            # self.notify(f"{new_plugin}", markup=False)

            # Update option dict with new plugins
            command = build_command(plugins=[new_plugin], pytest_options=["--help"])
            await run_plugin_collection(command=command)
            self.query_one(Input).clear()
            # self.mutate_reactive(ModalPlugin.plugin_option_dict)

    @property
    def loaded_plugins(self) -> list[str]:
        return [plugin.plugin_name for plugin in self.query(PluginEntry)]


class PluginEntry(Vertical):
    def __init__(
        self,
        plugin_name: str,
        plugin_dict: dict,
        installed: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.plugin_name = plugin_name
        self.installed = installed
        self.plugin_dict = plugin_dict
        self.plugin = Plugin(
            name=self.plugin_name, is_installed=self.installed, options=[]
        )

    def compose(self):
        with PlugInCollapsible(title=self.plugin_name):
            for option_dict in self.plugin_dict["options"]:
                option_name = " ".join(option_dict["names"])

                # Skip certain options for now
                if option_name in OPTIONS_TO_DISABLE:
                    continue

                match option_dict["type"]:
                    case OptionType.BOOL:
                        yield BoolOption(option_dict=option_dict)
                    case OptionType.STR:
                        yield StringOption(option_dict=option_dict)
                    case OptionType.LIST:
                        yield ListOption(option_dict=option_dict)
                    case OptionType.SELECTION:
                        yield SelectionOption(option_dict=option_dict)


class PluginInput(Input):
    def on_mount(self):
        self.display = False


class PluginAutoComplete(AutoComplete):
    available_plugin_list: reactive[list[str]] = reactive([])

    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        # Filter candidates based on target_state.text
        return [DropdownItem(main=plugin) for plugin in self.available_plugin_list]

    # Display Infos on completion about plugin
    # Maybe even better on typing
    def post_completion(self) -> None:
        self.notify(f"press enter to add plugin {self.target.value}")
        return super().post_completion()

    # TODO Add ctrl + j/k navigation


class PlugInCollapsible(Collapsible):
    amount_changed: reactive[int] = reactive(0)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.plugin = self.title

    def on_mount(self):
        self.update_amount()

    @on(Switch.Changed)
    @on(Input.Changed)
    @on(Select.Changed)
    @on(DataTable.RowSelected)
    def update_amount(self):
        self.amount_changed = sum(
            [widget.was_changed for widget in self._contents_list if widget.was_changed]
        )

    def watch_amount_changed(self):
        if self.amount_changed > 0:
            amount_str = (
                f"[$success]{self.amount_changed}/{len(self._contents_list)}[/]"
            )
        else:
            amount_str = f"[$error]{self.amount_changed}/{len(self._contents_list)}[/]"
        self.title = f"{amount_str} {self.plugin}"


class BoolOption(Vertical):
    app: "AyuApp"
    option: reactive[str] = reactive("", init=False)
    option_value: reactive[str] = reactive("", init=False)
    complete_option: reactive[str | None] = reactive(None, init=False)
    was_changed: reactive[bool] = reactive(False, init=False)

    def __init__(self, option_dict: dict[str, Any], *args, **kwargs) -> None:
        self.option_dict = option_dict
        super().__init__(*args, **kwargs)
        self.classes = "optionwidget"
        self.option = " ".join(option_dict["names"])
        self.option_value = option_dict["default"]

    def on_mount(self):
        self.query_one(Label).tooltip = self.option_dict["help"]
        # Set to current Value
        dest = self.option_dict["dest"]
        if dest != self.option_dict["default"]:
            self.query_one(Switch).value = self.app.selected_options_dict[dest]

    def compose(self):
        with Horizontal():
            yield Label(f"{self.option} [gray]{self.option_dict['dest']}[/]")
            yield Switch(value=self.option_dict["default"])
        yield Rule()
        return super().compose()

    def on_switch_changed(self, event: Switch.Changed):
        self.option_value = event.switch.value

    def watch_option_value(self):
        if self.option_value == self.option_dict["default"]:
            self.complete_option = None
        else:
            self.complete_option = f"{self.option}"

    def watch_was_changed(self):
        if self.was_changed:
            self.query_one(Label).update(
                f"[$success]{self.option}[/] [gray]{self.option_dict['dest']}[/]"
            )
        else:
            self.query_one(Label).update(
                f"{self.option} [gray]{self.option_dict['dest']}[/]"
            )

    # complete option string for the command builder
    def watch_complete_option(self):
        if self.complete_option is None:
            # self.app.options.pop(self.flag)
            self.was_changed = False
        else:
            # self.app.options[self.flag] = self.complete_flag
            self.was_changed = True

        # self.app.update_options()


class StringOption(Vertical):
    app: "AyuApp"
    option: reactive[str] = reactive("", init=False)
    option_value: reactive[str] = reactive("", init=False)
    complete_option: reactive[str | None] = reactive(None, init=False)
    was_changed: reactive[bool] = reactive(False, init=False)

    def __init__(self, option_dict: dict[str, str], *args, **kwargs) -> None:
        self.option_dict = option_dict
        super().__init__(*args, **kwargs)
        self.classes = "optionwidget"
        self.option = " ".join(option_dict["names"])
        self.option_value = option_dict["default"]

    def on_mount(self):
        self.query_one(Label).tooltip = self.option_dict["help"]
        # Set to current Value
        dest = self.option_dict["dest"]
        if dest != self.option_dict["default"]:
            value = self.app.selected_options_dict[dest]
            self.query_one(Input).value = f"{value}" if isinstance(value, list) else ""

    def compose(self):
        with Horizontal():
            yield Label(f"{self.option} [gray]{self.option_dict['dest']}[/]")
            yield Input(placeholder=f"default: {self.option_dict['default']}")
        yield Rule()
        return super().compose()

    def on_input_changed(self, event: Input.Changed):
        self.option_value = event.input.value

    def watch_option_value(self):
        if self.option_value in [self.option_dict["default"], ""]:
            self.complete_option = None
        else:
            self.complete_option = f"{self.option}={self.option_value}"

    def watch_was_changed(self):
        if self.was_changed:
            self.query_one(Label).update(
                f"[$success]{self.option}[/] [gray]{self.option_dict['dest']}[/]"
            )
        else:
            self.query_one(Label).update(
                f"{self.option} [gray]{self.option_dict['dest']}[/]"
            )

    def watch_complete_option(self):
        if self.complete_option is None:
            # self.app.options.pop(self.option)
            self.was_changed = False
        else:
            # self.app.options[self.option] = self.complete_option
            self.was_changed = True
        # self.app.update_options()


class SelectionOption(Vertical):
    app: "AyuApp"
    option: reactive[str] = reactive("", init=False)
    option_value: reactive[str] = reactive("", init=False)
    complete_option: reactive[str | None] = reactive(None, init=False)
    was_changed: reactive[bool] = reactive(False, init=False)

    def __init__(self, option_dict: dict[str, str | list], *args, **kwargs) -> None:
        self.option_dict = option_dict
        super().__init__(*args, **kwargs)
        self.classes = "optionwidget"
        self.option = " ".join(option_dict["names"])
        self.option_value = option_dict["default"]

    def compose(self):
        with Horizontal():
            yield Label(f"{self.option} [gray]{self.option_dict['dest']}[/]")
            with self.prevent(Select.Changed):
                yield Select(
                    value=self.option_dict["default"],
                    options=(
                        (choice, choice) for choice in self.option_dict["choices"]
                    ),
                    allow_blank=False,
                )
        yield Rule()
        return super().compose()

    def on_mount(self):
        self.query_one(Label).tooltip = self.option_dict["help"]
        # Set to current Value
        dest = self.option_dict["dest"]
        if dest != self.option_dict["default"]:
            self.query_one(Select).value = self.app.selected_options_dict[dest]

    def on_select_changed(self, event: Select.Changed):
        self.option_value = event.select.value

    def watch_option_value(self):
        if self.option_value == self.option_dict["default"]:
            self.complete_option = None
        else:
            self.complete_option = f"{self.option}={self.option_value}"

    def watch_was_changed(self):
        if self.was_changed:
            self.query_one(Label).update(
                f"[$success]{self.option}[/] [gray]{self.option_dict['dest']}[/]"
            )
        else:
            self.query_one(Label).update(
                f"{self.option} [gray]{self.option_dict['dest']}[/]"
            )

    def watch_complete_option(self):
        if self.complete_option is None:
            # self.app.options.pop(self.option)
            self.was_changed = False
        else:
            # self.app.options[self.option] = self.complete_option
            self.was_changed = True
        # self.app.update_options()


class ListOption(Vertical):
    app: "AyuApp"
    option: reactive[str] = reactive("", init=False)
    option_value: reactive[list[str]] = reactive(list, init=False)
    complete_option: reactive[str | None] = reactive(None, init=False)
    was_changed: reactive[bool] = reactive(False, init=False)

    def __init__(self, option_dict: dict[str, list], *args, **kwargs) -> None:
        self.option_dict = option_dict
        super().__init__(*args, **kwargs)
        self.classes = "optionwidget"
        self.option = " ".join(option_dict["names"])
        self.option_value = option_dict["default"]

    def on_mount(self):
        self.query_one(Label).tooltip = self.option_dict["help"]
        dest = self.option_dict["dest"]
        dest_values = self.app.selected_options_dict[dest]
        if dest_values != self.option_dict["default"]:
            for value in dest_values:
                self.add_new_value(new_value=value)

    def compose(self):
        with Horizontal():
            yield Label(f"{self.option} [gray]{self.option_dict['dest']}[/]")
            yield Input(placeholder="enter a value and press enter to add to list")
        self.list_table = DataTable(cursor_type="row", show_header=False)
        self.list_table.add_column("option", key="option")
        self.list_table.add_column("remove", key="remove")
        self.list_table.display = False

        yield self.list_table
        yield Rule()
        return super().compose()

    # TODO Add Input validation to prevent adding the same
    def on_input_submitted(self, event: Input.Submitted):
        new_value = event.input.value.strip()
        if new_value:
            self.add_new_value(new_value=new_value)
            event.input.clear()

    def add_new_value(self, new_value):
        if new_value in self.list_table.rows.keys():
            return

        self.list_table.add_row(
            new_value,
            ":cross_mark: click to remove",
            key=new_value,
        )
        self.option_value.append(new_value)
        self.mutate_reactive(ListOption.option_value)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.option_value.remove(event.row_key)
        self.list_table.remove_row(event.row_key)
        self.mutate_reactive(ListOption.option_value)
        # TODO When having a long entry and a scrollbar appears
        # The column widths doesnt reset back

    def watch_option_value(self):
        if self.option_value == self.option_dict["default"]:
            self.complete_option = None
            # self.parent.parent.update_amount()
        else:
            if len(self.option_value) == 1:
                self.complete_option = f"{self.option}={self.option_value[0]}"
            else:
                self.complete_option = f'{self.option}="{",".join(self.option_value)}"'

    def watch_was_changed(self):
        if self.was_changed:
            self.query_one(Label).update(
                f"[$success]{self.option}[/] [gray]{self.option_dict['dest']}[/]"
            )
        else:
            self.query_one(Label).update(
                f"{self.option} [gray]{self.option_dict['dest']}[/]"
            )
            self.query_one(Input).focus()
        self.list_table.display = self.was_changed

    def watch_complete_option(self):
        if self.complete_option is None:
            # self.app.options.pop(self.option)
            self.was_changed = False
        else:
            # self.app.options[self.option] = self.complete_option
            self.was_changed = True
        # self.app.update_options()
