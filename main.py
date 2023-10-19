import configparser
import logging
import schedule
from sdcclient import IbmAuthHelper, SdMonitorClient
from monitor import Monitor
from knowledge_base import KnowledgeBase
from analyzer import Analyzer
from planner import Planner


def job(monitor, analyzer):
    logging.info("Start Event loop")
    monitor.update_knowledge()
    # analyzer.analyze()


def main():
    # Parse the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    loop_duration = int(config['DEFAULT']['loop_duration'])
    look_back_duration = int(config['DEFAULT']['look_back_duration'])
    metrics_url = config['DEFAULT']['metrics_url']
    metrics_api_key = config['DEFAULT']['metrics_api_key']
    metrics_guid = config['DEFAULT']['metrics_guid']
    metrics_filter = config['DEFAULT']['metrics_filter']
    metric_sampling = config['DEFAULT']['metric_sampling']

    # initialize sys-dig client
    ibm_headers = IbmAuthHelper.get_headers(metrics_url, metrics_api_key, metrics_guid)
    sd_client = SdMonitorClient(sdc_url=metrics_url, custom_headers=ibm_headers)
    services_names = [
        "acmeair-authservice",
        "acmeair-bookingservice",
        "acmeair-customerservice",
        "acmeair-flightservice",
        "acmeair-mainservice"
    ]
    knowledge_base = KnowledgeBase('knowledge.csv')
    monitor = Monitor(knowledge_base, sd_client, metrics_filter, look_back_duration, metric_sampling,
                      services_names)
    planner = Planner()
    analyzer = Analyzer(knowledge_base, planner, services_names, cost_weight=0.3, success_rate_weight=0.3, latency_weight=0.4)

    # The loop will execute every <loop_duration> seconds
    schedule.every(loop_duration).seconds.do(
        job,
        monitor=monitor,
        analyzer=analyzer
    )

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%s', level=logging.DEBUG)
    main()
