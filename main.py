import configparser
import logging

import schedule
from sdcclient import IbmAuthHelper, SdMonitorClient
from monitor import Monitor


def job(monitor):
    logging.info("Start Event loop")


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

    # initialize sys-dig client
    ibm_headers = IbmAuthHelper.get_headers(metrics_url, metrics_api_key, metrics_guid)
    sd_client = SdMonitorClient(sdc_url=metrics_url, custom_headers=ibm_headers)

    monitor = Monitor()
    # The loop will execute every <loop_duration> seconds
    schedule.every(loop_duration).seconds.do(
        job,
        look_back_duration=look_back_duration,
        sd_client=sd_client,
        metrics_filter=metrics_filter
    )

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    logging.basicConfig(filename='MAPE-K.log', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%s')
    main()
