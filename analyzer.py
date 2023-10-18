class Analyzer:
    def __init__(self, knowledge_base, plan_pool, services_analyzed):
        self.knowledge_base = knowledge_base
        self.plan_pool = plan_pool
        self.services_analyzed = services_analyzed


    def analyze(self):
        knowledge = self.knowledge_base.get_current_knowledge()
        for service_name in self.services_analyzed[:1]:
            service_knowledge = knowledge[knowledge['service_name'] == service_name]
            print(service_knowledge.to_string())

