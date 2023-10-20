import logging
import time

import pandas as pd
import numpy as np


class Analyzer:
    def __init__(self, knowledge_base, services_analyzed):
        self.knowledge_base = knowledge_base
        self.services_analyzed = services_analyzed

    def analyze(self):
        knowledge = self.knowledge_base.get_current_knowledge()
        options_for_all_services = []
        for service_name in self.services_analyzed:
            service_knowledge = knowledge[knowledge['service_name'] == service_name]
            if not Analyzer.is_adaption_required(service_knowledge):
                continue
            pods_number = service_knowledge['pods_number'].values[0]
            min_cpu_quota_percentage_across_pods = service_knowledge['min_cpu_quota_percentage_across_pods'].values[0]
            max_cpu_quota_percentage_across_pods = service_knowledge['max_cpu_quota_percentage_across_pods'].values[0]
            min_memory_quota_percentage_across_pods = \
                service_knowledge['min_memory_quota_percentage_across_pods'].values[0]
            max_memory_quota_percentage_across_pods = \
                service_knowledge['max_memory_quota_percentage_across_pods'].values[0]
            min_jvm_heap_used_percentage_across_pods = \
                service_knowledge['min_jvm_heap_used_percentage_across_pods'].values[0]
            cpu_quota_cores = service_knowledge['cpu_quota_cores'].values[0]
            memory_quota_mb = service_knowledge['memory_quota_mb'].values[0]
            jvm_heap_max_mb = service_knowledge['jvm_heap_max_mb'].values[0]
            success_rate = service_knowledge['success_rate'].values[0]
            latency_ms = service_knowledge['latency_ms'].values[0]

            num_steps_cpu = 0
            num_steps_memory = 0
            num_steps_replica = 0
            num_steps_jvm_heap_max = 0

            if min_jvm_heap_used_percentage_across_pods >= 80:
                num_steps_jvm_heap_max = 2

            if max_cpu_quota_percentage_across_pods <= 40:
                num_steps_cpu = - 2
            elif min_cpu_quota_percentage_across_pods >= 90:
                num_steps_cpu = 2

            if max_memory_quota_percentage_across_pods <= 40:
                num_steps_memory = -2
            elif min_memory_quota_percentage_across_pods >= 80:
                num_steps_memory = 2

            if min_cpu_quota_percentage_across_pods >= 90 and min_memory_quota_percentage_across_pods >= 80:
                num_steps_replica = 1
            elif max_cpu_quota_percentage_across_pods <= 40 and max_memory_quota_percentage_across_pods < 40:
                num_steps_replica = -1
            elif success_rate <= 99.5 or latency_ms >= 300:
                num_steps_replica = 2

            options_cpu_memory_jvm = self.analyze_options(
                service_name=service_name,
                current_cpu_cores_quota=cpu_quota_cores,
                num_steps_cpu=num_steps_cpu,
                current_memory_quota_mb=memory_quota_mb,
                num_steps_memory=num_steps_memory,
                current_replica_nums=pods_number,
                current_jvm_heap_max_mb=jvm_heap_max_mb,
                num_steps_jvm_heap_max=num_steps_jvm_heap_max,
                current_success_rate=success_rate,
                current_latency_ms=latency_ms
            )

            options_replica_num = self.analyze_options(
                service_name=service_name,
                current_cpu_cores_quota=cpu_quota_cores,
                current_memory_quota_mb=memory_quota_mb,
                current_jvm_heap_max_mb=jvm_heap_max_mb,
                current_replica_nums=pods_number,
                nums_steps_replica=num_steps_replica,
                current_success_rate=success_rate,
                current_latency_ms=latency_ms
            )
            options = pd.concat([options_cpu_memory_jvm, options_replica_num], ignore_index=True)
            options_for_all_services.append(options)
        options_for_all_services = pd.concat(options_for_all_services, ignore_index=True)
        logging.debug("options:\n" + options_for_all_services.to_string())
        return options_for_all_services

    @staticmethod
    def is_adaption_required(service_knowledge):
        if service_knowledge.empty:
            return False
        if service_knowledge.isnull().values.any():
            return False
        return True

    @staticmethod
    def get_monthly_cost(replica_num, cpu_cores_used, memory_mb_used):
        # From IBM Cloud, 1 core cpu cost $12/ month; 1 GB memory cost $5/Month.
        return (cpu_cores_used * 12 + memory_mb_used * 5 / 1024) * replica_num

    @staticmethod
    def get_cost_utility_preference(monthly_cost):
        if monthly_cost <= 10:
            return 1.0
        elif monthly_cost <= 20:
            return 0.9
        elif monthly_cost <= 30:
            return 0.7
        elif monthly_cost <= 80:
            return 0.3
        else:
            return 0

    @staticmethod
    def get_success_rate_utility_preference(success_rate):
        if success_rate > 99.9:
            return 1
        elif success_rate > 99.5:
            return 0.1
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
            return 0.1
        else:
            return 0

    @staticmethod
    def convert_nano_seconds_to_milli_seconds(nano_seconds):
        return 1

    def get_utility(self,
                    monthly_cost,
                    success_rate,
                    latency,
                    cost_weight=0.3,
                    success_rate_weight=0.4,
                    latency_weight=0.5):
        utility = 0
        utility += cost_weight * self.get_cost_utility_preference(monthly_cost)
        utility += success_rate_weight * self.get_success_rate_utility_preference(success_rate)
        utility += latency_weight * self.get_latency_utility_preference(latency)
        return utility

    @staticmethod
    def get_success_rate_expected(cpu_quota, memory_quota, replica_num):
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

    @staticmethod
    def get_latency_expected(cpu_quota, memory_quota):
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
        return

    @staticmethod
    def get_possible_values(start, step, num_steps, lower_limit):
        if num_steps == 0:
            return [start]
        if num_steps > 0:
            return [start + step * i for i in range(1, num_steps + 1, 1) if start + step * i >= lower_limit]
        else:
            return [start + step * i for i in range(-1, num_steps - 1, -1) if start + step * i >= lower_limit]

    @staticmethod
    def analyze_options(service_name,
                        current_cpu_cores_quota=0.5,
                        step_cpu_cores=0.25,
                        num_steps_cpu=0,
                        min_cpu_cores_quota=0.25,
                        current_memory_quota_mb=412,
                        step_memory_mb=256,
                        num_steps_memory=0,
                        min_memory_quota_mb=512,
                        current_replica_nums=1,
                        step_replica=1,
                        nums_steps_replica=0,
                        min_replica_num=1,
                        current_jvm_heap_max_mb=512,
                        step_jvm_heap_max_mb=64,
                        num_steps_jvm_heap_max=0,
                        min_jvm_heap_max_mb=512,
                        current_success_rate=100,
                        current_latency_ms=100,
                        ):
        possible_cpu_cores_quota = Analyzer.get_possible_values(current_cpu_cores_quota, step_cpu_cores, num_steps_cpu,
                                                                min_cpu_cores_quota)
        possible_memory_quota_mb = Analyzer.get_possible_values(current_memory_quota_mb, step_memory_mb,
                                                                num_steps_memory, min_memory_quota_mb)
        possible_replica_num = Analyzer.get_possible_values(current_replica_nums, step_replica, nums_steps_replica,
                                                            min_replica_num)
        possible_jvm_heap_max_mb = Analyzer.get_possible_values(current_jvm_heap_max_mb, step_jvm_heap_max_mb,
                                                                num_steps_jvm_heap_max, min_jvm_heap_max_mb)
        rows = []
        column_names = [
            'service_name',
            'cpu_cores_quota',
            'memory_quota_mb',
            'replica_num',
            'jvm_heap_max_mb',
            'expected_monthly_cost',
            'expected_success_rate',
            'expected_latency',
            'expected_utility'
        ]
        for cpu_cores_quota in possible_cpu_cores_quota:
            for memory_quota_mb in possible_memory_quota_mb:
                for replica_num in possible_replica_num:
                    for jvm_heap_max_mb in possible_jvm_heap_max_mb:
                        if cpu_cores_quota == current_cpu_cores_quota and memory_quota_mb == current_cpu_cores_quota and replica_num == current_replica_nums and jvm_heap_max_mb == current_jvm_heap_max_mb:
                            continue
                        if jvm_heap_max_mb > current_jvm_heap_max_mb and jvm_heap_max_mb > memory_quota_mb:
                            while jvm_heap_max_mb > memory_quota_mb:
                                memory_quota_mb += step_memory_mb
                        elif jvm_heap_max_mb > memory_quota_mb:
                            jvm_heap_max_mb = memory_quota_mb
                        expected_monthly_cost = Analyzer.get_monthly_cost(replica_num, cpu_cores_quota, memory_quota_mb)
                        # expected_success_rate = Analyzer.get_success_rate_expected(cpu_cores_quota)
                        # expected_latency = Analyzer.get_latency_expected()
                        # expected_utility = Analyzer.get_utility(expected_monthly_cost, expected_success_rate,
                        #                                         expected_latency)

                        row = [service_name, cpu_cores_quota, memory_quota_mb, replica_num, jvm_heap_max_mb,
                               expected_monthly_cost,
                               0, 0, 0]
                        rows.append(row)
        df = pd.DataFrame(rows, columns=column_names)
        output_filename = f"{time.time()}-cpu_{current_cpu_cores_quota}_memo_{current_memory_quota_mb}_replica_{current_replica_nums}_jvm_{current_jvm_heap_max_mb}_success_rate_{current_success_rate:.2f}_latency_{current_latency_ms:.2f}.csv"
        df.to_csv('options/' + output_filename, index=False)
        return df
