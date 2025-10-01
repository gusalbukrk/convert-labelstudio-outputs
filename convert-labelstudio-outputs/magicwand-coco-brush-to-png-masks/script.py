import numpy as np
from PIL import Image
import os
import re
from typing import List, Dict, Optional
import json

def generate_composite_mask_png(npy_paths: List[str], png_path: str) -> Optional[str]:
    """
    Loads multiple NumPy brush mask arrays (H, W) and combines them into 
    a single master mask, saving it as a single-channel 8-bit grayscale PNG.
    """
    if not npy_paths:
        print("  Error: Input list of NPY paths is empty.")
        return None
        
    master_mask = None

    for npy_path in npy_paths:
        try:
            current_mask = np.load(npy_path)
        except Exception:
            # print(f"  Warning: Error loading {os.path.basename(npy_path)}. Skipping.")
            continue

        if current_mask.ndim != 2:
            # print(f"  Warning: Expected 2D array, got {current_mask.ndim} for {os.path.basename(npy_path)}. Skipping.")
            continue

        if master_mask is None:
            master_mask = current_mask
        else:
            if master_mask.shape != current_mask.shape:
                # print(f"  Warning: Mask shapes mismatch ({master_mask.shape} vs {current_mask.shape}) for {os.path.basename(npy_path)}. Skipping.")
                continue
                
            # Combine masks using np.maximum, which performs a logical OR on binary masks
            master_mask = np.maximum(master_mask, current_mask)
            
    if master_mask is None:
        return None

    master_mask = master_mask.astype(np.uint8)
    
    # Scale binary mask (0 or 1) to (0 or 255) for visibility
    if np.max(master_mask) <= 1:
        mask_array_scaled = master_mask * 255
    else:
        mask_array_scaled = master_mask
        
    try:
        # Use 'L' mode for 8-bit grayscale
        mask_image = Image.fromarray(mask_array_scaled, mode='L')
        mask_image.save(png_path)
        return os.path.abspath(png_path)
    except Exception as e:
        print(f"  An error occurred while saving the image: {e}")
        return None

def batch_process_masks(input_directory: str, output_directory: Optional[str] = None):
    """
    Scans a directory for NPY mask files, groups them by their shared annotation ID,
    and generates a composite PNG mask for each group.
    """
    input_directory = os.path.abspath(input_directory)

    if not os.path.isdir(input_directory):
        print(f"Error: Input directory not found: {input_directory}")
        return

    if output_directory is None:
        output_directory = input_directory
    else:
        output_directory = os.path.abspath(output_directory)
        os.makedirs(output_directory, exist_ok=True)

    print(f"Scanning directory: {input_directory}")
    print(f"Output directory for PNG masks: {output_directory}\n")

    grouped_npy_files: Dict[str, List[str]] = {}

    # Regex to group files by everything before the final group index: -<INDEX>.npy
    # Key includes: task-ID-annotation-ID-by-USER_ID-labels-LABEL_NAME
    filename_pattern = re.compile(r"^(task-\d+-annotation-\d+-by-\d+-labels-[A-Za-z0-9_]+)-\d+\.npy$")

    for filename in os.listdir(input_directory):
        if filename.endswith('.npy'):
            full_path = os.path.join(input_directory, filename)
            match = filename_pattern.match(filename)
            
            if match:
                group_key = match.group(1)
                if group_key not in grouped_npy_files:
                    grouped_npy_files[group_key] = []
                grouped_npy_files[group_key].append(full_path)
            # else:
            #     print(f"Warning: Filename '{filename}' does not match expected Label Studio pattern and will be skipped.")

    if not grouped_npy_files:
        print("No NPY files matching the expected Label Studio pattern were found in the directory.")
        return

    processed_count = 0
    total_groups = len(grouped_npy_files)
    
    for i, (group_key, npy_files) in enumerate(grouped_npy_files.items()):
        task_id = group_key.split('-')[1]

        # output_png_filename = f"{group_key}_composite_mask.png"
        output_png_filename = f"{task_id}.png"
        output_png_path = os.path.join(output_directory, output_png_filename)

        print(f"[{i + 1}/{total_groups}] Processing group '{group_key}' ({len(npy_files)} files)")
        
        if generate_composite_mask_png(npy_files, output_png_path):
            print(f"  ✅ Saved: {os.path.basename(output_png_path)}")
            processed_count += 1
        
        if i < total_groups - 1:
             print("-" * 30)

    print(f"\nBatch processing complete. Generated {processed_count} composite PNG masks.")

def get_filename_mapping(json_file_path: str) -> Optional[Dict[str, str]]:
    """
    Reads the Label Studio JSON export file and creates a map from 
    Task ID to the original image filename.
    
    Returns:
        Dict[str, str]: A dictionary mapping Task ID (string) to Image Filename (string).
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON file at {json_file_path}. Check file format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the JSON: {e}")
        return None

    mapping = {}
    
    # Iterate over every child/task in the main JSON array
    for task in data:
        task_id = str(task.get("id"))
        image_path = task.get("image", "")
        
        # Ensure both keys exist and image path is not empty
        if task_id and image_path:
            # Extract the filename from the full path (e.g., '/data/upload/../image.jpg' -> 'image.jpg')
            filename = os.path.basename(image_path)
            mapping[task_id] = filename
            
    return mapping

def rename_masks(mask_directory: str, mapping: Dict[str, str]):
    """
    Iterates over PNG files in the mask directory and renames them using the mapping.
    The script assumes mask files are named by Task ID (e.g., '91.png').
    """
    mask_directory = os.path.abspath(mask_directory)
    renamed_count = 0
    
    if not os.path.isdir(mask_directory):
        print(f"Error: Mask directory not found: {mask_directory}")
        return

    print(f"\n--- Starting Renaming in directory: {mask_directory} ---")
    
    for filename in os.listdir(mask_directory):
        if filename.endswith('.png'):
            # Current filename is assumed to be the Task ID, e.g., '91.png'
            task_id, _ = os.path.splitext(filename)
            
            if task_id in mapping:
                original_filename_base = mapping[task_id]
                
                # New filename format: [Original Image Name] + ".png"
                new_filename = original_filename_base + ".png"
                
                old_path = os.path.join(mask_directory, filename)
                new_path = os.path.join(mask_directory, new_filename)
                
                if old_path == new_path:
                    # File is already named correctly or has the same base name
                    continue
                
                try:
                    os.rename(old_path, new_path)
                    print(f"  Renamed '{filename}' to '{new_filename}'")
                    renamed_count += 1
                except FileExistsError:
                    print(f"  Warning: Target file '{new_filename}' already exists. Skipping rename for '{filename}'.")
                except Exception as e:
                    print(f"  Error renaming {filename}: {e}")
            else:
                print(f"  Warning: Task ID '{task_id}' not found in JSON mapping. Skipping '{filename}'.")

    print(f"\n--- Renaming complete. {renamed_count} PNG masks renamed. ---")

if __name__ == '__main__':
    # =========================================================
    # 💡 USER CONFIGURATION SECTION - EDIT THESE VARIABLES
    # =========================================================
    
    # Path to the directory containing your exported NPY files.
    INPUT_DIR = './input' 

    # Optional: Path to the directory to save the output PNG masks.
    # Set to None to save the PNGs in the same directory as the NPY files.
    OUTPUT_DIR = './output' 
    
    # =========================================================
    
    batch_process_masks(INPUT_DIR, OUTPUT_DIR)

    # Path to your Label Studio exported JSON file (e.g., 'exported.json').
    JSON_FILE_PATH = './exported.json' 
    
    # =========================================================
    
    # Step 1: Create the ID-to-Filename mapping from the JSON
    filename_map = get_filename_mapping(JSON_FILE_PATH)
    
    # Step 2: Rename the generated masks
    if filename_map:
        rename_masks(OUTPUT_DIR, filename_map)
    else:
        print("Skipping renaming step due to missing or invalid JSON mapping.")