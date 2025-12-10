import requests

url = "http://127.0.0.1:8000/api/employees/a123"

print("Testing request to:", url)

try:
    response = requests.get(url, timeout=5)
    print("STATUS:", response.status_code)
    print("BODY:", response.text)

except Exception as e:
    print("ERROR:", e)