import configparser
import logging
import schedule
from sdcclient import IbmAuthHelper, SdMonitorClient
from monitor import Monitor


def job(monitor):
    logging.info("Start Event loop")
    monitor.update_knowledge()


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
    services_monitored = [
        "acmeair-authservice",
        "acmeair-bookingservice",
        "acmeair-customerservice",
        "acmeair-flightservice",
        "acmeair-mainservice"
    ]
    monitor = Monitor("", sd_client, metrics_filter, look_back_duration, metric_sampling, services_monitored)
    # The loop will execute every <loop_duration> seconds
    schedule.every(loop_duration).seconds.do(
        job,
        monitor=monitor
    )

    # while True:
    #     schedule.run_pending()
    job(monitor)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%s', level=logging.DEBUG)
    main()
