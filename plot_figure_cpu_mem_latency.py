import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

csv_adaptive = '../load-test-ece750/data/jsons/entire-sys/metrics_entire_sys_1699137000_1699137600_thread_1200_adaptive.csv'
csv_baseline = '../load-test-ece750/data/jsons/entire-sys/metrics_entire_sys_1699135980_1699136580_thread_1200_baseline.csv'

def plot_figure(metric_name, outname, second_metric_name="sysdig_container_count"):
  # Load the data from knowledge.csv and knowledge_baseline.csv
  knowledge_df = pd.read_csv(csv_adaptive)
  knowledge_df['timestamp'] = knowledge_df['timestamp']-knowledge_df['timestamp'].min()

  knowledge_baseline_df = pd.read_csv(csv_baseline)
  knowledge_baseline_df['timestamp'] = knowledge_baseline_df['timestamp']-knowledge_baseline_df['timestamp'].min()

  # Define the list of services
  services = ['acmeair-authservice', 'acmeair-bookingservice', 'acmeair-customerservice', 'acmeair-flightservice']

  # Create a major figure with 5 subfigures
  fig, axes = plt.subplots(2, 4, figsize=(30, 5), sharex=True)
  # create all axes we need
  '''ax0 = plt.subplot(241)
  ax1 = ax0.twinx()
  ax2 = plt.subplot(242)
  ax3 = ax2.twinx()
  ax4 = plt.subplot(243)
  ax5 = ax4.twinx()
  ax6 = plt.subplot(244)
  ax7 = ax6.twinx()
  ax_list = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7]'''
  # Loop through each service and create a subfigure
  for i, service in enumerate(services):
      # Filter data for the current service from knowledge.csv
      knowledge_data = knowledge_df[knowledge_df['pod_name'] == service]

      # Filter data for the current service from knowledge_baseline.csv
      knowledge_baseline_data = knowledge_baseline_df[knowledge_baseline_df['pod_name'] == service]

      # Plot the 'max cpu' for knowledge.csv
      sns.lineplot(data=knowledge_data, x='timestamp', y=metric_name, label='adaptive', color='r', ax=axes[0,i])

      # Plot the 'max cpu' for knowledge_baseline.csv
      sns.lineplot(data=knowledge_baseline_data, x='timestamp', y=metric_name, label='baseline', color='b', ax=axes[0,i])

      # Plot the 'pods_number' for knowledge.csv
      sns.lineplot(data=knowledge_data, x='timestamp', y=second_metric_name, label='adapted pods number', color='g', ax=axes[1,i])

      # Plot the 'pods_number' for knowledge_baseline.csv
      sns.lineplot(data=knowledge_baseline_data, x='timestamp', y=second_metric_name, label='baseline pods_number', color='black', ax=axes[1,i])

      # Set titles, labels, and legends for each subfigure
      #axes[i].set_title(f"Service: {service}")
      #axes[i].set_xlabel("Timestamp")
      #axes[i].set_ylabel("min cpu quota percentage")
      #axes[i].legend(title="Type")

  # Set a common x-axis label
  #axes[-1].set_xlabel("Timestamp")

  # Adjust the layout of subfigures
  plt.tight_layout()

  # Save the figure to a file
  plt.savefig(str(outname)+".png")

  # Display the figure
  #plt.show()
  plt.clf()

def main():
  plot_figure("sysdig_container_cpu_quota_used_percent", "cpu_saturation")
  plot_figure("sysdig_container_memory_used_percent", "mem_saturation")
  plot_figure("sysdig_container_net_request_time", "latency")

if __name__=="__main__":
  main()