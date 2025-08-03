"""
Real-time Data Plotter

A decoupled, reusable component for real-time data visualization.
Supports multi-channel data display with configurable parameters.
"""

import sys
import numpy as np
import pyqtgraph as pg
import collections
import threading
from typing import List, Optional, Callable, Union
from pyqtgraph.Qt import QtWidgets, QtCore


class RealtimePlotter:
    """
    A real-time data plotter that can display multiple channels of data.
    
    This class provides a decoupled visualization component that can be easily
    integrated into any application that needs to display streaming data.
    """
    
    def __init__(self, 
                 num_channels: int = 2,
                 plot_duration: float = 20.0,
                 sampling_rate: float = 250.0,
                 update_interval: int = 50,
                 window_title: str = "Data Visualization",
                 window_size: tuple = (1000, 800),
                 channel_names: Optional[List[str]] = None,
                 colors: Optional[List[tuple]] = None):
        """
        Initialize the real-time plotter.
        
        Args:
            num_channels: Number of data channels to display
            plot_duration: Duration of data to display in seconds
            sampling_rate: Data sampling rate in Hz
            update_interval: Plot update interval in milliseconds
            window_title: Title of the plot window
            window_size: Window size as (width, height)
            channel_names: Custom names for channels (optional)
            colors: Custom colors for each channel as RGB tuples (optional)
        """
        self.num_channels = num_channels
        self.plot_duration = plot_duration
        self.sampling_rate = sampling_rate
        self.update_interval = update_interval
        self.window_title = window_title
        self.window_size = window_size
        
        # Calculate buffer size
        self.buffer_size = int(plot_duration * sampling_rate)
        
        # Generate time axis
        self.time_axis = np.linspace(0, plot_duration, self.buffer_size)
        
        # Set up channel names
        if channel_names is None:
            self.channel_names = [f"Channel {i + 1}" for i in range(num_channels)]
        else:
            self.channel_names = channel_names[:num_channels]
            
        # Set up colors
        if colors is None:
            self.colors = [(0, 100 + i * 20, 255 - i * 20) for i in range(num_channels)]
        else:
            self.colors = colors[:num_channels]
            
        # Initialize Qt application if not exists
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)
            
        # Initialize UI components
        self._init_ui()
        
        # Initialize data structures
        self._init_data_structures()
        
        # Set up timer for updates
        self._init_timer()
        
        # Thread safety
        self._data_lock = threading.Lock()
        
        # Callbacks
        self._data_callbacks: List[Callable] = []
        self._close_callbacks: List[Callable] = []
        
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main window
        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle(self.window_title)
        self.win.resize(*self.window_size)
        
        # Set up close event handler
        self.win.closeEvent = self._on_window_close
        
        # Create scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.win.setCentralWidget(scroll_area)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        scroll_area.setWidget(central_widget)
        self.layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Initialize plot components
        self.plot_widgets = []
        self.curves = []
        
        # Create plot widgets for each channel
        for i in range(self.num_channels):
            self._create_channel_plot(i)
            
        # Add stretch to layout
        self.layout.addStretch(1)
        
    def _create_channel_plot(self, channel_idx: int):
        """Create a plot widget for a specific channel."""
        # Create group box
        group_box = QtWidgets.QGroupBox(self.channel_names[channel_idx])
        group_layout = QtWidgets.QVBoxLayout()
        group_box.setLayout(group_layout)
        self.layout.addWidget(group_box)
        
        # Create plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.setLabel('bottom', 'Time', 's')
        plot_widget.setLabel('left', 'Amplitude')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.setXRange(0, self.plot_duration)
        
        # Create curve
        curve = plot_widget.plot(
            [], [],
            pen=pg.mkPen(color=self.colors[channel_idx], width=1),
            connect='finite'
        )
        
        group_layout.addWidget(plot_widget)
        
        # Store references
        self.plot_widgets.append(plot_widget)
        self.curves.append(curve)
        
    def _init_data_structures(self):
        """Initialize data buffers and related structures."""
        self.data_buffers = []
        for _ in range(self.num_channels):
            buffer = collections.deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
            self.data_buffers.append(buffer)
            
    def _init_timer(self):
        """Initialize the update timer."""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_plots)
        
    def _update_plots(self):
        """Update all plot displays."""
        with self._data_lock:
            for i in range(self.num_channels):
                if i < len(self.data_buffers):
                    y_data = np.array(self.data_buffers[i])
                    self.curves[i].setData(self.time_axis, y_data)
                    
        # Call registered callbacks
        for callback in self._data_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in data callback: {e}")
                
    def add_data_point(self, channel_idx: int, value: float):
        """
        Add a single data point to a specific channel.
        
        Args:
            channel_idx: Index of the channel (0-based)
            value: Data value to add
        """
        if 0 <= channel_idx < self.num_channels:
            with self._data_lock:
                self.data_buffers[channel_idx].append(value)
                
    def add_data_points(self, channel_idx: int, values: List[float]):
        """
        Add multiple data points to a specific channel.
        
        Args:
            channel_idx: Index of the channel (0-based)
            values: List of data values to add
        """
        if 0 <= channel_idx < self.num_channels:
            with self._data_lock:
                for value in values:
                    self.data_buffers[channel_idx].append(value)
                    
    def add_multi_channel_data(self, data: List[List[float]]):
        """
        Add data for multiple channels at once.
        
        Args:
            data: List of lists, where each inner list contains data for one channel
        """
        with self._data_lock:
            for ch_idx, channel_data in enumerate(data):
                if ch_idx < self.num_channels:
                    for value in channel_data:
                        self.data_buffers[ch_idx].append(value)
                        
    def clear_data(self, channel_idx: Optional[int] = None):
        """
        Clear data from buffers.
        
        Args:
            channel_idx: Index of channel to clear, or None to clear all channels
        """
        with self._data_lock:
            if channel_idx is None:
                # Clear all channels
                for buffer in self.data_buffers:
                    buffer.clear()
                    # Refill with zeros
                    for _ in range(self.buffer_size):
                        buffer.append(0.0)
            else:
                if 0 <= channel_idx < self.num_channels:
                    self.data_buffers[channel_idx].clear()
                    # Refill with zeros
                    for _ in range(self.buffer_size):
                        self.data_buffers[channel_idx].append(0.0)
                        
    def set_y_range(self, channel_idx: int, min_val: float, max_val: float):
        """
        Set the Y-axis range for a specific channel.
        
        Args:
            channel_idx: Index of the channel
            min_val: Minimum Y value
            max_val: Maximum Y value
        """
        if 0 <= channel_idx < self.num_channels:
            self.plot_widgets[channel_idx].setYRange(min_val, max_val)
            
    def enable_auto_range(self, channel_idx: int, enable: bool = True):
        """
        Enable or disable auto-ranging for a specific channel.
        
        Args:
            channel_idx: Index of the channel
            enable: Whether to enable auto-ranging
        """
        if 0 <= channel_idx < self.num_channels:
            self.plot_widgets[channel_idx].enableAutoRange(enable=enable)
            
    def add_data_callback(self, callback: Callable):
        """
        Add a callback function that will be called after each plot update.
        
        Args:
            callback: Function to call (should take no arguments)
        """
        self._data_callbacks.append(callback)
        
    def remove_data_callback(self, callback: Callable):
        """
        Remove a previously added callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self._data_callbacks:
            self._data_callbacks.remove(callback)
            
    def add_close_callback(self, callback: Callable):
        """
        Add a callback function that will be called when the window is closed.
        
        Args:
            callback: Function to call (should take no arguments)
        """
        self._close_callbacks.append(callback)
        
    def remove_close_callback(self, callback: Callable):
        """
        Remove a previously added close callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self._close_callbacks:
            self._close_callbacks.remove(callback)
            
    def _on_window_close(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event from Qt
        """
        # Call all registered close callbacks
        for callback in self._close_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in close callback: {e}")
        
        # Stop the timer
        self.stop()
        
        # Accept the close event
        event.accept()
            
    def start(self):
        """Start the real-time plotting."""
        self.timer.start(self.update_interval)
        self.win.show()
        
    def stop(self):
        """Stop the real-time plotting."""
        self.timer.stop()
        
    def show(self):
        """Show the plot window."""
        self.win.show()
        
    def hide(self):
        """Hide the plot window."""
        self.win.hide()
        
    def close(self):
        """Close the plot window and clean up resources."""
        self.stop()
        self.win.close()
        
    def run(self):
        """
        Run the Qt application main loop.
        
        Note: This is a blocking call. Use this when the plotter is the main component
        of your application. For integration with other async code, use start() instead.
        """
        self.start()
        return self.app.exec()
        
    def get_current_data(self, channel_idx: int) -> np.ndarray:
        """
        Get the current data buffer for a specific channel.
        
        Args:
            channel_idx: Index of the channel
            
        Returns:
            Current data as numpy array
        """
        if 0 <= channel_idx < self.num_channels:
            with self._data_lock:
                return np.array(self.data_buffers[channel_idx])
        return np.array([])
        
    def get_all_current_data(self) -> List[np.ndarray]:
        """
        Get current data buffers for all channels.
        
        Returns:
            List of numpy arrays, one for each channel
        """
        with self._data_lock:
            return [np.array(buffer) for buffer in self.data_buffers]
            
    def set_channel_name(self, channel_idx: int, name: str):
        """
        Update the name of a specific channel.
        
        Args:
            channel_idx: Index of the channel
            name: New name for the channel
        """
        if 0 <= channel_idx < self.num_channels:
            self.channel_names[channel_idx] = name
            # Update the group box title
            group_box = self.layout.itemAt(channel_idx).widget()
            if isinstance(group_box, QtWidgets.QGroupBox):
                group_box.setTitle(name)
                
    def set_update_interval(self, interval_ms: int):
        """
        Change the plot update interval.
        
        Args:
            interval_ms: New update interval in milliseconds
        """
        self.update_interval = interval_ms
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(interval_ms)