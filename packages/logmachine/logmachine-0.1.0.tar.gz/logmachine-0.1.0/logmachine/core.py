import os, sys
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
        'DEBUG': BOLD + '[DEBUG]' + RESET,
        'INFO': BOLD + '[INFO]' + RESET,
        'WARNING': BOLD + '[WARNING]' + RESET,
        'ERROR': BOLD + '[ERROR]' + RESET,
        'SUCCESS': BOLD + '[SUCCESS]' + RESET
    }

    def format(self, record):
        try:
            username = os.getlogin()
        except Exception:
            username = os.environ.get('USER', 'unknown')

        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        level_fmt = self.LEVEL_FORMATS.get(levelname, f'[{levelname}]')
        record.levelname = f"{color}{level_fmt}{self.RESET}"
        record.asctime = self.formatTime(record, self.datefmt)
        module_file = record.pathname
        parent_dir = os.path.basename(os.path.dirname(module_file)) or 'unknown'

        return f"""{self.COLORS.get('DEBUG')}({username}{self.RESET} @ {self.COLORS.get('WARNING') + parent_dir + self.RESET}) 🤌 CL Timing: {color}[ {record.asctime} ]{self.RESET}
{record.levelname} {record.getMessage()}
"""

class ContribLog(logging.Logger):
    SUCCESS = 25

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.addLevelName(self.SUCCESS, "SUCCESS")
        self.log_file = kwargs.get('log_file', 'logs.log')
        self.error_file = kwargs.get('error_file', 'errors.log')
        self.verbose = kwargs.get('verbose', False)
        self.debug_level = kwargs.get('debug_level', 0)
        self.name = kwargs.get('name', 'CL Logger')

    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.SUCCESS):
            self._log(self.SUCCESS, msg, args, **kwargs)

    def get_logger(self):
        # logger = logging.getLogger(self.name)
        self.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.handlers = []

        # File handlers
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        eh = logging.FileHandler(self.error_file)
        eh.setLevel(logging.ERROR)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.verbose else logging.CRITICAL + 1)

        formatter = CustomFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
        fh.setFormatter(formatter)
        eh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.addHandler(fh)
        self.addHandler(eh)
        self.addHandler(ch)

        # Filter console output based on debug_level
        class DebugLevelFilter(logging.Filter):
            def filter(self, record):
                level_map = {
                    0: ['ERROR', 'SUCCESS', 'WARNING', 'INFO', 'DEBUG'],
                    1: ['ERROR'],
                    2: ['SUCCESS'],
                    3: ['WARNING'],
                    4: ['INFO'],
                    5: ['ERROR', 'WARNING'],
                    6: ['INFO', 'SUCCESS'],
                    7: ['ERROR', 'WARNING', 'INFO']
                }
                allowed = level_map.get(int(self.debug_level), [])
                return record.levelname in allowed

        ch.addFilter(DebugLevelFilter())

        return self
    
    def parse_log(self, log_text):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        clean = ansi_escape.sub('', log_text)

        # Match `(username @ folder) 🤌 CL Timing: [timestamp]`
        header_pattern = r"\((.*?) @ (.*?)\) 🤌 CL Timing: \[ (.*?) \]"
        header_match = re.search(header_pattern, clean)

        if not header_match:
            return None

        user, module, timestamp = header_match.groups()
        lines = clean.splitlines()
        level_line = lines[1] if len(lines) > 1 else ''
        message = ' '.join(lines[2:]).strip()

        # Extract level from second line: e.g., "[INFO] Message"
        level_match = re.match(r'\[(\w+)\]', level_line)
        level = level_match.group(1) if level_match else "UNKNOWN"

        return {
            "user": user,
            "module": module,
            "level": level,
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

# Best initialization example to keep the custom methods available
logger = ContribLog({ "verbose": '--verbose' in sys.argv, "debug_level": os.getenv('DEBUG_LEVEL', 0) }).get_logger()
