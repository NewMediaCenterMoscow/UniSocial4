import logging
from time import sleep

class Worker():
    """Helper for role worker"""

    def __init__(self):
        self.__base_sleep_interval = 5.0
        self.__max_sleep_interval = 600.0

        self.__sleep_interval = 0

    def work(self):
        logging.info('working...')

        return False

    def run(self):

        while True:
            res = self.work()

            if res:
                self.__sleep_interval = 0
            else:
                if self.__sleep_interval == 0:
                    self.__sleep_interval = self.__base_sleep_interval

                if self.__sleep_interval < self.__max_sleep_interval:
                    self.__sleep_interval += self.__sleep_interval

            logging.info("sleep - " + str(self.__sleep_interval))
            sleep(self.__sleep_interval)


