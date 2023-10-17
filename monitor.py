import logging


class Monitor:
    def __init__(self, knowledge_store, sd_client, sysdig_filter, look_back_duration, metric_sampling):
        self.knowledgeStore = knowledge_store
        self.sd_client = sd_client
        self.sysdig_filter = sysdig_filter
        self.look_back_duration = look_back_duration
        self.metric_sampling = metric_sampling

    def _pull_metrics(self, look_back_duration):
        metrics = [
            {"id": "kube_pod_name"},
            {"id": "sysdig_container_cpu_cores_used",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "sysdig_container_memory_used_bytes",
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
            {"id": "jmx_jvm_heap_used",
             "aggregations": {
                 "time": "avg",
             }
             },
            {"id": "jmx_jvm_thread_count",
             "aggregations": {
                 "time": "avg",
             }
             },
        ]
        start_time = 0 - look_back_duration
        return self.sd_client.get_data(metrics=metrics,  # List of metrics to query
                                       start_ts=start_time,  # Start of query span is 600 seconds ago
                                       end_ts=0,  # End the query span now
                                       sampling_s=self.metric_sampling,  # 1 data point per minute
                                       filter=self.sysdig_filter,  # The filter specifying the target host
                                       datasource_type='container')  # The source for our metrics is the container

    def _preprocess(self, response):
        return ""

    def _write_to_knowledge_base(self, knowledge):
        pass

    def update_knowledge(self):
        ok, response = self._pull_metrics(self.look_back_duration)
        if not ok:
            logging.debug(response)
            logging.error("Failed to get metrics from SysDig.")
        logging.DEBUG(response)
        knowledge = self._preprocess(response)
        self._write_to_knowledge_base(knowledge)


