import requests
import json


def update_user_location(user_id, building, level, x, y, direction):
    user = {
        'user_id': user_id,
        'building': building,
        'level': level,
        'x': x,
        'y': y,
        'direction': direction
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post("http://localhost:3000/users/", data=json.dumps(user), headers=headers)
    return r


if __name__ == '__main__':
    print update_user_location('T10', '1', '2', 150, 40, 190)
