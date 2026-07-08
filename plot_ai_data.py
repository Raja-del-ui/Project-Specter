import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def generate_academic_plot(csv_file):
    print(f"[*] Reading telemetry data from {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"[-] Error: Could not find {csv_file}. Make sure you run an attack while the EDR is monitoring!")
        sys.exit(1)

    # Load the telemetry data
    df = pd.read_csv(csv_file)
    
    if df.empty:
        print("[-] The telemetry file is empty. Go trigger some file activity first!")
        sys.exit(1)

    # Separate normal activity (1) from attacks (-1)
    normal_data = df[df['AI_Prediction'] == 1]
    attack_data = df[df['AI_Prediction'] == -1]

    # Set up a beautiful dark-mode graph
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot normal activity (Green dots)
    ax.scatter(
        normal_data['IO_Speed'], 
        normal_data['Entropy'], 
        color='#22c55e', 
        label='Normal User Activity', 
        alpha=0.7, 
        s=100, 
        edgecolors='white'
    )

    # Plot ransomware activity (Red X's)
    ax.scatter(
        attack_data['IO_Speed'], 
        attack_data['Entropy'], 
        color='#ef4444', 
        label='Cryptographic Attack (Ransomware)', 
        marker='X', 
        s=150, 
        edgecolors='white'
    )

    # Add titles and labels
    plt.title('Isolation Forest AI: Threat Detection Boundary', fontsize=18, fontweight='bold', color='white', pad=20)
    plt.xlabel('I/O Speed (File Modifications per 5 Seconds)', fontsize=14, color='white')
    plt.ylabel('Shannon Entropy (File Randomness: 0 to 8)', fontsize=14, color='white')
    
    # Draw a visual "Danger Zone" threshold area
    ax.axhspan(7.0, 8.0, color='red', alpha=0.1)
    ax.axvspan(5, df['IO_Speed'].max() + 2, color='red', alpha=0.1)
    
    # Configure grid and legend
    ax.grid(color='#334155', linestyle='--', linewidth=1, alpha=0.5)
    legend = ax.legend(fontsize=12, loc='lower right', facecolor='#0f172a', edgecolor='#334155')
    for text in legend.get_texts():
        text.set_color("white")

    print("[+] Graph generated successfully! Close the window to exit.")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Ensure pandas and matplotlib are installed
    try:
        generate_academic_plot("edr_telemetry.csv")
    except ImportError:
        print("[-] Missing plotting libraries! Run: sudo apt install python3-pandas python3-matplotlib")
