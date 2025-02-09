from rich.console import Console
from rich.text import Text


class CustomPrinter(Console):
    def __init__(self, is_debug: bool = False):
        super().__init__()
        self.is_debug = is_debug

    def success(self, message: str):
        """Print success messages with enhanced formatting"""
        self._print_formatted("[✓]", message, "green", "bold")

    def error(self, message: str):
        """Print error messages with enhanced formatting"""
        self._print_formatted("[✗]", message, "red", "bold")

    def info(self, message: str):
        """Print info messages with enhanced formatting"""
        self._print_formatted("[ℹ]", message, "cyan")

    def warn(self, message: str):
        """Print warning messages with enhanced formatting"""
        self._print_formatted("[⚠]", message, "yellow", "bold")

    def debug(self, message: str):
        """Print debug messages with enhanced formatting"""
        if self.is_debug:
            self._print_formatted("[⚙]", message, "magenta", "dim")

    def _print_formatted(self, symbol: str, message: str, color: str, *styles: iter):
        text = Text()
        text.append(f"{symbol} ", style=color)
        text.append(message, style=" ".join([color] + list(styles)))
        self.print(text)


if __name__ == "__main__":
    printer = CustomPrinter()

    printer.success("Successfully processed order #12345")
    printer.error("Failed to connect to database")
    printer.info("Processing new order...")
    printer.warn("Low disk space")
    printer.debug("Connection attempt: 3")
