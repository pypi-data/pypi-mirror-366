from pathlib import Path

from textual.app import App
from textual.reactive import reactive

from dravik.models import AppState, LedgerSnapshot
from dravik.screens import (
    ChartsScreen,
    ErrorScreen,
    HelpScreen,
    QuitScreen,
    ReportsScreen,
    TransactionsScreen,
)
from dravik.services import AppServices

EMPTY_STATE = AppState(
    accounts_tree_filters=[],
    transactions_list_filters={},
    ledger_data=LedgerSnapshot(
        balances={},
        transactions=[],
        commodities=set(),
    ),
    account_labels={},
    currency_labels={},
    pinned_accounts=[],
    errors=[],
    charts_filters={
        "from_date": None,
        "to_date": None,
        "account": None,
        "depth": None,
        "etc_threshold": None,
        "currency": None,
    },
    reports_filters={
        "from_date": None,
        "to_date": None,
    },
)


class Dravik(App[None]):
    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("t", "switch_mode('transactions')", "Transactions"),
        ("\\", "switch_mode('help')", "Help"),
        ("c", "switch_mode('charts')", "Charts"),
        ("p", "switch_mode('reports')", "Reports"),
        ("q", "request_quit", "Quit"),
    ]
    MODES = {
        "transactions": TransactionsScreen,
        "help": HelpScreen,
        "charts": ChartsScreen,
        "reports": ReportsScreen,
        "error": ErrorScreen,
    }

    state: reactive[AppState] = reactive(lambda: EMPTY_STATE)

    def action_request_quit(self) -> None:
        self.app.push_screen(QuitScreen())

    def __init__(self, config_dir: str | None = None) -> None:
        self.config_dir = (
            Path(config_dir) if config_dir else Path.home() / ".config" / "dravik"
        )
        self.config_path = self.config_dir / "config.json"
        self.services = AppServices(self)
        super().__init__()

    def on_mount(self) -> None:
        self.services.create_configs()

        try:
            self.services.initial_check()
        except Exception as e:
            self.state.errors = [e]
            self.switch_mode("error")
            return

        self.state = self.services.get_initial_state()
        self.switch_mode("transactions")
