import threading


class Test:
    def __init__(self):
        self.a = "a"
        self.T = threading.Thread(target=self.my_method, args=["zzz"])
        
    def my_method(self, x):
        print("Hole: {}".format(x))
        
    def start(self):
        self.T.start()
        

T = Test()
T.start()

