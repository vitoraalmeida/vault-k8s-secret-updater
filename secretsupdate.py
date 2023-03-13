from kubernetes import client, config
import time
import hvac
import base64



def restart_pod():
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    time.sleep(10)
    for i in ret.items:
        if "python-readenv" in i.metadata.name:
            print("deleting pod %s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            v1.delete_namespaced_pod(name=i.metadata.name, namespace="vault", body=client.V1DeleteOptions())


def get_password():
    client = hvac.Client(url='http://10.244.1.85:8200',  token="root")
    print("conectou com o vault")
    print(client.is_authenticated())
    read_response = client.secrets.kv.read_secret_version(path='poc')
    return read_response

def update_secret(password):
    time.sleep(10)
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    sec = client.V1Secret()
    print("deleting secret...")
    api_instance.delete_namespaced_secret(name="python-readenv", namespace="vault", body=sec)
    print("creating secret...")
    print(f"SENHA {password}")
    sec.metadata = client.V1ObjectMeta(name="python-readenv")
    sec.type = "Opaque"
    sec.data = {"secret": password }
    api_instance.create_namespaced_secret(namespace="vault", body=sec)
    restart_pod()

def main():
    print("buscando password no vault")
    password = get_password()
    print(password['data']['data']['pass'])
    password = password['data']['data']['pass']
    password = base64.b64encode(password.encode('ascii'))
    print(password)
    print(password.decode('UTF-8'))
    update_secret(password.decode('UTF-8'))

if __name__ == '__main__':
    main()
