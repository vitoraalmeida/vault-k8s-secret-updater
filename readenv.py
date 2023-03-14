import os
import time

while(True):
    secret = os.getenv('SECRET')
    env1 = os.getenv('ENV1')
    env2 = os.getenv('ENV2')
    time.sleep(2)
    print(secret)
    print(env1)
    print(env2)

