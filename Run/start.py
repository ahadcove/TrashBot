import time
from api import send_move_can, send_stop_can
from garage import open_garage

def found_garbage():
	open_garage()
	time.sleep(10)
	send_move_can
		
