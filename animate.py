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
import os
import sys

import numpy as np
import pygame
import pygame.surfarray as surfarray

# ffmpeg -i "gif-frames/%05d.png" -filter_complex "[0]split[a][b]; [a]palettegen[palette]; [b][palette]paletteuse" -y output.gif

def is_green_pixel(r, g, b):
    threshold = 25  # Adjust as needed for best results
    avg_non_green = (r + b) / 2.0
    return g - avg_non_green > threshold


def npz_to_surfaces(npz, max_steps=1e6):
    size = 360
    if npz:
        chips = np.array(np.load(npz).get("chips"))
        chips = (
            np.clip(chips[:, [3, 2, 1], :, :], 0, 2500)
            .transpose(0, 2, 3, 1)
            .astype(np.float32)
        )
        chips /= 2500
        surfaces = []
        steps, _, _, _ = chips.shape
        for i in range(min(steps, max_steps)):
            chip = chips[i]
            chip = np.mean(chip, axis=2)
            chip = (chip * 0xFF).astype(np.uint8)
            loaded_a = surfarray.make_surface(np.stack([chip] * 3, axis=2))
            img_a = pygame.transform.scale(loaded_a, (360, 360))
            surfaces.append(img_a)
        return surfaces
    else:
        img_a = pygame.Surface((360, 360))
        img_a.fill((255, 0, 0))
        img_a = [img_a]
        return img_a


def animate(object_as, object_b, object_cs=None, output_dir=None):
    # Initialize pygame
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Load or create default object B
    if object_b:
        loaded_b = pygame.image.load(object_b)
        loaded_b.lock()
        for x in range(loaded_b.get_width()):
            for y in range(loaded_b.get_height()):
                r, g, b, a = loaded_b.get_at((x, y))
                if is_green_pixel(r, g, b):
                    loaded_b.set_at((x, y), (r, g, b, 0))
        loaded_b.unlock()
        img_b = pygame.transform.scale(loaded_b, (810, 810))
    else:
        img_b = pygame.Surface((810, 810))
        img_b.fill((0, 255, 0))

    # Ensure the output directory exists
    if output_dir is not None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    frame_number = 0
    clock = pygame.time.Clock()

    if min(len(object_as), len(object_cs)) > 0:
        pairs = zip(object_as, object_cs)
    else:
        pairs = [(None, None)]

    for object_a, object_c in pairs:
        # Load or create default object A
        img_a = npz_to_surfaces(object_a)

        # Load or create default object C
        if object_c:
            loaded_c = pygame.image.load(object_c)
            loaded_c.lock()
            for x in range(loaded_c.get_width()):
                for y in range(loaded_c.get_height()):
                    r, g, b, a = loaded_c.get_at((x, y))
                    if is_green_pixel(r, g, b):
                        loaded_c.set_at((x, y), (r, g, b, 0))
            loaded_c.unlock()
            img_c = pygame.transform.scale(loaded_c, (270, 270))
        else:
            img_c = pygame.Surface((270, 270))
            img_c.fill((0, 0, 255))

        # Set initial positions
        pos_a = [-360, 360]  # Start from the left off-screen
        pos_b = [555, 135]  # Center of the screen
        pos_c = [825, 405]  # Behind the center object

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Move object A from left to right until it's behind object B
            if pos_a[0] < 780:
                pos_a[0] += 13  # Speed

            # Once object A is behind object B, move object C from left to right
            elif pos_c[0] < 1920:  # Until it's off-screen to the right
                pos_c[0] += 13  # Speed

            # If object C is off-screen, break for the next A + B pair
            else:
                break

            # Draw
            _img_a = img_a[(frame_number // 15) % len(img_a)]
            screen.fill((255, 255, 255))  # White background
            if pos_a[0] < 780:
                screen.blit(_img_a, pos_a)
            elif pos_c[0] < 1920:
                screen.blit(img_c, pos_c)
            screen.blit(img_b, pos_b)

            pygame.display.flip()

            # Save the frame
            if output_dir is not None:
                pygame.image.save(screen, os.path.join(output_dir, f"{frame_number:05}.png"))
            frame_number += 1

            clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Animate lists of objects A's and B's with object C.")
    parser.add_argument("--object_as", nargs='*', help="List of paths to the NPZs for object Ass (360x360 each)", default=[])
    parser.add_argument("--object_b", help="Path to the PNG for object B (810x810)", default=None)
    parser.add_argument("--object_cs", nargs='*', help="List of paths to the PNGs for object Cs (270x270 each)", default=[])
    parser.add_argument("--output-dir", type=str, help="Where to store the generated frames", default=None)
    args = parser.parse_args()

    animate(args.object_as, args.object_b, args.object_cs, args.output_dir)
