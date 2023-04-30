import math
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise


class PDR:
    def __init__(self, acc_data, gyro_data, mag_data, time_interval):
        self.acc_data = acc_data  # Accelerometer data
        self.gyro_data = gyro_data  # Gyroscope data
        self.mag_data = mag_data  # Magnetometer data
        self.time_interval = time_interval  # Time interval between sensor readings

        # Step detection parameters
        self.step_count = 0
        self.last_max = 0
        self.last_min = 0
        self.step_threshold = 0.5

        # Step length estimation parameters
        self.K1 = 0.4
        self.K2 = 0.2
        self.K3 = 0.4
        self.step_length = 0

        # Heading estimation parameters
        self.pitch_acc = 0
        self.roll_acc = 0
        self.pitch_gyro = 0
        self.roll_gyro = 0
        self.heading_mag = 0
        self.heading_gyro = 0
        self.heading = 0
        self.alpha = 0.5

        # Position estimation parameters
        self.position = np.array([0, 0])
        self.prev_position = np.array([0, 0])

    def data_filter(self, data, low_cut, high_cut, fs):
        """
        Applies a bandpass filter to the given data.
        :param data: The data to filter.
        :param low_cut: The low cut frequency for the filter.
        :param high_cut: The high cut frequency for the filter.
        :param fs: The sampling rate of the data.
        :return: The filtered data.
        """
        nyquist_freq = 0.5 * fs
        low = low_cut / nyquist_freq
        high = high_cut / nyquist_freq
        b, a = butter(4, [low, high], btype='band')
        filtered_data = filtfilt(b, a, data)
        return filtered_data

    def estimate_step_length(self, filtered_data, fs):
        """
        Estimates the step length using Kim's method.

        :param filtered_data: The filtered accelerometer data.
        :param fs: The sampling rate of the data.
        :return: The estimated step length in meters.
        """
        # Compute the norm of the acceleration data
        norm = np.linalg.norm(filtered_data, axis=1)

        # Find the local minima and maxima of the norm data
        maxima, _ = find_peaks(norm, distance=int(fs*0.5))
        minima, _ = find_peaks(-norm, distance=int(fs*0.5))
        peaks = np.concatenate((maxima, minima))

        # Compute the time between each peak
        times = peaks / fs
        intervals = np.diff(times)

        # Compute the step length using Kim's method
        step_length = 0.43 * np.power(intervals, 0.5)

        return step_length

    def estimate_heading(self, accel_data, gyro_data, mag_data):
        """
        Estimates the heading using sensor fusion of accelerometer, gyroscope, and magnetometer data.
        :param accel_data: The accelerometer data.
        :param gyro_data: The gyroscope data.
        :param mag_data: The magnetometer data.
        :return: The estimated heading in degrees.
        """
        # Compute pitch and roll using the accelerometer and gyroscope data
        pitch_acc = np.arctan2(accel_data[:, 0], np.sqrt(
            accel_data[:, 1]**2 + accel_data[:, 2]**2))
        roll_acc = np.arctan2(-accel_data[:, 1], accel_data[:, 2])
        dt = np.diff(gyro_data[:, 3])

        # Integrate the gyroscope data to obtain pitch and roll
        pitch_gyro = np.cumsum(gyro_data[:, 0] * dt)
        roll_gyro = np.cumsum(gyro_data[:, 1] * dt)

        # Combine the pitch and roll data using the Kalman filter
        kalman = KalmanFilter(dim_x=2, dim_z=2)
        kalman.x = np.array([pitch_gyro[0], roll_gyro[0]])
        kalman.F = np.array([[1, -dt[0]], [0, 1]])
        kalman.H = np.array([[1, 0], [0, 1]])
        kalman.P *= 1000
        kalman.R = np.array([[0.5, 0], [0, 0.5]])
        kalman.Q = Q_discrete_white_noise(2, dt[0], 0.1)
        pitch_kalman = np.zeros_like(pitch_gyro)
        roll_kalman = np.zeros_like(roll_gyro)
        for i in range(len(pitch_gyro)):
            kalman.predict()
            kalman.update(np.array([pitch_gyro[i], roll_gyro[i]]))
            pitch_kalman[i] = kalman.x[0]
            roll_kalman[i] = kalman.x[1]

        # Combine the pitch, roll, and magnetometer data to compute the heading
        mx = mag_data[:, 0]
        my = mag_data[:, 1]
        mz = mag_data[:, 2]
        yaw_mag = np.arctan2(my, mx)
        heading = np.degrees(np.arctan2(np.sin(yaw_mag - roll_kalman), np.cos(yaw_mag - roll_kalman)
                             * np.sin(pitch_kalman) - np.sin(yaw_mag - roll_kalman) * np.cos(pitch_kalman)))

        return heading

    def position_estimation(self):
        # calculate the x and y components of the step
        x_step = self.step_length * math.sin(self.angle)
        y_step = self.step_length * math.cos(self.angle)

        # calculate the change in position
        delta_x = x_step * math.sin(math.radians(self.heading))
        delta_y = y_step * math.cos(math.radians(self.heading))

        # update the current position
        self.cur_pos[0] = self.prev_pos[0] + delta_x
        self.cur_pos[1] = self.prev_pos[1] + delta_y

        # update the previous position
        self.prev_pos[0] = self.cur_pos[0]
        self.prev_pos[1] = self.cur_pos[1]

        return self.cur_pos


# initialize the PDR object

# generate some example data
acc_data = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
            (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)]
gyro_data = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
             (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]
mag_data = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]


def estimate_location(acc_data, gyro_data, mag_data):
    pdr = PDR(acc_data, gyro_data, mag_data, 2)

    # filter the accelerometer data
    # pdr.data_filter(acc_data, 0.75, 20, 1)

    # estimate the step length
    pdr.estimate_step_length(acc_data, 100)

    # estimate the heading
    pdr.estimate_heading(acc_data, gyro_data, mag_data)

    # perform position estimation
    cur_pos = pdr.position_estimation()

    return cur_pos
