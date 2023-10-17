import configparser
import sched
from sdcclient import IbmAuthHelper, SdMonitorClient


def pull_metrics(loop_back_duration, sd_client):

    metrics = [

    ]


def execute_event_loop(loop_back_duration, sd_client):
    pull_metrics(loop_back_duration, sd_client)


def main():
    # Parse the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    loop_duration = int(config['DEFAULT']['loop_duration'])
    loop_back_duration = int(config['DEFAULT']['loop_back_duration'])
    metrics_url = config['DEFAULT']['metrics_url']
    metrics_api_key = config['DEFAULT']['metrics_api_key']
    metrics_guid = config['DEFAULT']['metrics_guid']

    # initialize sys-dig client
    ibm_headers = IbmAuthHelper.get_headers(metrics_url, metrics_api_key, metrics_guid)
    sd_client = SdMonitorClient(sdc_url=metrics_url, custom_headers=ibm_headers)

    # The loop will execute every <loop_duration> seconds
    scheduler = sched.scheduler()
    scheduler.enter(loop_duration,
                    1,
                    execute_event_loop,
                    kwargs={
                        "loop_back_duration": loop_back_duration,
                        "sd_client": sd_client
                    }
                    )
    scheduler.run()


if __name__ == '__main__':
    main()
