import configparser
import logging
import schedule
from sdcclient import IbmAuthHelper, SdMonitorClient
from monitor import Monitor
from knowledge_base import KnowledgeBase
from analyzer import Analyzer
from planner import Planner
<<<<<<< HEAD


def job(monitor, analyzer, planner):
    monitor.update_knowledge()
    options = analyzer.analyze()
    planner.plan(options)
=======
from executor import Executor


def job(monitor, analyzer, planner, executor):
    monitor.update_knowledge()
    options = analyzer.analyze()
    optimal_options = planner.plan(options)
    executor.execute(optimal_options)
>>>>>>> 19bad95d8adf536fbe00514c02a4ed50d2c64888


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
<<<<<<< HEAD
=======
    monthly_cost_limit_per_service = int(config['DEFAULT']['monthly_cost_limit_per_pod'])
>>>>>>> 19bad95d8adf536fbe00514c02a4ed50d2c64888

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
<<<<<<< HEAD
    planner = Planner()
    analyzer = Analyzer(knowledge_base, services_names)
=======
    planner = Planner(monthly_cost_limit_per_service)
    analyzer = Analyzer(knowledge_base, services_names)
    executor: Executor = Executor()
>>>>>>> 19bad95d8adf536fbe00514c02a4ed50d2c64888

    # The loop will execute every <loop_duration> seconds
    schedule.every(loop_duration).seconds.do(
        job,
        monitor=monitor,
        analyzer=analyzer,
<<<<<<< HEAD
        planner=planner
=======
        planner=planner,
        executor=executor
>>>>>>> 19bad95d8adf536fbe00514c02a4ed50d2c64888
    )

    logging.info("The MAPE-K loop Started.")
    while True:
        try:
            schedule.run_pending()
        except KeyboardInterrupt:
            schedule.clear()
            logging.info("The MAPE-K loop Stopped.")
            break


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%s', level=logging.DEBUG)
    main()
