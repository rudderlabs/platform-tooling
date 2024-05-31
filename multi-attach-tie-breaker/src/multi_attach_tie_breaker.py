from kubernetes import client, config, watch
import os

# if the ENV_MATCHING_WORKLOADS is not defined we are going to match all workloads
ENV_MATCHING_WORKLOADS = "MATCHING_WORKLOADS"


class WorkloadMatcher:
    def __init__(self, workload_regexes=None):
        self.workload_regexes = workload_regexes or []

    def match(self, pod_name):
        # in the case there are no regexes we assume that all workloads are matched
        if not self.workload_regexes:
            return True
        for regex in self.workload_regexes:
            if regex in pod_name:
                return True
        return False


def watch_k8s_events(workload_matcher=None):
    workload_matcher = workload_matcher or WorkloadMatcher()
    # Load Kubernetes configuration from default location
    # config.load_kube_config()
    config.load_incluster_config()

    # Create a Kubernetes API client
    api_client = client.CoreV1Api()

    w = watch.Watch()
    for event in w.stream(api_client.list_event_for_all_namespaces):
        event_type = event["type"]
        event_object = event["object"]
        if event_type == "Warning" and "multi-attach error" in event_object.message:
            # Multi-attach error detected, delete volume attachment
            print(event_object.message)
            volume_name = event_object.involved_object.name
            namespace = event_object.involved_object.namespace
            pod_name = event_object.involved_object.field_selector.split("=")[1]

            delete_volume_matching_volume_attachment(
                api_client, volume_name, pod_name, namespace, workload_matcher
            )


def delete_volume_attachment(api_client, volume_name, pod_name, namespace):
    # Delete the volume attachment associated with the pod
    try:
        api_client.delete_namespaced_persistent_volume_claim(
            name=volume_name, namespace=namespace
        )
        print(f"Deleted volume attachment for pod {pod_name} and volume {volume_name}")
    except client.rest.ApiException as e:
        print(f"Error deleting volume attachment: {e}")


def delete_volume_matching_volume_attachment(
    api_client, volume_name, pod_name, namespace, workload_matcher=None
):
    workload_matcher = workload_matcher or WorkloadMatcher()
    return (
        delete_volume_attachment(api_client, volume_name, pod_name, namespace)
        if workload_matcher.match(pod_name)
        else None
    )


if __name__ == "__main__":
    # let's load the workload_regexes from the envronment variable MATCHING_WORKLOADS
    import os

    matching_workloads = os.getenv(ENV_MATCHING_WORKLOADS, "").split(",")
    # let's trim any spaces and get rid of empty strings
    matching_workloads = [
        workload.strip() for workload in matching_workloads if workload
    ]
    workload_matcher = WorkloadMatcher(workload_regexes=matching_workloads)
    watch_k8s_events(workload_matcher)
