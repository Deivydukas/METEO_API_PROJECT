import matplotlib.pyplot as plt


def plot_temperature(data):

    # Separate measured and forecast data
    measured = data[data["type"] == "Measured"]

    forecast = data[data["type"] == "Forecast"]

    # Create temperature plot
    plt.figure(figsize=(12, 6))

    plt.plot(
        measured.index,
        measured["airTemperature"],
        label="Measured",
    )

    plt.plot(
        forecast.index,
        forecast["airTemperature"],
        label="Forecast",
    )

    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")

    plt.title("Measured and Forecast Temperature")

    plt.legend()
    plt.grid()
    plt.tight_layout()

    plt.show()