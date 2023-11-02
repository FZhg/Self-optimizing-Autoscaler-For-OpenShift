import logging


class Planner:
    def __init__(self, monthly_cost_limit_per_service):
        self.monthly_cost_limit = monthly_cost_limit_per_service

    def plan(self, options):
        options = options[options['expected_monthly_cost'] <= self.monthly_cost_limit]
        min_cost_options = options.sort_values('expected_monthly_cost').drop_duplicates('service_name')
        return min_cost_options





