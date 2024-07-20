import os

import ua_appointment_checker.constants as cons


class Environment:
    """There's information that needs to be passed
    to the application as a form of environment variables.

    This class encapsulates all the information needed
    for the application as attributes.

    Each attribute is computed from os.environ and
    a default is used if applicable. 
    """
    @property
    def remote_chrome_hostname(self) -> str:
        return os.environ.get("REMOTE_CHROME_HOST", cons.DEFAULT_REMOTE_CHROME_HOST)

    @property
    def remote_chrome_port(self) -> int:
        port = os.environ.get("REMOTE_CHROME_PORT",
                              cons.DEFAULT_REMOTE_CHROME_PORT)
        return int(port)

    @property
    def bot_token(self) -> str:
        return os.environ.get("TELEGRAM_BOT_TOKEN", "")


app_environment = Environment()
