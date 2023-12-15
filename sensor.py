import random
import time

class sensor():
    def __init__(self, seed=None):
    
        if seed is None:
            random.seed(time.time())
        else:
            random.seed(seed)
            
    def read(self):
        now = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())
        temp = random.gauss(65.0, 10.0)
        humidity = random.gauss(50, 10.0)
        return (now, temp, humidity)
