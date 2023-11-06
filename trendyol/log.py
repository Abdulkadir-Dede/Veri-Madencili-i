
import datetime
import os

class Log():
    def __init__(self) -> None:
        self.filename =f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        # if not os.path.exists("logs"):
        #     os.mkdir("logs")
        # with open(os.path.join("logs", self.filename), "w", encoding="utf-8") as f:
        #     pass
    
    def Write(self, State, desc):
        with open(os.path.join("logs", self.filename),"a", encoding="utf-8") as f:
            f.write(f'{datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")} | {State} | {desc}\n')
