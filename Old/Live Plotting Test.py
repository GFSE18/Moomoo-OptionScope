import matplotlib.pyplot as plt
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler

# Create 16 subplots
def live_plot_sixteen_random_numbers():
    plt.ion()
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))  # 4x4 grid for 16 subplots
    axes = axes.flatten()  # Flatten for easier iteration
    
    # Initialize data for each subplot
    x_data = [[] for _ in range(16)]
    y_data = [[] for _ in range(16)]
    lines = []
    
    for i, ax in enumerate(axes):
        ax.set_title(f"Live Plot of Random Numbers - Set {i+1}")
        ax.set_xlabel("Time Step")
        ax.set_ylabel("Random Number")
        line, = ax.plot([], [], label=f"Set {i+1}")
        ax.legend()
        lines.append(line)

    time_step = [0]  # Use a mutable object to track the time step
    
    # Function to update plots
    def update_plots():
        for i in range(16):
            random_number = np.random.random()
            x_data[i].append(time_step[0])
            y_data[i].append(random_number)
            lines[i].set_xdata(x_data[i])
            lines[i].set_ydata(y_data[i])
            axes[i].relim()
            axes[i].autoscale_view()
        
        # Redraw the updated plots
        fig.canvas.draw()
        fig.canvas.flush_events()
        time_step[0] += 1

    # Scheduler to call update_plots every 1 second
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_plots, 'interval', seconds=1)
    scheduler.start()

    # Keep the program running to allow live updates
    try:
        while True:
            plt.pause(0.1)  # Prevents program from exiting immediately
    except KeyboardInterrupt:
        print("Live plot stopped.")
        scheduler.shutdown()
        plt.ioff()
        plt.show()

live_plot_sixteen_random_numbers()