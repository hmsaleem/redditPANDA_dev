"forks child processes until you type 'q'"
import time
import os
from datetime import datetime

class scheduler:
    def __init__(self, h=0, m=0, s=0):
        self.h = h
        self.m = m
        self.s = s
        print "Parent Process", os.getpid()

    def runit(self, fn, *args):
        time_step = self.h*3600 + self.m*60 + self.s
        while True:
            starttime = time.time()
            newpid = os.fork()
            if newpid == 0:
                fn(*args)
            exec_time = time.time()-starttime
            tlambda = int(exec_time)/time_step
            ttime = (tlambda+1)*time_step
            time.sleep(ttime - ((time.time()-starttime)%ttime))


if __name__ == "__main__":
    def child():
        print 'Hello from child', os.getpid()
        print str(datetime.now())
        time.sleep(10)
        os._exit(0) # else goes back to parent loop

    ss = scheduler(s=5)
    ss.runit(child)
