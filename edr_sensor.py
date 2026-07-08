import math
import os

def calculate_shannon_entropy(file_path):
    """
    Reads a file and calculates its Shannon Entropy to detect encryption.
    Returns a float between 0.0 and 8.0.
    """
    try:
        # Read the file as raw binary bytes
        with open(file_path, 'rb') as f:
            byte_data = f.read()
            
        data_length = len(byte_data)
        
        # If the file is empty, entropy is 0
        if data_length == 0:
            return 0.0
            
        # Create a dictionary to count the frequency of each byte (0-255)
        byte_frequencies = {}
        for byte in byte_data:
            byte_frequencies[byte] = byte_frequencies.get(byte, 0) + 1
            
        # Calculate the Shannon Entropy
        entropy = 0.0
        for count in byte_frequencies.values():
            # Calculate the probability of this byte P(x)
            probability = count / data_length
            # Apply the formula: -P(x) * log2(P(x))
            entropy -= probability * math.log2(probability)
            
        return entropy

    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return 0.0

# --- Test the Sensor ---
if __name__ == "__main__":
    # Create a quick dummy file to test standard text
    test_file = "test_normal.txt"
    with open(test_file, "w") as f:
        f.write("This is a normal text file with low randomness. " * 50)
        
    score = calculate_shannon_entropy(test_file)
    print(f"[*] Entropy Score for readable text: {score:.4f}")
    
    # In a real scenario, an AES encrypted file would score ~7.99
    
    # Cleanup
    os.remove(test_file)
