from requests import get, post

def send_move_can():
	response = get("http://192.168.1.145:6890/move?speed=3&time=2.8&braketime=500",)
	print(response.text)

def send_stop_can():
	response = get("http://192.168.1.145:6890/stop",)
	print(response.text)

if __name__ == "__main__":
	send_move_can()
