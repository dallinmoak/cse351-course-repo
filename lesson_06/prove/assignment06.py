"""
Course: CSE 351
Assignment: 06
Author: Dallin Moak

Instructions:

- see instructions in the assignment description in Canvas

"""

import multiprocessing as mp
import os
import cv2
import numpy as np

import math

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
def worker_smooth_image(input_queue, output_queue, kernel_size):
    while True:
        img = input_queue.get()
        if img is None:
            print("smoothing worker received termination signal")
            output_queue.put(None)
            break
        smoothed_img = task_smooth_image(img[1], kernel_size)
        output_queue.put((img[0], smoothed_img))


# ---------------------------------------------------------------------------
def worker_grayscale_image(input_queue, output_queue, downsample_factor):
    while True:
        img = input_queue.get()
        if img is None:
            print(
                f"grayscale worker received termination signal, forwarding {downsample_factor} termination signals"
            )
            for _ in range(int(downsample_factor)):
                output_queue.put(None)
            break
        gray_img = task_convert_to_grayscale(img[1])
        output_queue.put((img[0], gray_img))


# ---------------------------------------------------------------------------
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
def run_image_processing_pipeline(counts, queue_size_limit):
    print("Starting image processing pipeline...")

    queue_1 = mp.Queue(maxsize=queue_size_limit)
    queue_2 = mp.Queue(maxsize=queue_size_limit)
    queue_3 = mp.Queue(maxsize=queue_size_limit)

    smooth_process_count = counts[0]
    grayscale_process_count = counts[1]
    edge_process_count = counts[2]
    gray_to_edge_ratio = math.ceil(edge_process_count / grayscale_process_count)

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
            args=(queue_2, queue_3, gray_to_edge_ratio),
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
    queue_1.put(None)

    for index, p in enumerate(smooth_processes):
        print(f"sending termination signal to smooth processe {index}, {p.name}")
        queue_1.put(None)

    for p in smooth_processes + grayscale_processes + edge_processes:
        p.join()

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer("Processing Images")

    smooth_count = 1
    grayscale_count = 1
    edge_count = 2

    queue_size_limit = 3000

    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print("Link to faces.zip:")
        print(
            "   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing"
        )
    else:
        run_image_processing_pipeline((smooth_count, grayscale_count, edge_count), queue_size_limit)

    log.write(
        f"attempt with {smooth_count} smoothing and {grayscale_count} grayscale processes and {edge_count} edge processes and 3 queues of size {queue_size_limit}"
    )
    log.stop_timer("Total Time To complete")
