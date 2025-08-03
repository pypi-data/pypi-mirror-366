from math import log10
import numpy as np
import matplotlib.pyplot as plt
from typing import List
import json
import argparse


def plot_benchmarks(json_paths: List[str], names: List[str], font_size: int = 15, output_path: str = None, titles: bool = False) -> None:
    """
    Create multiple bar plots of benchmark results with shared x-axis.

    Args:
        json_paths: List of paths to JSON files containing benchmark results
        names: List of names in the order they should appear on the plot
        font_size: Base font size for the plot (default: 15)
        output_path: Optional path to save the plot. If None, no plot is saved (default: None)
        titles: Whether to use the JSON file names as titles for the subplots (default: False)

    Examples:
        >>> results_dir = "/path/to/results"
        >>> json_paths = [
        ...     results_dir + "/bed_chr22.json",
        ...     results_dir + "/pgen_chr22.json",
        ...     results_dir + "/vcf_chr22.json"
        ... ]
        >>> names = ["snputils", "pgenlib", "pysnptools", "sgkit", "plinkio",
        ...          "scikit-allel", "pandas-plink", "cyvcf2", "pysam"]
        >>> plot_benchmarks(json_paths, names=names, output_path='benchmark.png', titles=True)
    """
    # Set font sizes
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': font_size,
        'axes.titlesize': font_size * 1.5,
        'axes.labelsize': font_size * 1.1,
        'xtick.labelsize': font_size * 1.1,
        'ytick.labelsize': font_size,
        'figure.dpi': 300,
    })

    # Create figure with subplots
    fig, axs = plt.subplots(len(json_paths), 1, figsize=(15, 3*len(json_paths)), sharex=True)
    if len(json_paths) == 1:
        axs = [axs]

    # Common plotting parameters
    bar_width = 0.8
    bar_color = '#4C72B0'
    marker_color = '#C44E52'

    # Process each JSON file
    for ax_idx, (json_path, ax) in enumerate(zip(json_paths, axs)):
        # Read and parse JSON
        with open(json_path) as f:
            data = json.load(f)

        # Extract benchmark data
        benchmarks = {}
        for bench in data['benchmarks']:
            name = bench['params']['name']
            mean = bench['stats']['mean']
            std = bench['stats']['stddev']
            benchmarks[name] = {'mean': mean, 'std': std}

        # Create arrays for plotting
        means = []
        stds = []
        has_data = []
        for name in names:
            if name in benchmarks:
                means.append(benchmarks[name]['mean'])
                stds.append(benchmarks[name]['std'])
                has_data.append(True)
            else:
                means.append(0)
                stds.append(0)
                has_data.append(False)

        # Calculate threshold for cropping
        valid_means = [m for m, h in zip(means, has_data) if h and m > 0]
        if valid_means:
            min_val = min(valid_means)
            y_max = min_val * 20
        else:
            y_max = 1

        # Plot bars
        for i, (mean, std, has_benchmark) in enumerate(zip(means, stds, has_data)):
            if has_benchmark:
                label = f'{mean:.2f}s'
                if mean > 60:  # Minute conversion
                    minutes = int(mean // 60)
                    seconds = int(mean % 60)
                    label = f'{minutes}m{seconds}s'
                if mean > y_max:
                    # For cropped bars
                    ax.bar(i, y_max, bar_width, color=bar_color)
                    ax.text(i, y_max*0.85, '↑' * (int(log10(mean)) - int(log10(min_val))),
                            ha='center', va='bottom', color='white', fontsize=font_size * 1.5)
                    ax.text(i, y_max*0.75, label,
                            ha='center', va='bottom', fontsize=font_size, color='white')
                else:
                    ax.bar(i, mean, bar_width,
                           yerr=std, ecolor='black', capsize=5, color=bar_color)
                    ax.text(i, mean + std, label,
                            ha='center', va='bottom', fontsize=font_size)
            else:
                markersize = font_size * 1.5
                ax.plot(i, y_max/10, 'x', color=marker_color, markersize=markersize, mew=3)

        # Customize subplot
        ax.set_ylabel('Time (seconds)')
        ax.set_ylim(0, y_max)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        if titles:
            # Add file name as title (extract format from filename)
            format_name = json_path.split('/')[-1].split('.json')[0].upper().replace('_', ' ')
            ax.set_title(format_name)

    axs[-1].set_xticks(np.arange(len(names)))  # Set common x-axis
    text_objects = axs[-1].set_xticklabels(names)  # Set x-tick labels
    text_objects[0].set_fontweight('bold')  # Make first column x-tick label bold

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.show()
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Create benchmark plots from JSON files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python plot_benchmarks.py \\
        --json-paths results/bed_chr22.json results/pgen_chr22.json results/vcf_chr22.json \\
        --names snputils pgenlib pysnptools sgkit plinkio scikit-allel pandas-plink cyvcf2 pysam \\
        --output benchmark.png \\
        --titles
        """
    )

    parser.add_argument(
        '--json-paths',
        required=True,
        nargs='+',
        help='Paths to JSON files containing benchmark results'
    )

    parser.add_argument(
        '--names',
        required=True,
        nargs='+',
        help='Names to appear on the plot in order'
    )

    parser.add_argument(
        '--font-size',
        type=int,
        default=15,
        help='Base font size for the plot (default: 15)'
    )

    parser.add_argument(
        '--output',
        help='Path to save the plot (if not specified, plot will only be displayed)'
    )

    parser.add_argument(
        '--titles',
        action='store_true',
        help='Use JSON file names as subplot titles'
    )

    args = parser.parse_args()

    plot_benchmarks(
        json_paths=args.json_paths,
        names=args.names,
        font_size=args.font_size,
        output_path=args.output,
        titles=args.titles
    )


if __name__ == '__main__':
    main()
