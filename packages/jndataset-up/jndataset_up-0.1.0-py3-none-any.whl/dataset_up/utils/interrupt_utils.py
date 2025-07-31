import os
import signal
from dataset_up.utils.concurrent_utils import interrupt_event

def register_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
def signal_handler(sig, frame):
    print("\n接收到中断信号,强制退出！\n")
    interrupt_event.set()
    os._exit(0)
    
