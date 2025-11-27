import requests, json
r = requests.post('http://127.0.0.1:5000/ask', json={'message': 'Explain merge vs rebase in 3 steps, briefly.'})
print('status', r.status_code)
try:
    j = r.json()
    print(json.dumps(j, indent=2))
except Exception as e:
    print('raw:', r.text)
