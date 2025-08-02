import time

class TimerService:
    def start_timer(self):
        self.__start_time = time.time()
    
    def get_elapsed_time_in_sec(self):
        return time.time() - self.__start_time
