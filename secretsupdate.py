from kubernetes import client, config
import time
import hvac
import base64
import os

def restart_pod(app_name, namespace):
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    print(ret.items)
    time.sleep(10)
    for i in ret.items:
        if app_name in i.metadata.name:
            print("deleting pod %s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            v1.delete_namespaced_pod(name=i.metadata.name, namespace=namespace, body=client.V1DeleteOptions())


def get_password(vault_addr, vault_secret_path, vault_token):
    client = hvac.Client(url=f'{vault_addr}:8200',  token=vault_token)

#    Habilitar approle

#    client = hvac.Client()
#
#    client.sys.enable_auth_method(
#        method_type='approle',
#    )
#
#    # Mount approle auth method under a different path:
#    client.sys.enable_auth_method(
#        method_type='approle',
#        path='my-approle',
#    )

#    Authenticação hvac.api.auth_methods.AppRole.login()

#    client = hvac.Client()
#
#    client.auth.approle.login(
#        role_id='<some_role_id>',
#        secret_id='<some_secret_id>',
#    )


    print("vault connected")
    print(client.is_authenticated())
    print("getting pass in vault")
    read_response = client.secrets.kv.read_secret_version(path=vault_secret_path)
    return read_response


def update_secret(password, namespace, app_name):
    time.sleep(10)
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    sec = client.V1Secret()
    print("reading secret")
    secret = api_instance.read_namespaced_secret(name=app_name, namespace=namespace)
    print(secret.data)
    print(f"updating secret instace with new password {password}")
    secret.data['secret'] = password
    print(secret.data)
    print("deleting old secret...")
    api_instance.delete_namespaced_secret(name=app_name, namespace=namespace, body=sec)
    print("recreating secret...")
    sec.metadata = client.V1ObjectMeta(name=app_name)
    sec.type = "Opaque"
    sec.data = secret.data
    api_instance.create_namespaced_secret(namespace=namespace, body=sec)
    restart_pod()

def main():
    vault_addr = os.getenv('VAULT_ADDR').strip()
    vault_token = os.getenv('VAULT_TOKEN').strip()
    vault_secret_path = os.getenv('VAULT_SECRET_PATH').strip()
    vault_secret_key = os.getenv('VAULT_SECRET_KEY').strip()
    app_name = os.getenv('APP_NAME').strip()
    namespace = os.getenv('NAMESPACE').strip()
    print(vault_addr)
    print(vault_token)
    print(vault_secret_path)
    print(app_name)
    print(namespace)

    password = get_password(vault_addr, vault_secret_path, vault_token)
    print(password)
    print(password['data']['data'][vault_secret_key])
    password = password['data']['data'][vault_secret_key]
    password = base64.b64encode(password.encode('ascii'))
    print(password)
    print(password.decode('UTF-8'))
    update_secret(password.decode('UTF-8'), namespace, app_name)

if __name__ == '__main__':
    main()
