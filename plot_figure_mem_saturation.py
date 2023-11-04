import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data from knowledge.csv and knowledge_baseline.csv
knowledge_df = pd.read_csv("knowledge_adaptive.csv")
knowledge_df['start_time_stamp'] = knowledge_df['start_time_stamp']-knowledge_df['start_time_stamp'].min()

knowledge_baseline_df = pd.read_csv("knowledge_baseline.csv")
knowledge_baseline_df['start_time_stamp'] = knowledge_baseline_df['start_time_stamp']-knowledge_baseline_df['start_time_stamp'].min()

# Define the list of services
services = ['acmeair-authservice', 'acmeair-bookingservice', 'acmeair-customerservice', 'acmeair-flightservice', 'acmeair-mainservice']

# Create a major figure with 5 subfigures
fig, axes = plt.subplots(1, 5, figsize=(30, 5), sharex=True)
# create all axes we need
ax0 = plt.subplot(151)
ax1 = ax0.twinx()
ax2 = plt.subplot(152)
ax3 = ax2.twinx()
ax4 = plt.subplot(153)
ax5 = ax4.twinx()
ax6 = plt.subplot(154)
ax7 = ax6.twinx()
ax8 = plt.subplot(155)
ax9 = ax8.twinx()
ax_list = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]

# Loop through each service and create a subfigure
for i, service in enumerate(services):
    # Filter data for the current service from knowledge.csv
    knowledge_data = knowledge_df[knowledge_df['service_name'] == service]

    # Filter data for the current service from knowledge_baseline.csv
    knowledge_baseline_data = knowledge_baseline_df[knowledge_baseline_df['service_name'] == service]

    # Plot the 'max mem' for knowledge.csv
    sns.lineplot(data=knowledge_data, x='start_time_stamp', y='max_memory_quota_percentage_across_pods', label='adaptive', color='r', ax=ax_list[i*2])

    # Plot the 'max mem' for knowledge_baseline.csv
    sns.lineplot(data=knowledge_baseline_data, x='start_time_stamp', y='max_memory_quota_percentage_across_pods', label='baseline', color='b', ax=ax_list[i*2])

    # Plot the 'pods_number' for knowledge.csv
    sns.lineplot(data=knowledge_data, x='start_time_stamp', y='pods_number', label='adapted pods number', color='g', ax=ax_list[i*2+1])

    # Plot the 'pods_number' for knowledge_baseline.csv
    sns.lineplot(data=knowledge_baseline_data, x='start_time_stamp', y='pods_number', label='baseline pods_number', color='black', ax=ax_list[i*2+1])

    # Set titles, labels, and legends for each subfigure
    axes[i].set_title(f"Service: {service}")
    axes[i].set_xlabel("Timestamp")
    axes[i].set_ylabel("max mem quota percentage")
    axes[i].legend(title="Type")

# Set a common x-axis label
axes[-1].set_xlabel("Timestamp")

# Adjust the layout of subfigures
plt.tight_layout()

# Save the figure to a file
plt.savefig("mem_saturation.png")

# Display the figure
plt.show()


