from requests import get, post

# Make sure you fill in your token here
hass_token = ''

headers = {
    "Authorization": f"Bearer {hass_token}",
    "content-type": "application/json",
}

def open_garage():
	response = post("http://192.168.1.15:8123/api/services/cover/toggle", json={"entity_id": "cover.garage_door"}, headers=headers,)
	print(response.text)

if __name__ == "__main__":
    open_garage()