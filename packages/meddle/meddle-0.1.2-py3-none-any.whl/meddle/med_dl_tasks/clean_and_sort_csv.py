import csv
import os
import re


def replace_text_and_sort_csv(folder_path):
    """
    Recursively searches for CSV files in a folder, replaces a specific text pattern,
    and then sorts the CSV content by the 'id' column.

    Args:
        folder_path (str): The path to the folder to start searching from.
    """
    # Define the pattern to search for: starts with /mnt/petrelfs/liwei1/Med-MLEBench/medmnist_preprocess/
    # and captures the rest of the path.
    search_pattern = re.compile(re.escape("/mnt/petrelfs/liwei1/Med-MLEBench/medmnist_preprocess/") + r"[^/]+/(.*)")
    # search_pattern = re.compile(re.escape("mnist") + r"(.*)")

    print(f"Starting search and sort in folder: {folder_path}")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                try:
                    # --- Text Replacement Part ---
                    original_content = ""
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()

                    # Perform the replacement
                    content_after_replace = search_pattern.sub(r'input/\1', original_content)

                    # --- Sorting Part ---
                    rows = []
                    header = None
                    id_column_index = -1

                    # Use StringIO to treat the string content as a file for the csv reader
                    from io import StringIO
                    csvfile = StringIO(content_after_replace)

                    reader = csv.reader(csvfile)

                    # Read the header
                    try:
                        header = next(reader)
                        # Find the index of the 'id' column (case-insensitive search)
                        try:
                            id_column_index = [i for i, h in enumerate(header) if h.lower() == 'id'][0]
                        except IndexError:
                            print(f"Warning: 'id' column not found in header of {file_path}. Skipping sort for this file.")
                            # If 'id' column is not found, use the content after replacement directly
                            rows_to_write = content_after_replace.splitlines() # Keep as lines for writing
                            header = None # No header to handle separately during write
                            id_column_index = -1 # Ensure sort is skipped

                    except StopIteration:
                        print(f"Warning: {file_path} appears to be empty or has no header. Skipping sort.")
                        rows_to_write = [] # Nothing to write
                        header = None
                        id_column_index = -1

                    if id_column_index != -1:
                        # Read the rest of the rows
                        for row in reader:
                            rows.append(row)

                        # Sort the rows based on the 'id' column
                        # Attempt to convert ID to integer for numerical sort, fallback to string sort
                        try:
                            rows.sort(key=lambda row: int(row[id_column_index]))
                        except (ValueError, IndexError):
                             # Fallback to string sort if conversion to int fails or index is out of bounds
                             rows.sort(key=lambda row: row[id_column_index])
                        except Exception as e:
                             print(f"An error occurred during sorting {file_path}: {e}. Skipping sort.")
                             # If sorting fails, use the content after replacement directly
                             rows_to_write = content_after_replace.splitlines()
                             header = None
                             id_column_index = -1 # Ensure sort is skipped


                        # Prepare rows for writing (header + sorted rows)
                        if header:
                            rows_to_write = [header] + rows
                        else:
                             rows_to_write = rows # Should not happen if header was read, but as a fallback

                    # --- Write back to file ---
                    # Only write if content changed or sorting was performed
                    # If sorting was skipped due to errors or missing 'id', we write the content after replacement
                    if content_after_replace != original_content or id_column_index != -1:
                         print("Changes detected (text replacement or sorting), writing back to file.")
                         with open(file_path, 'w', encoding='utf-8', newline='') as f:
                            writer = csv.writer(f)
                            if id_column_index != -1:
                                # Write header and sorted rows using csv writer
                                writer.writerows(rows_to_write)
                            else:
                                # Write the content after replacement if sorting was skipped
                                f.write("\n".join(rows_to_write)) # Write lines back with newlines

                    else:
                        print("No changes needed.")


                except FileNotFoundError:
                    print(f"Error: File not found - {file_path}")
                except PermissionError:
                    print(f"Error: Permission denied to access - {file_path}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing {file_path}: {e}")

    print("Processing complete.")

# --- How to use the script ---
# Replace 'your_folder_path_here' with the actual path to your folder.
# Example usage:
# replace_text_and_sort_csv('/path/to/your/folder')

# Uncomment the line below and provide the folder path to run the script
# replace_text_and_sort_csv('./z_test')
replace_text_and_sort_csv('./')

