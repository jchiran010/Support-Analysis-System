import requests

s = requests.Session()
res = s.post('http://127.0.0.1:5000/login', data={'username': 'admin', 'password': 'admin'})
if res.status_code != 200:
    print('Failed to login:', res.status_code)

for route in ['/dashboard', '/complaints', '/analytics', '/reports', '/users', '/notifications', '/settings']:
    r = s.get('http://127.0.0.1:5000' + route)
    print(route, r.status_code)
