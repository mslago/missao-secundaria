import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

for x in range(1, 10):
    # Load audio file
    audiofile = f"audiofile{x}.wav"
    fs, data = wavfile.read(audiofile)
    if len(data.shape) > 1:  # Stereo to mono
        data = data.mean(axis=1)

    # Perform FFT
    N = len(data)
    fft_result = np.fft.fft(data)
    freqs = np.fft.fftfreq(N, 1/fs)
    magnitude = np.abs(fft_result)

    # Filter frequencies: Only consider values above 400 Hz
    filter_idx = freqs > 400  # Boolean mask for frequencies > 400 Hz
    filtered_freqs = freqs[filter_idx]
    filtered_magnitude = magnitude[filter_idx]

    # Resonant Frequency is above 1500Hz, not what we want
    filter_2_idx = filtered_freqs < 1500
    filtered_2_freqs = filtered_freqs[filter_2_idx]
    filtered_2_magnitude = filtered_magnitude[filter_2_idx]

    # Find the resonant frequency
    peak_index = np.argmax(filtered_2_magnitude)
    resonant_freq = filtered_2_freqs[peak_index]
    print(f"Resonant Frequency: {resonant_freq} Hz")

    params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w",
          "axes.titlecolor" : "w"}
    plt.rcParams.update(params)

    # Plot filtered spectrum
    plt.plot(filtered_freqs, filtered_magnitude)
    plt.title("Speed of sound: " + str(round(resonant_freq*0.132*2, 2)) + " m/s")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.savefig(f"{audiofile}.png", dpi=400, transparent=True)
    x=x+1
