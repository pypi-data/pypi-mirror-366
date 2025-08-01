#!/usr/bin/env python3
import time
import os
import argparse

notes_freq = {
    'G4': 392,
    'A4': 440,
    'B4': 494,
    'C5': 523,
    'D5': 587,
    'E5': 659,
    'F5': 698,
    'G5': 784,
}

def song(fast=False, name="person"):

    speed = 0.01 if fast else 0.15

    notes = [
        ('G4', 300, " Ha"),
        ('G4', 300, "ppy "),
        ('A4', 600, "birth"),
        ('G4', 600, "day "),
        ('C5', 600, "to "),
        ('B4', 900, "you!\n"),

        ('G4', 300, " Ha"),
        ('G4', 300, "ppy "),
        ('A4', 600, "birth"),
        ('G4', 600, "day "),
        ('D5', 600, "to "),
        ('C5', 900, "you!\n"),

        ('G4', 300, " Ha"),
        ('G4', 300, "ppy "),
        ('G5', 600, "birth"),
        ('E5', 600, "day "),
        ('C5', 600, "dear "),
        ('B4', 600, f"{name}"),
        ('A4', 900, "..\n"),

        ('F5', 450, " Ha"),
        ('F5', 450, "ppy "),
        ('E5', 600, "birth"),
        ('C5', 600, "day "),
        ('D5', 600, "to "),
        ('C5', 900, "you! \n"),
    ]

    for note, duration, syllable in notes:
        duration = duration * 0.4 if fast else duration
        if syllable:
            print(syllable, end='', flush=True)
        freq = notes_freq[note]
        os.system(f"beep -f {freq} -l {duration}")
        time.sleep(duration / 1000 * speed)

def main():
    parser = argparse.ArgumentParser(description="Play Happy Birthday tune on Linux terminal beep.")
    parser.add_argument("-f", "--fast", action="store_true", help="Play faster version")
    parser.add_argument("name", nargs="?", default="person", help="Name of the birthday person")
    args = parser.parse_args()

    print("\n")
    song(fast=args.fast, name=args.name)
    print("\n")

if __name__ == "__main__":
    main()

