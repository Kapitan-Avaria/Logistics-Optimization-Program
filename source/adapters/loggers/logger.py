from source.domain.logger_interface import LoggerInterface


class Logger(LoggerInterface):

    def __init__(self, log_file=None):
        self.log_file = log_file

    def print(self, message):
        # with open(self.log_file, 'a') as f:
        #     f.write(message + '\n')
        # print(message)
        return
