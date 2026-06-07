import os
import sys
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.main import app

client = TestClient(app)

print('GET /')
resp = client.get('/')
print(resp.status_code)
print(resp.json())

print('\nPOST /query with form')
resp = client.post('/query', data={'question': 'Who is the CEO of the company?'})
print(resp.status_code)
print(resp.json())

print('\nGET /query')
resp = client.get('/query', params={'question': 'Who is the CEO of the company?'})
print(resp.status_code)
print(resp.json())
