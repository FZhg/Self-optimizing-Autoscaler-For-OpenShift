import json
import logging
import pandas as pd


class Monitor:
    def __init__(self, knowledge_store, sd_client, sysdig_filter, look_back_duration, metric_sampling,
                 services_monitored):
        self.knowledge_store = knowledge_store
        self.sd_client = sd_client
        self.sysdig_filter = sysdig_filter
        self.look_back_duration = look_back_duration
        self.metric_sampling = metric_sampling
        self.metrics_to_pull = [
            {"id": "kube_pod_name"},
            {"id": "sysdig_container_cpu_cores_used",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "sysdig_container_cpu_quota_used_percent",
             "aggregations": {
                 "time": "avg",
                 "group": "sum"
             }
             },
            {"id": "sysdig_container_memory_used_bytes",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "sysdig_container_memory_limit_used_percent",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "sysdig_container_net_request_time",
             "aggregations": {
                 "time": "max",
             }
             },
            {"id": "sysdig_container_net_http_error_count",
             "aggregations": {
                 "time": "sum",
             }
             },
            {"id": "sysdig_container_net_request_count",
             "aggregations": {
                 "time": "sum",
             }
             },
            {"id": "sysdig_container_net_server_total_bytes",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "jmx_jvm_heap_used",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "jmx_jvm_heap_used_percent",
             "aggregations": {
                 "time": "avg",
             }
             },
        ]
        self.services_monitored = services_monitored

    def _pull_metrics_pod(self, look_back_duration):

        start_time = 0 - look_back_duration
        return self.sd_client.get_data(metrics=self.metrics_to_pull,  # List of metrics to query
                                       start_ts=start_time,  # Start of query span is 600 seconds ago
                                       end_ts=0,  # End the query span now
                                       sampling_s=self.metric_sampling,  # 1 data point per minute
                                       filter=self.sysdig_filter,  # The filter specifying the target host
                                       datasource_type='container')  # The source for our metrics is the container

    @staticmethod
    def get_column_names(metrics_definitions):
        metrics_definitions = metrics_definitions[1:]  # exclude pod names
        return ['time_stamp', 'pod_name'] + [definition['id'] for definition in metrics_definitions]

    @staticmethod
    def _convert_metrics_json_to_df(metrics_json, metrics_definitions):
        data = metrics_json['data']
        column_names = Monitor.get_column_names(metrics_definitions)
        rows = []
        for item in data:
            timestamp = item['t']
            values = item['d']
            pod_name = values[0]
            row = [timestamp, pod_name] + values[1:]
            rows.append(row)
        return pd.DataFrame(rows, columns=column_names)

    def _preprocess(self, response):
        """
        :param response:
        :return:
        """
        df = Monitor._convert_metrics_json_to_df(response, self.metrics_to_pull)
        return self.get_knowledge(df)

    def get_knowledge(self, df):
        """
        start_time_stamp
        end_time_stamp,
        service_name,
        pods_number,
        min_cpu_quota_percentage_across_pods,
        max_cpu_quota_percentage_across_pods,
        min_cpu_cores_used_across_pods,
        max_cpu_cores_used_across_pods,
        min_memory_quota_percentage_across_pods,
        max_memory_quota_percentage_across_pods,
        min_memory_used_bytes_across_pods,
        max_memory_used_bytes_across_pods,
        min_jvm_heap_used_percentage_across_pods,
        min_jvm_heap_used_bytes,
        success_rate,
        latency
        """
        column_names = [
            "start_time_stamp",
            "end_time_stamp",
            "service_name",
            "pods_number",
            "min_cpu_quota_percentage_across_pods",
            "max_cpu_quota_percentage_across_pods",
            "min_cpu_cores_used_across_pods",
            "max_cpu_cores_used_across_pods",
            "min_memory_quota_percentage_across_pods",
            "max_memory_quota_percentage_across_pods",
            "min_memory_used_bytes_across_pods",
            "max_memory_used_bytes_across_pods",
            "min_jvm_heap_used_percentage_across_pods",
            "min_jvm_heap_used_bytes",
            "success_rate",
            "latency"
        ]
        rows = []
        for service_name in self.services_monitored:
            service_df = df[df['pod_name'].str.startswith(service_name)]
            start_time_stamp = service_df['time_stamp'].min()
            end_time_stamp = service_df['time_stamp'].max()
            time_average_service_df = service_df.groupby('pod_name').mean()
            pods_num = service_df['pod_name'].nunique(dropna=True)
            min_cpu_quota_percentage_across_pods = (
                time_average_service_df['sysdig_container_cpu_quota_used_percent'].min())
            max_cpu_quota_percentage_across_pods = \
                time_average_service_df['sysdig_container_cpu_quota_used_percent'].max()
            min_cpu_cores_used_across_pods = time_average_service_df['sysdig_container_cpu_cores_used'].min()
            max_cpu_cores_used_across_pods = time_average_service_df['sysdig_container_cpu_cores_used'].max()
            min_memory_quota_percentage_across_pods = (
                time_average_service_df['sysdig_container_memory_limit_used_percent'].min())
            max_memory_quota_percentage_across_pods = (
                time_average_service_df['sysdig_container_memory_limit_used_percent'].max())
            min_memory_used_bytes_across_pods = (
                time_average_service_df['sysdig_container_memory_used_bytes'].min())
            max_memory_used_bytes_across_pods = (
                time_average_service_df['sysdig_container_memory_used_bytes'].max())
            min_jvm_heap_used_percentage_across_pods = (
                time_average_service_df['jmx_jvm_heap_used_percent'].min())
            max_jvm_heap_used_percentage_across_pods = (
                time_average_service_df['jmx_jvm_heap_used_percent'].max())
            min_jvm_heap_used_bytes = (
                time_average_service_df['jmx_jvm_heap_used'].min())
            max_jvm_heap_used_bytes = (
                time_average_service_df['jmx_jvm_heap_used'].max())
            total_request_count = service_df['sysdig_container_net_request_count'].sum()
            total_error_count = service_df['sysdig_container_net_http_error_count'].sum()
            if total_request_count == 0:
                success_rate = 0
            else:
                success_rate = (1 - (total_error_count / total_request_count)) * 100
            latency = service_df['sysdig_container_net_request_time'].max()
            row = [
                start_time_stamp,
                end_time_stamp,
                service_name,
                pods_num,
                min_cpu_quota_percentage_across_pods,
                max_cpu_quota_percentage_across_pods,
                min_cpu_cores_used_across_pods,
                max_cpu_cores_used_across_pods,
                min_memory_quota_percentage_across_pods,
                max_memory_quota_percentage_across_pods,
                min_memory_used_bytes_across_pods,
                max_memory_used_bytes_across_pods,
                min_jvm_heap_used_percentage_across_pods,
                max_jvm_heap_used_percentage_across_pods,
                min_jvm_heap_used_bytes,
                max_jvm_heap_used_bytes,
                success_rate,
                latency
            ]
            rows.append(row)

        return pd.DataFrame(rows, columns=column_names)

    def _write_to_knowledge_base(self, knowledge):
        self.knowledge_store.write_knowledge(knowledge)

    def update_knowledge(self):
        ok, pod_metrics_response = self._pull_metrics_pod(self.look_back_duration)
        if not ok:
            logging.debug(pod_metrics_response)
            logging.error("Failed to get metrics from SysDig.")
            return False
        logging.debug("Metrics Pulled: " + str(pod_metrics_response))
        knowledge = self._preprocess(pod_metrics_response)
        self._write_to_knowledge_base(knowledge)

