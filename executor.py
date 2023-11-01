import logging
import os


class Executor:
    """
    Before running this code, make sure the oc client is in right cluster and namespace.
    """

    def __init__(self):
        pass

    @staticmethod
    def run_oc_command(oc_command):
        os.system(oc_command)

    @staticmethod
    def horizontal_scale(deployment_name, current_replicas, future_replicas):
        logging.info("Vertical Scaling for " + deployment_name + f"current_replicas: {current_replicas}, future_replicas: {future_replicas}")
        oc_command = f"oc scale --current_replicas={current_replicas} --replicas={future_replicas} deployment/{deployment_name}"
        Executor.run_oc_command(oc_command)

    @staticmethod
    def vertical_scale(deployment_name, current_cup_quota_cores, future_cpu_quota_cores, current_memory_quota_mb, future_memory_quota_mb):
        logging.info("Horizontal Scaling for " + deployment_name + f"current_cpu_quota_cores: {current_cup_quota_cores}, future_cpu_quota_cores: {future_cpu_quota_cores}, current_memory_quota_mb: {current_memory_quota_mb}, future_memory_quota_mb:{future_memory_quota_mb}")
        oc_command = f"oc set resources deployment {deployment_name} --limits=cpu={future_cpu_quota_cores},memory={future_memory_quota_mb}Mi"
        # TODO: add consistency check
        Executor.run_oc_command(oc_command)

    @staticmethod
    def scale_jvm_heap_size(deployment_name, current_jvm_heap_max_mb, future_jvm_heap_max_mb):
        pass

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
            elif current_cpu_cores_quota != future_cpu_cores_quota or current_memory_quota_mb != future_memory_quota_mb:
                Executor.vertical_scale(service_name, current_cpu_cores_quota, future_cpu_cores_quota, current_memory_quota_mb, future_memory_quota_mb)






