class Analyzer:
    def __init__(self, knowledge_base, plan_pool, services_analyzed, cost_weight, success_rate_weight, latency_weight):
        self.knowledge_base = knowledge_base
        self.plan_pool = plan_pool
        self.services_analyzed = services_analyzed
        self.cost_weight = cost_weight
        self.success_rate_weight = success_rate_weight
        self.latency_weight = latency_weight

    def analyze(self):
        knowledge = self.knowledge_base.get_current_knowledge()
        for service_name in self.services_analyzed[:1]:
            service_knowledge = knowledge[knowledge['service_name'] == service_name]
            if not Analyzer.is_adaption_required(service_knowledge):
                continue
            pods_number = service_knowledge.at[0, 'pods_number']
            min_cpu_quota_percentage_across_pods = service_knowledge.at[0, 'min_cpu_quota_percentage_across_pods']
            max_cpu_quota_percentage_across_pods = service_knowledge.at[0, 'max_cpu_quota_percentage_across_pods']
            min_cpu_cores_used_across_pods = service_knowledge.at[0, 'min_cpu_cores_used_across_pods']
            max_cpu_cores_used_across_pods = service_knowledge.at[0, 'max_cpu_cores_used_across_pods ']
            min_memory_quota_percentage_across_pods = service_knowledge.at[0, 'min_memory_quota_percentage_across_pods']
            max_memory_quota_percentage_across_pods = service_knowledge.at[
                0, 'max_memory_quota_percentage_across_pods ']
            min_memory_used_bytes_across_pods = service_knowledge.at[0, 'min_memory_used_bytes_across_pods']
            max_memory_used_bytes_across_pods = service_knowledge.at[0, 'max_memory_used_bytes_across_pods']
            min_jvm_heap_used_percentage_across_pods = service_knowledge.at[
                0, 'min_jvm_heap_used_percentage_across_pods']
            min_jvm_heap_used_bytes = service_knowledge.at[0, 'min_jvm_heap_used_bytes']
            cpu_quota = Analyzer.get_cpu_quota(min_cpu_quota_percentage_across_pods, min_cpu_cores_used_across_pods)
            memory_quota = Analyzer.get_memory_quota(min_memory_quota_percentage_across_pods,
                                                     min_memory_used_bytes_across_pods)
            jvm_quota = Analyzer.get_memory_quota(min_jvm_heap_used_percentage_across_pods, min_jvm_heap_used_bytes)
            cpu_quota_steps = Analyzer.round_to_nearest_quarter(0.5 * cpu_quota)
            success_rate = service_knowledge.at[0, 'success_rate']
            latency = service_knowledge.at[0, 'latency']

            if min_cpu_cores_used_across_pods >= 90 and max_memory_used_bytes_across_pods <= 40:
                options = self.analyze_options(
                    cpu_quota,
                    cpu_quota_steps,
                    memory_quota,
                    -1,
                    pods_number,
                    0,
                    jvm_quota,
                    0,
                    success_rate,
                    latency
                )
            elif max_cpu_quota_percentage_across_pods < 40 and min_memory_quota_percentage_across_pods >= 80:
                options = self.analyze_options(
                    cpu_quota,
                    - cpu_quota_steps,
                    memory_quota,
                    1,
                    pods_number,
                    0,
                    jvm_quota,
                    0,
                    success_rate,
                    latency
                )
            elif min_cpu_quota_percentage_across_pods >= 90 and min_memory_quota_percentage_across_pods > 80:
                options = self.analyze_options(
                    cpu_quota,
                    0,
                    memory_quota,
                    0,
                    pods_number,
                    1,
                    jvm_quota,
                    0,
                    success_rate,
                    latency
                )
            elif max_cpu_quota_percentage_across_pods <= 40 and max_memory_quota_percentage_across_pods <= 40:
                options = self.analyze_options(
                    cpu_quota,
                    0,
                    memory_quota,
                    0,
                    pods_number,
                    -1,
                    jvm_quota,
                    0,
                    success_rate,
                    latency
                )
            elif min_jvm_heap_used_percentage_across_pods >= 80:
                options = self.analyze_options(
                    cpu_quota,
                    0,
                    memory_quota,
                    0,
                    pods_number,
                    0,
                    jvm_quota,
                    1,
                    success_rate,
                    latency
                )


    @staticmethod
    def get_cpu_quota(cpu_quota_percentage, cpu_cores_used):
        return 1

    @staticmethod
    def round_to_nearest_quarter(num_to_be_rounded):
        return 1

    @staticmethod
    def round_to_nearest_twos_power(num_to_be_rouned):
        return 1

    @staticmethod
    def get_memory_quota(self, memory_quota_percentage, memory_bytes_used):
        return 1

    @staticmethod
    def is_adaption_required(service_knowledge):
        if service_knowledge.isnull().values.any():
            return False
        return True

    @staticmethod
    def get_cost_utility_preference(cpu_cores_used, memory_bytes_used):
        memory_Gb_used = Analyzer.convert_bytes_to_Gb(memory_bytes_used)
        cost_per_month = cpu_cores_used * 12 + memory_Gb_used * 5 # from IBM Cloud
        if cost_per_month <= 10:
            return 1.0
        elif cost_per_month <= 20:
            return 0.9
        elif cost_per_month <= 30:
            return 0.7
        elif cost_per_month <= 80:
            return 0.1
        else:
            return 0

    @staticmethod
    def convert_bytes_to_Gb(memory_bytes):
        return 1

    @staticmethod
    def get_success_rate_utility_preference(success_rate):
        if success_rate > 99.9:
            return 1
        elif success_rate > 99.5:
            return 0.8
        elif success_rate > 99:
            return 0.5
        else:
            return 0

    @staticmethod
    def get_latency_utility_preference(latency):
        latency = Analyzer.convert_nano_seconds_to_milli_seconds(latency)
        if latency < 100:
            return 1
        elif latency < 200:
            return 0.8
        elif latency < 300:
            return 0.6
        else:
            return 0

    @staticmethod
    def convert_nano_seconds_to_milli_seconds(nano_seconds):
        return 1

    def get_utility(self, cpu_quota, memory_quota, success_rate_expected, latency_expected, pod_num):
        utility = 0
        utility += self.cost_weight * self.get_cost_utility_preference(cpu_quota * pod_num, memory_quota * pod_num)
        utility += self.success_rate_weight * self.get_success_rate_utility_preference(success_rate_expected)
        utility += self.latency_weight * self.get_latency_utility_preference(latency_expected)
        return utility

    # prediction and grid search
    def predict_for_option(self):
        pass
        # call utility function
        # self.get_utility(cpu_quota, memory_quota, success_rate_expected, latency_expected, pod_num)

    def analyze_options(self,
                        current_cpu_cores_quota,
                        step_cpu_cores,
                        current_memory_bytes_quota,
                        step_memory_bytes,
                        current_pod_nums,
                        step_pod_nums,
                        current_jvm_heap_bytes_quota,
                        step_jvm_heap_bytes,
                        current_success_rate,
                        current_latency,
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
        # call the predict_for_option
        return []
