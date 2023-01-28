"""
Find and save the true barcodes from a list of apparent barcodes in FASTQ format
"""

import argparse
from collections import Counter
from pathlib import Path
from typing import Optional


def find_barcodes(
    input_file: Path,
    anchor: str,
    cell_count: int,
    error_hamming_distance: int,
    proportion_to_consider: float,
    output_directory: Optional[Path],
):
    """
    Takes file, anchor sequence, cell count, allowable Hamming distance for error correction,
    proportion of barcodes to consider for error correction, and optional output directory,
    saves text file of true barcodes and prints true barcode count and directory to file.
    """

    explicit_barcodes_counter = extract_barcodes(input_file, anchor)

    if error_hamming_distance > 0:
        explicit_barcodes_counter = group_by_hamming_distance(
            explicit_barcodes_counter,
            cell_count,
            error_hamming_distance,
            proportion_to_consider,
        )

    true_barcodes = get_true_barcodes(explicit_barcodes_counter, cell_count)

    write_to_file(true_barcodes, input_file, output_directory)


def extract_barcodes(input_file, anchor):
    """
    Takes filepath to a list of apparent barcodes and anchor, returns a counter of explicit
    barcode counts.
    """

    explicit_barcodes_counter = Counter()
    with open(input_file) as file:
        for line_number, line in enumerate(file):
            # check for anchor on every fourth line
            if (line_number + 3) % 4 == 0:
                anchor_index = line.find(anchor, 30)
                if anchor_index != -1:
                    barcode = line[anchor_index - 30 : anchor_index]
                    explicit_barcodes_counter[barcode] += 1
    return explicit_barcodes_counter


def group_by_hamming_distance(
    explicit_barcodes_counter, cell_count, error_hamming_distance, proportion_to_consider
):
    """
    Takes barcodes counter, cell count, allowable Hamming distance, proportion of barcodes to
    consider for error correction, and returns a counter of apparent barcodes grouped within
    the allowable Hamming distance, and their counts.
    """

    max_number_of_barcode_groups = cell_count * proportion_to_consider
    grouped_barcodes = {}
    barcode_groups = 0
    for explicit_barcode, explicit_count in sorted(
        explicit_barcodes_counter.items(), key=lambda x: x[1], reverse=True
    ):
        # Stop grouping and return once we reach this number of total barcode groups
        if barcode_groups > max_number_of_barcode_groups:
            return grouped_barcodes
        if not grouped_barcodes:
            grouped_barcodes[explicit_barcode] = explicit_count
            continue
        neighbor = find_hamming_neighbor(
            explicit_barcode, grouped_barcodes, error_hamming_distance
        )
        # If there exists a neighbor barcode in grouped_barcodes
        if neighbor is not None:
            grouped_barcodes[neighbor] += explicit_count
        else:
            grouped_barcodes[explicit_barcode] = explicit_count
            # Increment each time a unique barcode is added to grouped_barcodes
            barcode_groups += 1
    return grouped_barcodes


def find_hamming_neighbor(explicit_barcode, grouped_barcodes, error_hamming_distance):
    """
    Takes an explicit barcode, dictionary of grouped barcodes, and allowable Hamming
    distance, returns a more frequent barcode that is within the Hamming distance of the
    explicit barcode if one is found.
    """

    for grouped_barcode in grouped_barcodes.keys():
        if is_hamming_neighbor(explicit_barcode, grouped_barcode, error_hamming_distance):
            return grouped_barcode
    return None


def is_hamming_neighbor(string1, string2, error_hamming_distance):
    """
    Takes two strings of equal length and allowable Hamming distance, returns whether
    the two strings are within the allowable Hamming distance.
    """

    assert len(string1) == len(
        string2
    ), "Error: barcode sequences must be the same length"
    length = len(string1)
    distance = 0
    i = 0
    while i < length and distance <= error_hamming_distance:
        if string1[i] != string2[i]:
            distance += 1
        i += 1
    if distance <= error_hamming_distance:
        return True
    return False


def get_true_barcodes(explicit_barcodes_counter, cell_count):
    """
    Takes barcode counter and cell count, returns a list of the most common barcodes sorted by
    decreasing frequency.
    """

    true_barcodes = []
    for explicit_barcode, _ in sorted(
        explicit_barcodes_counter.items(), key=lambda x: x[1], reverse=True
    ):
        true_barcodes.append(explicit_barcode)
        if len(true_barcodes) == cell_count:
            break
    return true_barcodes


def write_to_file(true_barcodes, input_file, output_directory):
    """
    Takes list of sorted barcodes, input file path, output directory, and saves the list of
    barcodes in a text document at the output directory location.
    """

    if output_directory is not None:
        output_directory.mkdir(parents=True, exist_ok=True)
    else:
        output_directory = input_file.parent.resolve()

    output_file = Path(output_directory, "output.txt")
    with open(output_file, "w") as file:
        for barcode in true_barcodes:
            file.writelines(barcode + "\n")
    print(
        f"{len(true_barcodes)} true barcodes found. Results located in {output_file.resolve()}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="filepath to FASTQ file")
    parser.add_argument("anchor", type=str, help="the known anchor sequence")
    parser.add_argument(
        "cell_count",
        type=int,
        help="number of cells sequenced/expected true barcodes",
    )
    parser.add_argument(
        "-e",
        "--error-hamming-distance",
        type=int,
        default=1,
        help="""Hamming distance used for error correction, default is 1, 0 disables error 
        correction""",
    )
    parser.add_argument(
        "-p",
        "--proportion-to-consider",
        type=float,
        default=1,
        help="""number of barcode groups to create during error correction proportional to
        cell-count, default is 1 (error-correction stops once cell_count number of groups are
        created), this argument is ignored when error_hamming_distance is zero""",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="directory to save output list of true barcodes, default is with input file",
    )
    args = parser.parse_args()
    if args.error_hamming_distance < 0:
        parser.error("error distance must be greater than or equal to 0")
    if args.proportion_to_consider < 1:
        parser.error("proportion_to_consider must be greater than or equal to 1")
    find_barcodes(
        args.input,
        args.anchor,
        args.cell_count,
        args.error_hamming_distance,
        args.proportion_to_consider,
        args.output,
    )
