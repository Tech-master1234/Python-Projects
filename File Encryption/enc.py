import os
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import logging

# Set up logging for error handling and progress tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    # Ask the user for a key file name
    key_name = input("Enter the key file name (with extension, e.g., 'key.key') or leave blank: ").strip()
    if not key_name:  # If no key name is provided, generate one based on the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        key_name = f"key_{current_time}.key"

    key_path = input("Enter the key file path (leave blank to save in the current working directory): ").strip()
    if not key_path:  # Default to saving in the current working directory
        key_path = os.path.join(os.getcwd(), key_name)
    else:
        key_path = os.path.join(key_path, key_name)

    # Check if the key file already exists to avoid overwriting
    if os.path.exists(key_path):
        overwrite = input(f"The key file '{key_path}' already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Exiting without creating a key.")
            exit()

    # Generate a random AES key (32 bytes for 256-bit encryption)
    key = get_random_bytes(32)
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    print(f"A 256-bit AES key has been generated and saved as '{key_path}'.")

    # Define input folder
    input_folder = input("Enter the input folder path (files to encrypt): ").strip()
    if not os.path.exists(input_folder):  # Ensure the input folder exists
        print(f"The input folder '{input_folder}' does not exist. Exiting...")
        exit()
    elif not os.listdir(input_folder):  # Check if the folder contains files
        print(f"The input folder '{input_folder}' is empty. Exiting...")
        exit()

    # Ask the user for an output folder or default to 'Encrypted' in the current working directory
    output_folder = input("Enter the output folder path (leave blank for './Encrypted'): ").strip()
    if not output_folder:  # Default to 'Encrypted' in the current directory
        output_folder = os.path.join(os.getcwd(), "Encrypted")

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Created output folder: {output_folder}")

    # Encrypt each file in the input folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):  # Process only files
            try:
                with open(file_path, "rb") as file:
                    file_data = file.read()

                # Initialize AES cipher in CBC mode
                cipher = AES.new(key, AES.MODE_CBC)
                iv = cipher.iv  # Initialization vector

                # Encrypt the data
                encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

                # Save the encrypted file with IV prepended
                encrypted_file_path = os.path.join(output_folder, filename)
                with open(encrypted_file_path, "wb") as encrypted_file:
                    encrypted_file.write(iv + encrypted_data)

                logging.info(f"Encrypted file '{filename}' and saved to '{encrypted_file_path}'")
            except Exception as e:
                logging.error(f"Failed to encrypt file '{filename}': {e}")

    print(f"All files have been encrypted and saved in the folder: {output_folder}")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    print("The script encountered an error and exited.")

