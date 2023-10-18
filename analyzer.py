class Analyzer:
    def __init__(self, knowledge_base, plan_pool, services_analyzed):
        self.knowledge_base = knowledge_base
        self.plan_pool = plan_pool
        self.services_analyzed = services_analyzed
        self.weights = []
        self.utility_score = {}


    def analyze(self):
        knowledge = self.knowledge_base.get_current_knowledge()
        for service_name in self.services_analyzed[:1]:
            service_knowledge = knowledge[knowledge['service_name'] == service_name]
            print(service_knowledge.to_string())
            options = self.increase_cpu_only()

    def get_cost_utility_preference(self, cpu_cores_used, memory_bytes_used):
        pass

    def get_error_rate_utility_preference(self, success_rate):
        pass

    def get_utility(self, cpu_quota, memeory_quota, success_rate_expected, latency_expected):
    def increase_cpu_quota_only(self):
        '''

        :return:
        '''
        return self.grid_search(current_cpu_cores_used, step_cpu_cores, 0, 0, 0, 0)

    def decrease_cpu_quota_only(self):
        pass

    def increase_memory_quota_only(self):
        pass

    def decrease_memory_quota_only(self):
        pass

    def add_replica(self):
        pass

    def remove_replicas(self):
        pass

    # prediction and grid search
    def predict_for_option(self):
        # get the success_rate_expected, latency_expected somehow
        # call utility function
        self.get_utility(cpu_quota, memeory_quota, success_rate_expected, latency_expected)

    def analyze_options(self,
                    current_cpu_cores_quota,
                    step_cpu_cores,
                    current_memory_bytes_quota,
                    step_memory_bytes,
                    current_pod_nums,
                    step_pod_nums,
                    current_jvm_heap_bytes_quota,
                    step_jvm_heap_bytes
                    ):
        '''
        :param current_cpu_cores_quota:
        :param step_cpu_cores:
        :param current_memory_bytes_used:
        :param step_memory_bytes:
        :param current_pod_nums:
        :param step_pod_nums:
        :param current_jvm_heap_bytes_used:
        :param step_jvm_heap_bytes_used:
        :return: A set of options with utility
        '''
        # picking new set of options: cpu, memory, and pods
        if step_cpu_cores > 0:       
            current_cpu_cores_quota += 0.25*step_cpu_cores
        elif step_cpu_cores < 0:    
            current_cpu_cores_quota -= 0.25*step_cpu_cores
        if step_memory_bytes == 1:    
            current_memory_bytes_quota *= 2
        elif step_memory_bytes == -1: 
            current_memory_bytes_quota /= 2
        if step_pod_nums == 1:        
            current_pod_nums += 1
        elif step_pod_nums == -1:
            current_pod_nums -= 1
        if step_jvm_heap_bytes == 1:
            current_jvm_heap_bytes_quota *= 2
        elif step_jvm_heap_bytes == -1:
            current_jvm_heap_bytes_quota /= 2

        # dealing with memory quota conflict
        if current_jvm_heap_bytes_quota > current_memory_bytes_quota:
            # whoever is not updating will follow the updates
            if step_memory_bytes == 0:
                current_memory_bytes_quota = current_jvm_heap_bytes_quota
            elif step_jvm_heap_bytes == 0:
                current_jvm_heap_bytes_quota = current_memory_bytes_quota
            # else we allocate more resources
            else:
                current_memory_bytes_quota = current_jvm_heap_bytes_quota

        # return the results if it is cached
        current_status = "cpu-{}_mem-{}_pod-{}".format(
                                   current_cpu_cores_quota, 
                                   current_memory_bytes_quota, 
                                   current_pod_nums)
        if current_status in self.utility_score.keys():
            return self.utility_score[current_status]
        else:
            # call the predict_for_option
            pass

