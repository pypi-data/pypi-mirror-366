import re
from kubernetes import client

from walker.config import Config
from .kube_context import KubeContext

# utility collection; methods are all static
class CustomResources:
    def get_app_ids():
        app_ids_by_ss: dict[str, str] = {}

        group = Config().get('app.cr.group', 'ops.c3.ai')
        v = Config().get('app.cr.v', 'v2')
        plural = Config().get('app.cr.plural', 'c3cassandras')
        label = Config().get('app.label', 'c3__app_id-0')
        strip = Config().get('app.strip', '0')

        v1 = client.CustomObjectsApi()
        try:
            c3cassandras = v1.list_cluster_custom_object(group=group, version=v, plural=plural)
            for c in c3cassandras.items():
                if c[0] == 'items':
                    for item in c[1]:
                        app_ids_by_ss[f"{item['metadata']['name']}@{item['metadata']['namespace']}"] = item['metadata']['labels'][label].strip(strip)
        except Exception:
            pass

        return app_ids_by_ss

    def get_cr_name(cluster: str, namespace: str = None):
        nn = cluster.split('@')
        # cs-9834d85c68-cs-9834d85c68-default-sts
        if not namespace and len(nn) > 1:
            namespace = nn[1]
        if not namespace:
            namespace = KubeContext.in_cluster_namespace()
        groups = re.match(Config().get('app.cr.cluster-regex', r"(.*?-.*?)-.*"), nn[0])

        return f"{groups[1]}@{namespace}"

    def get_metrics(namespace: str, pod_name: str, container_name: str = None) -> dict[str, any]:
        # 'containers': [
        #     {
        #     'name': 'cassandra',
        #     'usage': {
        #         'cpu': '31325875n',
        #         'memory': '17095800Ki'
        #     }
        #     },
        #     {
        #     'name': 'medusa',
        #     'usage': {
        #         'cpu': '17947213n',
        #         'memory': '236456Ki'
        #     }
        #     },
        #     {
        #     'name': 'server-system-logger',
        #     'usage': {
        #         'cpu': '49282n',
        #         'memory': '1608Ki'
        #     }
        #     }
        # ]
        for pod in CustomResources.list_metrics_crs(namespace)['items']:
            p_name = pod["metadata"]["name"]
            if p_name == pod_name:
                if not container_name:
                    return pod

                for container in pod["containers"]:
                    if container["name"] == container_name:
                        return container

        return None

    def list_metrics_crs(namespace: str, plural = "pods") -> dict[str, any]:
        group = "metrics.k8s.io"
        version = "v1beta1"

        api = client.CustomObjectsApi()

        return api.list_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural)