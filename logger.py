import datetime
import os

from config import IST, SENT_FOLDER


class Logger:
    """Writes every message to both the console and a dated log file."""

    def __init__(self, log_folder: str):
        os.makedirs(log_folder, exist_ok=True)
        now            = datetime.datetime.now(IST)
        filename       = now.strftime("run_%Y-%m-%d_%H-%M-%S.log")
        self.log_path  = os.path.join(log_folder, filename)
        self.start_time = now
        self._write_header(now)

    def _write_header(self, now: datetime.datetime):
        self._append(f"{'='*60}")
        self._append(f"  AutoMailer Session Log")
        self._append(f"  Started : {now.strftime('%Y-%m-%d %H:%M:%S')}")
        self._append(f"{'='*60}\n")

    def _timestamp(self) -> str:
        return datetime.datetime.now(IST).strftime("%H:%M:%S")

    def _append(self, message: str):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def log(self, message: str):
        stamped = f"[{self._timestamp()}] {message}"
        print(stamped)
        self._append(stamped)

    def write_footer(self, sent: int, skipped: int, failed: int, csv_file: str, archived: bool):
        elapsed = datetime.datetime.now(IST) - self.start_time
        self._append(f"\n{'='*60}")
        self._append(f"  Session Summary")
        self._append(f"  CSV file  : {csv_file}")
        self._append(f"  ✅ Sent   : {sent}")
        self._append(f"  ⏭️  Skipped : {skipped}")
        self._append(f"  ❌ Failed : {failed}")
        self._append(f"  Archived  : {'Yes → ' + SENT_FOLDER + '/' if archived else 'No — stays in pending/ for retry'}")
        self._append(f"  Duration  : {str(elapsed).split('.')[0]}")
        self._append(f"  Ended     : {datetime.datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")
        self._append(f"{'='*60}\n")
        print(f"\n📄 Log saved → {self.log_path}")
