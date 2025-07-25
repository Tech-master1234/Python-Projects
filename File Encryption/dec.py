import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging

# Set up logging for error handling and progress tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    # Ask the user for the key file path
    key_path = input("Enter the path to the key file (e.g., 'key.key'): ").strip()
    if not os.path.exists(key_path):  # Validate key file existence
        print(f"The key file '{key_path}' does not exist. Exiting...")
        exit()

    # Load the AES key from the key file
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    print(f"Loaded AES key from '{key_path}'.")

    # Define the input folder (encrypted files)
    input_folder = input("Enter the folder path containing encrypted files: ").strip()
    if not os.path.exists(input_folder):  # Ensure the input folder exists
        print(f"The folder '{input_folder}' does not exist. Exiting...")
        exit()
    elif not os.listdir(input_folder):  # Check if the folder contains files
        print(f"The folder '{input_folder}' is empty. Exiting...")
        exit()

    # Ask the user for the output folder or default to 'Decrypted' in the current working directory
    output_folder = input("Enter the output folder path (leave blank for './Decrypted'): ").strip()
    if not output_folder:  # Default to 'Decrypted' in the current directory
        output_folder = os.path.join(os.getcwd(), "Decrypted")

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Created output folder: {output_folder}")

    # Decrypt each file in the input folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):  # Process only files
            try:
                with open(file_path, "rb") as encrypted_file:
                    encrypted_data = encrypted_file.read()

                # Extract the IV (first 16 bytes) and the encrypted data
                iv = encrypted_data[:16]
                actual_encrypted_data = encrypted_data[16:]

                # Initialize AES cipher for decryption
                cipher = AES.new(key, AES.MODE_CBC, iv)

                # Decrypt and unpad the data
                decrypted_data = unpad(cipher.decrypt(actual_encrypted_data), AES.block_size)

                # Save the decrypted file to the output folder
                decrypted_file_path = os.path.join(output_folder, filename)
                with open(decrypted_file_path, "wb") as decrypted_file:
                    decrypted_file.write(decrypted_data)

                logging.info(f"Decrypted file '{filename}' and saved to '{decrypted_file_path}'")
            except Exception as e:
                logging.error(f"Failed to decrypt file '{filename}': {e}")

    print(f"All files have been decrypted and saved in the folder: {output_folder}")

except Exception as e:
    logging.error(f"An error occurred: {e}")
    print("The script encountered an error and exited.")
