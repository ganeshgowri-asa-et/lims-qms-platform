"""
Graph Generation Service for Test Reports
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime


class GraphGenerator:
    """Generate graphs for IEC test reports"""

    def __init__(self, output_dir: str = "reports/graphs", dpi: int = 300):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def generate_iv_curve(
        self,
        voltage_data: List[float],
        current_data: List[float],
        output_filename: str,
        title: str = "I-V Characteristic Curve",
        show_mpp: bool = True
    ) -> str:
        """
        Generate I-V (Current-Voltage) characteristic curve

        Args:
            voltage_data: List of voltage measurements
            current_data: List of current measurements
            output_filename: Name of output file
            title: Graph title
            show_mpp: Show maximum power point marker

        Returns:
            Path to generated graph
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot I-V curve
        ax.plot(voltage_data, current_data, 'b-', linewidth=2, label='I-V Curve')

        # Find and mark maximum power point if requested
        if show_mpp and len(voltage_data) == len(current_data):
            power = np.array(voltage_data) * np.array(current_data)
            mpp_idx = np.argmax(power)
            ax.plot(voltage_data[mpp_idx], current_data[mpp_idx], 'ro',
                   markersize=10, label=f'MPP: {voltage_data[mpp_idx]:.2f}V, {current_data[mpp_idx]:.2f}A')

        ax.set_xlabel('Voltage (V)', fontsize=12)
        ax.set_ylabel('Current (A)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_power_curve(
        self,
        voltage_data: List[float],
        current_data: List[float],
        output_filename: str,
        title: str = "P-V Power Curve"
    ) -> str:
        """
        Generate P-V (Power-Voltage) curve

        Args:
            voltage_data: List of voltage measurements
            current_data: List of current measurements
            output_filename: Name of output file
            title: Graph title

        Returns:
            Path to generated graph
        """
        # Calculate power
        power_data = np.array(voltage_data) * np.array(current_data)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot P-V curve
        ax.plot(voltage_data, power_data, 'r-', linewidth=2, label='P-V Curve')

        # Mark maximum power point
        mpp_idx = np.argmax(power_data)
        ax.plot(voltage_data[mpp_idx], power_data[mpp_idx], 'go',
               markersize=10, label=f'Pmax: {power_data[mpp_idx]:.2f}W')

        ax.set_xlabel('Voltage (V)', fontsize=12)
        ax.set_ylabel('Power (W)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_temperature_profile(
        self,
        time_data: List[datetime],
        temperature_data: List[float],
        output_filename: str,
        title: str = "Temperature Profile",
        threshold: Optional[float] = None
    ) -> str:
        """
        Generate temperature vs time profile

        Args:
            time_data: List of timestamps
            temperature_data: List of temperature measurements
            output_filename: Name of output file
            title: Graph title
            threshold: Optional temperature threshold line

        Returns:
            Path to generated graph
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot temperature profile
        ax.plot(time_data, temperature_data, 'b-', linewidth=2, label='Temperature')

        # Add threshold line if provided
        if threshold is not None:
            ax.axhline(y=threshold, color='r', linestyle='--',
                      linewidth=2, label=f'Threshold: {threshold}°C')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_degradation_chart(
        self,
        test_names: List[str],
        degradation_values: List[float],
        output_filename: str,
        title: str = "Power Degradation Analysis",
        limit: float = 5.0
    ) -> str:
        """
        Generate degradation comparison chart

        Args:
            test_names: List of test names
            degradation_values: List of degradation percentages
            output_filename: Name of output file
            title: Graph title
            limit: Acceptable degradation limit (%)

        Returns:
            Path to generated graph
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bar chart
        colors = ['green' if abs(v) <= limit else 'red' for v in degradation_values]
        bars = ax.bar(test_names, degradation_values, color=colors, alpha=0.7)

        # Add limit line
        ax.axhline(y=limit, color='orange', linestyle='--',
                  linewidth=2, label=f'Acceptance Limit: ±{limit}%')
        ax.axhline(y=-limit, color='orange', linestyle='--', linewidth=2)

        # Add value labels on bars
        for bar, value in zip(bars, degradation_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.2f}%',
                   ha='center', va='bottom' if height > 0 else 'top')

        ax.set_xlabel('Test', fontsize=12)
        ax.set_ylabel('Power Degradation (%)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()
        plt.xticks(rotation=45, ha='right')

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_time_series_plot(
        self,
        data_points: List[Dict[str, Any]],
        output_filename: str,
        x_key: str,
        y_keys: List[str],
        title: str = "Time Series Data",
        x_label: str = "Time",
        y_label: str = "Value"
    ) -> str:
        """
        Generate generic time series plot from data points

        Args:
            data_points: List of data point dictionaries
            output_filename: Name of output file
            x_key: Key for x-axis data
            y_keys: List of keys for y-axis data
            title: Graph title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Path to generated graph
        """
        df = pd.DataFrame(data_points)

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each y-key as separate line
        for y_key in y_keys:
            if y_key in df.columns:
                ax.plot(df[x_key], df[y_key], marker='o',
                       linewidth=2, label=y_key)

        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_interactive_iv_curve(
        self,
        voltage_data: List[float],
        current_data: List[float],
        output_filename: str,
        title: str = "Interactive I-V Curve"
    ) -> str:
        """
        Generate interactive I-V curve using Plotly

        Args:
            voltage_data: List of voltage measurements
            current_data: List of current measurements
            output_filename: Name of output file
            title: Graph title

        Returns:
            Path to generated HTML file
        """
        # Calculate power
        power_data = np.array(voltage_data) * np.array(current_data)

        # Create figure with secondary y-axis
        fig = go.Figure()

        # Add I-V curve
        fig.add_trace(go.Scatter(
            x=voltage_data,
            y=current_data,
            mode='lines+markers',
            name='Current',
            line=dict(color='blue', width=3),
            yaxis='y1'
        ))

        # Add P-V curve
        fig.add_trace(go.Scatter(
            x=voltage_data,
            y=power_data,
            mode='lines+markers',
            name='Power',
            line=dict(color='red', width=3),
            yaxis='y2'
        ))

        # Update layout
        fig.update_layout(
            title=title,
            xaxis=dict(title='Voltage (V)'),
            yaxis=dict(title='Current (A)', side='left'),
            yaxis2=dict(title='Power (W)', side='right', overlaying='y'),
            hovermode='x unified',
            template='plotly_white'
        )

        # Save as HTML
        output_path = self.output_dir / output_filename
        fig.write_html(output_path)

        return str(output_path)

    def generate_comparison_chart(
        self,
        categories: List[str],
        series_data: Dict[str, List[float]],
        output_filename: str,
        title: str = "Comparison Chart",
        y_label: str = "Value"
    ) -> str:
        """
        Generate grouped bar chart for comparison

        Args:
            categories: List of category names
            series_data: Dictionary of series_name: [values]
            output_filename: Name of output file
            title: Graph title
            y_label: Y-axis label

        Returns:
            Path to generated graph
        """
        x = np.arange(len(categories))
        width = 0.8 / len(series_data)

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each series
        for i, (series_name, values) in enumerate(series_data.items()):
            offset = width * i - (width * len(series_data) / 2 - width / 2)
            ax.bar(x + offset, values, width, label=series_name, alpha=0.8)

        ax.set_xlabel('Category', fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Save figure
        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)
