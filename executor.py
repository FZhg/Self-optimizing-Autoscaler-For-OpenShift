import os


class Executor:
    """
    Before running this code, make sure the oc client is in right cluster and namespace.
    """

    def __init__(self):
        pass

    @staticmethod
    def run_oc_command(oc_command):
        os.system(oc_command)

    @staticmethod
    def horizontal_scale(deployment_name, current_replicas, future_replicas):
        oc_command = f"oc scale --current_replicas={current_replicas} --replicas={future_replicas} deployment/{deployment_name}"
        Executor.run_oc_command(oc_command)

    def vertical_scale(self):
        pass


if __name__ == "__main__":
    executor = Executor()
    executor.horizontal_scale("acmeair-authservice", 4, 1)
