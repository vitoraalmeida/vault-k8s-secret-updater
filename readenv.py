import os
import time

while(True):
    secret = os.getenv('SECRET')
    time.sleep(2)
    print(secret)

