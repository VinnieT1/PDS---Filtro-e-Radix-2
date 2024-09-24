import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sounddevice as sd

def fft2(x):
    N = len(x)
    if N == 1:
        return x
    else:
        X_even = fft2(x[0::2])
        X_odd = fft2(x[1::2])
    
    X = np.zeros(N, dtype=complex)
    
    for m in range(N):
        m_alias = m % (N//2)
        X[m] = X_even[m_alias] + np.exp(-2j * np.pi * m / N) * X_odd[m_alias]

    return X

def send_and_receive(x, ser):
    received_values = []

    for i in range(len(x)):
        encoded_float = f'{x[i]}\n'.encode()
        ser.write(encoded_float)

        # Wait until data is received
        while ser.in_waiting == 0:
            pass

        # Read and decode the response
        while ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').strip()
            received_values.append(float(received))

        yield float(received)  # Yield each received value for real-time plotting

# Audio callback to capture microphone input
def audio_callback(indata, frames, time, status):
    global mic_data
    mic_data = indata[:, 0]

# Initialize sound device stream
sampling_rate = 2048
window_size = 5  # Sliding window in seconds
mic_data = np.zeros(sampling_rate)

# Open the serial port (modify COM port as needed)
ser = serial.Serial('COM5', 115200)
print('waiting for auto-reset...')  # arduino resets when serial connection is made, so wait for it to boot up
time.sleep(2)
print('waiting done')

# Setup the plot for real-time updating
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_ylim(-2, 2)  # amplitude axis

original_line, = ax.plot([], [], 'b', label='Original Signal')
filtered_line, = ax.plot([], [], 'r', label='Filtered Signal')
ax.legend()
plt.ylabel('Amplitude')

# Data lists for updating
received_values = []
time_data = []

# Initialize the plot
def init():
    original_line.set_data([], [])
    filtered_line.set_data([], [])
    return original_line, filtered_line

# Update function for the real-time plot
def update(frame):
    # Append time and received data for real-time plotting
    received_values.append(frame)
    
    # Ensure mic_data and received_values have the same length before plotting
    len_data = min(len(received_values), len(mic_data))
    time_data = np.arange(0, len_data) / sampling_rate  # Update time_data accordingly
    
    # Dynamically update x-axis limits based on the sliding window
    current_time = len(time_data) / sampling_rate
    ax.set_xlim(max(0, current_time - window_size), current_time)

    # Update plot with original and received data
    original_line.set_data(time_data, mic_data[:len_data])
    filtered_line.set_data(time_data, received_values[:len_data])
    
    return original_line, filtered_line

# Start recording microphone data
with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_rate):
    print('sending and receiving data...')
    ani = FuncAnimation(fig, update, frames=send_and_receive(mic_data, ser), init_func=init, blit=True, interval=1, repeat=False)

    plt.show()

# Close the serial port
ser.close()
print('data sent and received')

# After real-time plotting, process FFT
X = fft2(mic_data)
N = len(X)
X_mag = abs(X) / N
f = np.linspace(0, sampling_rate, N)[0:N // 2 + 1]
X_mag = 2 * X_mag[0:N // 2 + 1]
X_mag[0] = X_mag[0] / 2

plt.figure(figsize=(8, 6))
plt.xlabel('Freq (Hz)')
plt.ylabel('DFT Amplitude |X(freq)|')
plt.plot(f, X_mag, 'b')

Y = fft2(received_values)
Y_mag = abs(Y) / N
Y_mag = 2 * Y_mag[0:N // 2 + 1]
Y_mag[0] = Y_mag[0] / 2

plt.plot(f, Y_mag, 'r')

plt.legend(['Original Signal', 'Filtered Signal'])
plt.grid(True)
plt.show()
