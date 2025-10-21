# copilot_debug.py
import os
import logging

def is_debug_enabled():
    return os.environ.get("COPILOT_DEBUG", "0") in ("1", "true", "True")

def enable_debug():
    os.environ["COPILOT_DEBUG"] = "1"
    os.environ["COPILOT_LOG_LEVEL"] = "DEBUG"
    logging.getLogger().setLevel(logging.DEBUG)

def parse_args_with_debug(argv):
    debug = any(flag in argv for flag in ["--debug", "--verbose"])
    clean_args = [arg for arg in argv if arg not in ["--debug", "--verbose"]]
    if debug:
        enable_debug()
    else:
        os.environ["COPILOT_LOG_LEVEL"] = "WARNING"
    return debug, clean_args

