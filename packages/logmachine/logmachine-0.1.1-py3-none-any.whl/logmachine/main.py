import os
import re
import json
import logging

class CustomFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\x1b[36m',
        'INFO': '\x1b[34m',
        'WARNING': '\x1b[33m',
        'ERROR': '\x1b[31m',
        'SUCCESS': '\x1b[32m'
    }
    RESET = '\x1b[0m'
    BOLD = '\x1b[1m'
    LEVEL_FORMATS = {
        'DEBUG': BOLD + '[ DEBUG ]' + RESET,
        'INFO': BOLD + '[ INFO ]' + RESET,
        'WARNING': BOLD + '[ WARNING ]' + RESET,
        'ERROR': BOLD + '[ ERROR ]' + RESET,
        'SUCCESS': BOLD + '[ SUCCESS ]' + RESET
    }

    def format(self, record) -> str:
        try:
            username = os.getlogin()
        except Exception:
            username = os.environ.get('USER', 'unknown')

        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        level_fmt = self.LEVEL_FORMATS.get(levelname, f'{levelname}')
        level_fmt = f"{color}{level_fmt}{self.RESET}"
        record.asctime = self.formatTime(record, self.datefmt)
        module_file = record.pathname
        parent_dir = os.path.basename(os.path.dirname(record.pathname)) if module_file != '<stdin>' else 'stdin'

        return f"""{self.COLORS.get('DEBUG')}({username}{self.RESET} @ {self.COLORS.get('WARNING') + parent_dir + self.RESET}) 🤌 CL Timing: {color}[ {record.asctime} ]{self.RESET}
{level_fmt} {record.getMessage()}
"""

class ContribLog(logging.Logger):
    SUCCESS = 25

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, level=logging.DEBUG)
        logging.addLevelName(self.SUCCESS, "SUCCESS")
        self.log_file = kwargs.get('log_file', 'logs.log')
        self.error_file = kwargs.get('error_file', 'errors.log')
        self.debug_level = int(kwargs.get('debug_level', 0))
        self.verbose = kwargs.get('verbose', False)
        self.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.handlers = []

        # File handlers
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        eh = logging.FileHandler(self.error_file)
        eh.setLevel(logging.ERROR)

        # Console handler
        class CLStreamHandler(logging.StreamHandler):
            def __init__(self, *args, **kwargs):
                super().__init__()
                self.parse_log = kwargs.get('log_parser')

            def emit(self, record):
                try:
                    msg = self.format(record)
                    super().emit(record)
                    # print(self.parse_log(msg)) # This will be used in the future when central is implemented

                except Exception:
                    self.handleError(record)

        ch = CLStreamHandler(log_parser=self.parse_log)
        ch.setLevel(logging.DEBUG)

        formatter = CustomFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
        fh.setFormatter(formatter)
        eh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(eh)
        self.addHandler(ch)

        # Filter console output based on debug_level
        class DebugLevelFilter(logging.Filter):
            def __init__(self, debug_level):
                super().__init__()
                self.debug_level = int(debug_level)

            def filter(self, record):
                if self.debug_level == 0:
                    return True

                level_map = {
                    1: ['ERROR'],
                    2: ['SUCCESS'],
                    3: ['WARNING'],
                    4: ['INFO'],
                    5: ['ERROR','WARNING'],
                    6: ['INFO','SUCCESS'],
                    7: ['ERROR','WARNING','INFO']
                }
                allowed = level_map.get(self.debug_level, [])
                return record.levelname in allowed

        ch.addFilter(DebugLevelFilter(self.debug_level if not self.verbose else 0))

    def success(self, msg, *args, **kwargs) -> None:
        if self.isEnabledFor(self.SUCCESS):
            self._log(self.SUCCESS, msg, args, **kwargs)

    def parse_log(self, log_text) -> dict:
        log_text = log_text.strip()
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        clean = ansi_escape.sub('', log_text)

        # Match `(username @ folder) 🤌 CL Timing: [timestamp]`
        header_pattern = r"\((.*?) @ (.*?)\) 🤌 CL Timing: \[ (.*?) \]"
        header_match = re.search(header_pattern, clean)

        if not header_match:
            return None

        user, module, timestamp = header_match.groups()
        lines = clean.splitlines()
        level_line = ' '.join(lines[1:]).strip() if len(lines) > 1 else ''

        level_match = re.match(r'\[(\s\w+\s)\]\s?(.*)', level_line)
        level = level_match.group(1) if level_match else "UNKNOWN"
        message = level_match.group(2) if level_match else ''

        return {
            "user": user,
            "module": module,
            "level": level.strip(),
            "timestamp": timestamp,
            "message": ansi_escape.sub('', message)
        }

    
    def jsonifier(self) -> list:
        """
        Reads the log file and returns a list of JSON objects representing each log entry.
        Reserved for central web collection, intentionally not used in CLI.
        Returns:
            list: A list of JSON objects, each representing a log entry.
        """
        log_entries = []
        with open(self.log_file, 'r') as file:
            content = file.read()
            log_lines = content.split('\n\n')  # Split by double newlines to separate
            for line in log_lines:
                if line.strip():
                    log_entry = self.parse_log(line)
                    if log_entry:
                        log_entries.append(json.dumps(log_entry))

        return log_entries


logging.setLoggerClass(ContribLog)
