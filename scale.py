#!/usr/bin/env python3

# BSD 3-Clause License
#
# Copyright (c) 2023
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse

import tqdm
from PIL import Image, ImageDraw


def scale_image(image_path, frames, output_dir):
    # Open the original image
    original_image = Image.open(image_path)
    width, height = original_image.size

    # Create a white background
    background = Image.new("RGB", (width, height), "white")

    for i in tqdm.tqdm(range(frames)):
        # Calculate scaling factor
        factor = 1 - (i / frames)

        # Calculate new dimensions
        new_width = int(width * factor)
        new_height = int(height * factor)

        # Resize the image
        resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Create a new frame with white background
        frame = background.copy()

        # Calculate the position to paste the scaled image
        paste_x = (width - new_width) // 2
        paste_y = (height - new_height) // 2

        # Paste the resized image onto the frame
        frame.paste(resized_image, (paste_x, paste_y))

        # Save the frame
        frame.save(f"{output_dir}/{i:05}.png")


if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Scale down an image into frames")

    # Add arguments
    parser.add_argument("image_path", type=str, help="Path to the PNG image file")
    parser.add_argument("frames", type=int, help="Number of frames to generate")
    parser.add_argument("output_dir", type=str, help="Directory to save the generated frames")

    # Parse arguments
    args = parser.parse_args()

    # Call the scale_image function
    scale_image(args.image_path, args.frames, args.output_dir)
