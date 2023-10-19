class Analyzer:
    def __init__(self, knowledge_base, plan_pool, services_analyzed, cost_weight, success_rate_weight, latency_weight):
        self.knowledge_base = knowledge_base
        self.plan_pool = plan_pool
        self.services_analyzed = services_analyzed
        self.memory_quota_lower_bound = 512
        self.jvm_heap_quota_lower_bound = 512
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

            if min_cpu_quota_percentage_across_pods >= 90 and max_memory_quota_percentage_across_pods <= 40:
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
        return Analyzer.round_to_nearest_quarter(cpu_cores_used / (cpu_quota_percentage / 100))

    @staticmethod
    def round_to_nearest_quarter(num_to_be_rounded):
        return 1

    @staticmethod
    def round_to_nearest_twos_power(num_to_be_rounded):
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
        memory_gb_used = Analyzer.convert_bytes_to_Gb(memory_bytes_used)
        cost_per_month = cpu_cores_used * 12 + memory_gb_used * 5  # from IBM Cloud
        if cost_per_month <= 10:
            return 1.0
        elif cost_per_month <= 20:
            return 0.9
        elif cost_per_month <= 30:
            return 0.7
        elif cost_per_month <= 80:
            return 0.3
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
            return 0.4
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

    def get_success_rate_expected(self, cpu_quota, memory_quota):
        threshold_1 = 0.99
        threshold_2 = 1.0
        cpu_lower_bound = 0.25
        cpu_upper_bound = 3
        mem_lower_bound = 512
        mem_upper_bound = 4096

        def empirical_func_cpu(quota):
            return threshold_1 + ((threshold_2 - threshold_1) / (cpu_upper_bound - cpu_lower_bound)) * (
                    quota - cpu_lower_bound)

        def empirical_func_memory(quota):
            return threshold_1 + ((threshold_2 - threshold_1) / (mem_upper_bound - mem_lower_bound)) * (
                    quota - mem_lower_bound)

        if cpu_quota < cpu_lower_bound or memory_quota < mem_lower_bound:
            return threshold_1
        elif cpu_quota > cpu_upper_bound and memory_quota > mem_upper_bound:
            return threshold_2
        else:
            return (empirical_func_cpu(cpu_quota) + empirical_func_memory(memory_quota)) / 2

    def get_latency_expected(self, cpu_quota, memory_quota):
        threshold_1 = 300
        threshold_2 = 100
        cpu_lower_bound = 0.25
        cpu_upper_bound = 3
        mem_lower_bound = 512
        mem_upper_bound = 4096

        def empirical_func_cpu(quota):
            return threshold_2 - ((threshold_1 - threshold_2) / (cpu_upper_bound - cpu_lower_bound)) * (
                    quota - cpu_lower_bound)

        def empirical_func_memory(quota):
            return threshold_2 - ((threshold_1 - threshold_2) / (mem_upper_bound - mem_lower_bound)) * (
                    quota - mem_lower_bound)

        if cpu_quota < cpu_lower_bound or memory_quota < mem_lower_bound:
            return threshold_1
        elif cpu_quota > cpu_upper_bound and memory_quota > mem_upper_bound:
            return threshold_2
        else:
            return (empirical_func_cpu(cpu_quota) + empirical_func_memory(memory_quota)) / 2

    # prediction
    def predict_for_option(self, cpu_quota, memory_quota, pod_num):
        # get the success_rate_expected, latency_expected with our empirical rules
        success_rate_expected = self.get_success_rate_expected(cpu_quota, memory_quota)
        latency_expected = self.get_latency_expected(cpu_quota, memory_quota)

        # call utility function
        utility_score = self.get_utility(cpu_quota, memory_quota,
                                         success_rate_expected, latency_expected, pod_num),
        return utility_score, success_rate_expected, latency_expected

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
        :param current_memory_bytes_quota:
        :param step_memory_bytes:
        :param current_pod_nums:
        :param step_pod_nums:
        :param current_jvm_heap_bytes_quota:
        :param step_jvm_heap_bytes:
        :param current_success_rate:
        :param current_latency:
        :return:
        '''
        if step_jvm_heap_bytes == 1:
            current_jvm_heap_bytes_quota *= 2
        elif step_jvm_heap_bytes == -1 and current_jvm_heap_bytes_quota > self.jvm_heap_quota_lower_bound:
            current_jvm_heap_bytes_quota /= 2
        # calculate utilities score for all set of options
        options_and_utilities = []
        for i in range(abs(step_cpu_cores) + 1):
            for j in range(abs(step_memory_bytes) + 1):
                inloop_cpu_step = i * (step_cpu_cores / abs(step_cpu_cores))
                inloop_mem_step = j * (step_memory_bytes / abs(step_memory_bytes))
                cpu_quota = current_cpu_cores_quota + 0.25 * inloop_cpu_step
                memory_quota = current_memory_bytes_quota * 2 ** inloop_mem_step
                if memory_quota < self.memory_quota_lower_bound: continue
                if current_jvm_heap_bytes_quota > memory_quota:
                    memory_quota = current_jvm_heap_bytes_quota
                utility_score, success_rate_expected, latency_expected = self.predict_for_option(cpu_quota,
                                                                                                 memory_quota,
                                                                                                 current_pod_nums),
                options_and_utilities += [
                    cpu_quota,
                    inloop_cpu_step,
                    memory_quota,
                    inloop_mem_step,
                    current_pod_nums,
                    current_jvm_heap_bytes_quota,
                    step_jvm_heap_bytes,
                    utility_score,
                    success_rate_expected,
                    latency_expected
                ]
        return options_and_utilities
