import hvac
import base64

client = hvac.Client(url='http://172.17.0.2:8200',  token="dev-token")
print(client.is_authenticated())

read_response = client.secrets.kv.read_secret_version(path='poc')

print(read_response['data']['data']['pass'])
password = read_response['data']['data']['pass']
print(base64.b64encode(password.encode('ascii')))
