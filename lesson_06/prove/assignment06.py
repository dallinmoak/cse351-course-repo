"""
Course: CSE 351
Assignment: 06
Author: [Your Name]

Instructions:

- see instructions in the assignment description in Canvas

"""

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = [".jpg"]


# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")


# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image  # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)


# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print(
            "Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny."
        )
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif (
        len(image.shape) == 3 and image.shape[2] != 1
    ):  # Should not happen with typical images
        print(
            f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}"
        )
        return image  # Or raise error
    return cv2.Canny(image, threshold1, threshold2)


# ---------------------------------------------------------------------------
def process_images_in_folder(
    input_folder,  # input folder with images
    output_folder,  # output folder for processed images
    processing_function,  # function to process the image (ie., task_...())
    load_args=None,  # Optional args for cv2.imread
    processing_args=None,
):  # Optional args for processing function

    create_folder_if_not_exists(output_folder)
    print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")

    processed_count = 0
    for filename in os.listdir(input_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(input_folder, filename)
        output_image_path = os.path.join(
            output_folder, filename
        )  # Keep original filename

        try:
            # Read the image
            if load_args is not None:
                img = cv2.imread(input_image_path, load_args)
            else:
                img = cv2.imread(input_image_path)

            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            # Save the processed image
            cv2.imwrite(output_image_path, processed_img)

            processed_count += 1
        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")

    print(
        f"Finished processing. {processed_count} images processed into '{output_folder}'."
    )


def worker_smooth_image(input_queue, output_queue, kernel_size):
    while True:
        img = input_queue.get()
        if img is None:
            print("smoothing worker received termination signal")
            output_queue.put(None)
            break
        smoothed_img = task_smooth_image(img[1], kernel_size)
        output_queue.put((img[0], smoothed_img))


def worker_grayscale_image(input_queue, output_queue):
    while True:
        img = input_queue.get()
        if img is None:
            print("grayscale worker received termination signal")
            output_queue.put(None)
            break
        gray_img = task_convert_to_grayscale(img[1])
        output_queue.put((img[0], gray_img))


def worker_edge_detection(input_queue, output_dir, threshold1, threshold2):
    create_folder_if_not_exists(output_dir)
    while True:
        item = input_queue.get()
        if item is None:
            print("edge detection worker received termination signal")
            break
        filename, img = item
        edges_img = task_detect_edges(img, threshold1, threshold2)
        output_image_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_image_path, edges_img)


# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")
     # Load images and put them into the first queue

    queue_1 = mp.Queue(maxsize=20)
    queue_2 = mp.Queue(maxsize=20)
    queue_3 = mp.Queue(maxsize=20)

    smooth_process_count = 1
    grayscale_process_count = 1
    edge_process_count = 1

    smooth_processes = []
    grayscale_processes = []
    edge_processes = []

    for _ in range(smooth_process_count):
        p = mp.Process(
            target=worker_smooth_image,
            args=(queue_1, queue_2, GAUSSIAN_BLUR_KERNEL_SIZE),
        )
        smooth_processes.append(p)

    for _ in range(grayscale_process_count):
        p = mp.Process(
            target=worker_grayscale_image,
            args=(queue_2, queue_3),
        )
        grayscale_processes.append(p)

    for _ in range(edge_process_count):
        p = mp.Process(
            target=worker_edge_detection,
            args=(queue_3, STEP3_OUTPUT_FOLDER, CANNY_THRESHOLD1, CANNY_THRESHOLD2),
        )
        edge_processes.append(p)

    for index, p in enumerate(smooth_processes):
        print(f"starting smooth process {index}, {p.name}")
        p.start()
    
    for index, p in enumerate(grayscale_processes):
        print(f"starting grayscale process {index}, {p.name}")
        p.start()
    
    for index, p in enumerate(edge_processes):
        print(f"starting edge process {index}, {p.name}")
        p.start()

    for filename in os.listdir(INPUT_FOLDER):
        input_image_path = os.path.join(INPUT_FOLDER, filename)
        img = cv2.imread(filename=input_image_path)
        if img is None:
            print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
            break
        if img is not None:
            queue_1.put((filename, img))
    print("All images loaded into the first queue.")
    # queue_1.put(None)

    for index, p in enumerate(smooth_processes):
        print(f"sending termination signal to smooth processe {index}, {p.name}")
        queue_1.put(None)
    for index, p in enumerate(grayscale_processes):
        print(f"sending termination signal to grayscale process {index}, {p.name}")
        queue_2.put(None)
    for index, p in enumerate(edge_processes):
        print(f"sending termination signal to edge process {index}, {p.name}")
        queue_3.put(None)

    for p in smooth_processes + grayscale_processes + edge_processes:
        p.join()

    # TODO
    # - create queues
    # - create barriers
    # - create the three processes groups
    # - you are free to change anything in the program as long as you
    #   do all requirements.

    # --- Step 1: Smooth Images ---
    # process_images_in_folder(
    #     INPUT_FOLDER,
    #     STEP1_OUTPUT_FOLDER,
    #     task_smooth_image,
    #     processing_args=(GAUSSIAN_BLUR_KERNEL_SIZE,),
    # )

    # --- Step 2: Convert to Grayscale ---
    # process_images_in_folder(
    #     STEP1_OUTPUT_FOLDER, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale
    # )

    # --- Step 3: Detect Edges ---
    # process_images_in_folder(
    #     STEP2_OUTPUT_FOLDER,
    #     STEP3_OUTPUT_FOLDER,
    #     task_detect_edges,
    #     load_args=cv2.IMREAD_GRAYSCALE,
    #     processing_args=(CANNY_THRESHOLD1, CANNY_THRESHOLD2),
    # )

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    # print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    # print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer("Processing Images")

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print("Link to faces.zip:")
        print(
            "   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing"
        )
    else:
        run_image_processing_pipeline()

    log.write("attempt with 1 process each for 3 queue setup")
    log.stop_timer("Total Time To complete")
