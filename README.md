# Introduction
In this project, I deliver a program which automates the selection of true barcodes out of a long list of apparent barcodes. This is a necessary step in MAPseq, a novel neuroanatomical tracing method. Once the true barcodes are known, conclusions can be drawn about signaling patterns of neurons throughout the brain.

# Background
[MAPseq](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6640135/) is a technique for the mapping of neuron connections in the brain. This technique is advantageous to conventional neuroanatomical tracing methods in several ways, including its high throughput. In MAPseq, random RNA nucleotide sequences known as "barcodes" are generated within main neuron cell bodies (somas) using a virus. The barcodes then spread to the neuron's axons. By matching the locations of these unique barcodes (both in the soma, and other regions), the long-range connections of many individual neurons can be mapped. If a barcode exists in both the soma within one region, and also in another region of the brain, then an axon is very likely connecting the soma to that region. The generation of barcodes is a biologic process, completed after injection, so the exact barcodes are not known in advance. It is known, however, that the number of neuron cells being sequenced will be approximately equal to the number of true barcodes. 

Potential barcodes are able to be identified by anchor sequences. A characteristic of the virus which produces barcodes is a known string of nucleotide base pairs called an "anchor." These known anchor sequences occur adjacent to barcodes. In other words, a potential barcode is defined as the base pairs immediately preceding the anchor sequence. The datasets used are from experiments with 30 nucleotide barcodes and a 19 nucleotide anchor sequence (GTACTGCGGCCGCTACCTA). By searching for this anchor sequence in the sequencing data, it can be deduced that the 30 base pairs preceding any occurrence of this anchor sequence are a potential barcode. The provided data has already been parsed for any pattern loosely matching the anchor sequence. Each 4 lines of the FASTQ file is one read, including the potential barcode and anchor sequence. 

Errors are imminent during the sequencing and transcription processes. Because of this, error correction may be applied to combine barcodes which have only a few incorrect base pairs. 


# File descriptions
The notebook `barcodes.ipynb` is used to show the thought process behind building the solution, and where the justifications are laid out before they are implemented. It also includes considerations and examples of optimizations, and observations of the dataset. The result is `find_barcodes.py`, a script that can be used through the command line.

# Solution
The true barcodes are expected to have a higher count relative to errors in the data. The most frequently occurring barcodes are most likely the true barcodes. 

By default, error correction is applied by grouping less common barcodes into more common barcodes within 1 Hamming distance of each other. The benefit of correcting similar barcodes is situational, so error correction can be increased or disabled. Disabling error correction will simply return the most common explicit barcodes.

It is not necessary to compare all barcodes with all other barcodes in order to get an accurate picture of the true barcodes. Due to the heavily skewed distribution of the dataset, considering only a portion of the most common barcodes results in nearly the same results, but with much better runtime. Comparing all barcodes might achieve more accurate results, but there will still exist uncertainty, especially near the threshold for true barcodes. 

All of these thoughts are expanded upon in `barcodes.ipynb`.

# How to run
This program was developed using Python 3.8 without any external requirements. It can be run on any machine with Python installed; version 3.8 is recommended. It can be invoked by running 

```
python3 find_barcodes.py input anchor cell_count
``` 

from the command line. 

`input` is the filepath of a fastq file to find barcodes in. 

`anchor` is the anchor sequence. 

`cell_count` is the number of cells sequenced (the expected number of true barcodes).


Additional arguments can also be passed:

```
usage: find_barcodes.py [-h] [-e ERROR_HAMMING_DISTANCE] [-p PROPORTION_TO_CONSIDER] [-o OUTPUT] input anchor cell_count

positional arguments:
  input                 filepath to FASTQ file
  anchor                the known anchor sequence
  cell_count            number of cells sequenced/expected true barcodes

optional arguments:
  -h, --help            show this help message and exit
  -e ERROR_HAMMING_DISTANCE, --error-hamming-distance ERROR_HAMMING_DISTANCE
                        Hamming distance used for error correction, default is 1, 0 disables error correction
  -p PROPORTION_TO_CONSIDER, --proportion-to-consider PROPORTION_TO_CONSIDER
                        number of barcode groups to create during error correction proportional to cell-count, default is 1 (error-correction stops once cell_count number of groups are created), this argument is ignored when error_hamming_distance is zero
  -o OUTPUT, --output OUTPUT
                        directory to save output list of true barcodes, default is with input file
```

`error_hamming_distance` is the Hamming distance between similar barcodes which will be grouped together. The error distance is 1 by default. Error correction can be disabled by setting this to 0.

`proportion_to_consider` is essentially how thorough the error correction is. The default value of 1 will do the minimum number of comparisons necessary in order to return `cell_count` number of barcode groups. Higher values will consider more barcodes, resulting in results that align more closely with the entire dataset, at the expense of runtime. For example, when `proportion_to_consider` is 3 and `cell_count` is 500, the program will continue grouping barcodes until it creates 1500 barcode groups. The top 500 barcode groups are then output. With a high enough value, the program will compare every barcode to every other barcode. This is not recommended, as runtime increases quadratically proportional to number of barcodes compared. 

`output` is the directory to save the results in and is by default the same directory that the input file is in. Linux, Mac, and Windows path syntax are accepted. The output file is always named `output.txt` and will overwrite existing files in the output directory with the same name. 

Example on Linux:
```
$ python3 find_barcodes.py ./data_1M.fastq GTACTGCGGCCGCTACCTA 350 -o ./output_dir -p 3
350 true barcodes found. Results located in /home/user/find-barcodes/output_dir/output.txt
```