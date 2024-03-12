import logging
from subprocess import PIPE, run


class Executor:
    """
    Before running this code, make sure the oc client is in right cluster and namespace.
    """

    def __init__(self):
        pass


    @staticmethod
    def horizontal_scale(deployment_name, current_replicas, future_replicas):
        logging.info("Horizontal Scaling for " + deployment_name + f"current_replicas: {current_replicas}, future_replicas: {future_replicas}")
        oc_command = f"oc scale --current_replicas={current_replicas} --replicas={future_replicas} deployment/{deployment_name}"
        run(oc_command, shell=True)

    @staticmethod
    def vertical_scale(deployment_name, current_cup_quota_cores, future_cpu_quota_cores, current_memory_quota_mb, future_memory_quota_mb):
        logging.info("Horizontal Scaling for " + deployment_name + f"current_cpu_quota_cores: {current_cup_quota_cores}, future_cpu_quota_cores: {future_cpu_quota_cores}, current_memory_quota_mb: {current_memory_quota_mb}, future_memory_quota_mb:{future_memory_quota_mb}")
        oc_command = f"oc set resources deployment {deployment_name} --limits=cpu={future_cpu_quota_cores},memory={future_memory_quota_mb}Mi"
        # TODO: add consistency check
        run(oc_command, shell=True)

    @staticmethod
    def get_command_output(command):
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return result.stdout

    @staticmethod
    def get_replicas(deployment_name):
        selector_name = deployment_name[:-7] + "-deployment"
        get_pod_deployment_command = f"oc get pods --selector=name={selector_name} --no-headers -o custom-columns=\":metadata.name\""
        pod_names_in_deployment_str = Executor.get_command_output(get_pod_deployment_command)
        pod_names_in_deployment = pod_names_in_deployment_str.split("\n")[:-1]
        return len(pod_names_in_deployment)


    @staticmethod
    def scale_jvm_heap_size(deployment_name, current_jvm_heap_max_mb, future_jvm_heap_max_mb):
        selector_name = deployment_name[:-7] + "-deployment"
        get_pod_deployment_command = f"oc get pods --selector=name={selector_name} --no-headers -o custom-columns=\":metadata.name\""
        pod_names_in_deployment_str = Executor.get_command_output(get_pod_deployment_command)
        pod_names_in_deployment = pod_names_in_deployment_str.split("\n")[:-1]
        for pod_names in pod_names_in_deployment:
            pass
            # TODO: add build, image-building







    @staticmethod
    def execute(options):
        for index, row in options.iterrows():
            service_name = row['service_name']
            current_cpu_cores_quota = row['current_cpu_cores_quota']
            current_memory_quota_mb = row['current_memory_quota_mb']
            current_replica_num = row['current_replica_num']
            current_jvm_heap_max_mb = row['current_jvm_heap_max_mb']
            future_cpu_cores_quota = row['future_cpu_cores_quota']
            future_memory_quota_mb = row['future_memory_quota_mb']
            future_replica_num = row['future_replica_num']
            future_jvm_heap_max_mb = row['future_jvm_heap_max_mb']
            if future_replica_num != current_replica_num:
                Executor.horizontal_scale(service_name, current_replica_num, future_replica_num)





