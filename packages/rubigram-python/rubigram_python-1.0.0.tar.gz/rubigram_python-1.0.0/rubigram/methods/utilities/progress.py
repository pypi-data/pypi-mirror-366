
import sys
import time
from .colors import Colors


class Progress:
    def __init__(self):
        self.start_time = time.time()
        self.total_size = None
        self.last_uploaded = 0
        self.last_time = self.start_time

    def __call__(self, total_size: int, uploaded_bytes: int) -> None:
        if self.total_size is None:
            self.total_size = total_size

        now = time.time()
        delta_bytes = uploaded_bytes - self.last_uploaded
        delta_time = now - self.last_time
        speed_bps = delta_bytes / delta_time if delta_time > 0 else 0

        if speed_bps >= 3 * 1024 * 1024:
            speed_color = Colors.GREEN
            speed_val = speed_bps / (1024 * 1024)
            speed_unit = f"{Colors.CYAN}Mb/s{Colors.RESET}"
        elif speed_bps >= 1 * 1024 * 1024:
            speed_color = Colors.YELLOW
            speed_val = speed_bps / (1024 * 1024)
            speed_unit = f"{Colors.CYAN}Mb/s{Colors.RESET}"
        else:
            speed_color = Colors.RED
            speed_val = speed_bps / (1024 * 1024)
            speed_unit = f"{Colors.CYAN}Mb/s{Colors.RESET}"

        percent = min(uploaded_bytes / self.total_size * 100, 100)
        current_mb = uploaded_bytes / (1024 ** 2)
        total_mb = self.total_size / (1024 ** 2)
        current_mb = min(current_mb, total_mb)

        if percent >= 100:
            percent_color = Colors.GREEN
            current_mb_color = Colors.GREEN
        elif percent >= 99:
            percent_color = Colors.GREEN
            current_mb_color = Colors.MAGENTA
        elif percent >= 75:
            percent_color = Colors.MAGENTA
            current_mb_color = Colors.CYAN
        elif percent >= 50:
            percent_color = Colors.YELLOW
            current_mb_color = Colors.YELLOW
        elif percent >= 25:
            percent_color = Colors.ORANGE
            current_mb_color = Colors.ORANGE
        else:
            percent_color = Colors.RED
            current_mb_color = Colors.RED

        percent_str = f"{percent_color}{percent:6.2f}%{Colors.RESET}"
        current_mb_str = f"{current_mb_color}{current_mb:6.2f}MB{Colors.RESET}"
        total_mb_str = f"{Colors.MAGENTA}{total_mb:.2f}MB{Colors.RESET}"
        tps_str = f"{Colors.ORANGE}TPS{Colors.RESET}"
        speed_str = f"{speed_color}{speed_val:6.2f}{Colors.RESET} {speed_unit}"

        sys.stdout.write(
            f'\r{percent_str}  {Colors.WHITE}[{current_mb_str} / {total_mb_str}]{Colors.RESET}  {tps_str} {speed_str}'
        )
        sys.stdout.flush()

        self.last_uploaded = uploaded_bytes
        self.last_time = now

        if uploaded_bytes >= self.total_size:
            print()
