import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import builtins

class SlackLogger:
    _logging_in_progress = False  # Flag to prevent recursion

    def __init__(self, token, channel):
        self.token = token
        self.channel = channel
        self.client = WebClient(token=self.token)

    def send_message(self, text):
        """Sends a message to the specified Slack channel."""
        if SlackLogger._logging_in_progress:
            return  # Avoid recursion if we're already logging
        try:
            SlackLogger._logging_in_progress = True
            response = self.client.chat_postMessage(channel=self.channel, text=text)
            if not response.get("ok"):
                print(f"Failed to send message: {response}")
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
        finally:
            SlackLogger._logging_in_progress = False

    class SlackLoggerHandler(logging.Handler):
        def __init__(self, slack_logger):
            super().__init__()
            self.slack_logger = slack_logger

        def emit(self, record):
            log_entry = self.format(record)
            self.slack_logger.send_message(log_entry)

    @staticmethod
    def redirect_print_to_logger(logger):
        """Redirects print statements to the specified logger."""
        original_print = builtins.print  # Keep a reference to the original print

        def print_to_logger(*args, **kwargs):
            message = " ".join(str(arg) for arg in args)
            if not SlackLogger._logging_in_progress:  # Prevent recursion
                logger.info(message)
            else:
                original_print(*args, **kwargs)  # Fallback to original print

        builtins.print = print_to_logger

    @classmethod
    def create_logger(cls, slack_token, slack_channel='C07DYFK5SE8', redirect_print=True):
        """Creates a logger that sends log messages to a Slack channel."""
        # Initialize SlackLogger and SlackLoggerHandler
        slack_logger = cls(slack_token, slack_channel)
        slack_handler = cls.SlackLoggerHandler(slack_logger)

        # Create a logger and attach the custom Slack handler
        logger = logging.getLogger('SlackLogger')
        logger.setLevel(logging.INFO)  # Set the logging level
        logger.addHandler(slack_handler)

        # Set a basic format for the log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        slack_handler.setFormatter(formatter)

        # Automatically redirect print statements if specified
        if redirect_print:
            cls.redirect_print_to_logger(logger)

        return logger
