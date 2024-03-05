import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Step 1: Load the CSV data
# Make sure to replace 'output.csv' with the actual path to your CSV file
df = pd.read_csv('output.csv')

# Assuming the first column is frequencies, and the other columns are intensities at different time points
frequencies = df.iloc[:, 0].values  # Frequency values
time_columns = df.columns[1:]  # Time points

# Step 2: Set up the plot
fig, ax = plt.subplots()
ax.set_xlim(df.iloc[:, 0].min(), df.iloc[:, 0].max())  # Set x-axis limits based on frequency range
ax.set_ylim(df.iloc[:, 1:].min().min(), df.iloc[:, 1:].max().max())  # Set y-axis limits based on min/max intensity values

# Create a scatter plot with initial intensity values (e.g., from the first time point)
scat = ax.scatter(frequencies, df[time_columns[0]].values, s=1, alpha=0.75)

def update(frame_number):
    # Update scatter plot with intensity values for the current time point
    scat.set_offsets(np.c_[frequencies, df[time_columns[frame_number]].values])
    ax.set_title(time_columns[frame_number])  # Update the plot title to show the current time point

# Step 3: Create the animation
ani = FuncAnimation(fig, update, frames=range(len(time_columns)), repeat=True)

plt.show()
