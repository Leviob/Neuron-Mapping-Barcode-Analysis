from collections import Counter
from find_barcodes import *


def test_group_by_hamming_distance_prioritize_common_barcodes():
    barcodes_counter = Counter(
        {
            "AAAA": 3,
            "AAGG": 2,
            "AAGA": 1,
            "AAAG": 1,
        }
    )

    result = Counter(
        {
            "AAAA": 5,
            "AAGG": 2,
        }
    )

    assert group_by_hamming_distance(barcodes_counter, 100, 1, 100) == result


def test_group_by_hamming_distance_measures_hamming_distance_correctly():
    barcodes_counter = Counter(
        {
            "AAAA": 3,
            "AAAC": 1,
            "AACA": 1,
            "CACA": 1,
            "TTTT": 3,
            "GTTT": 1,
            "GTGT": 1,
        }
    )

    grouped_by_1 = Counter(
        {
            "AAAA": 5,
            "CACA": 1,
            "TTTT": 4,
            "GTGT": 1,
        }
    )

    grouped_by_2 = Counter(
        {
            "AAAA": 6,
            "TTTT": 5,
        }
    )

    assert group_by_hamming_distance(barcodes_counter, 100, 1, 100) == grouped_by_1
    assert group_by_hamming_distance(barcodes_counter, 100, 2, 100) == grouped_by_2


def test_is_hamming_neighbor_measures_correct_distance():

    assert is_hamming_neighbor("AAAA", "AAAA", 1) is True
    assert is_hamming_neighbor("AACA", "AAAA", 1) is True
    assert is_hamming_neighbor("TAAA", "CAAA", 1) is True
    assert is_hamming_neighbor("TTAA", "AAAA", 2) is True
    assert is_hamming_neighbor("CAAA", "ACAA", 1) is False
    assert is_hamming_neighbor("TTAA", "AAAA", 1) is False
    assert is_hamming_neighbor("AAAA", "TTTT", 3) is False
    assert is_hamming_neighbor("AAAA", "TTTT", 4) is True


def test_get_true_barcodes():
    explicit_barcodes_counter = Counter(
        {
            "TTTT": 1,
            "AAAA": 4,
            "GGGG": 2,
            "CCCC": 3,
        }
    )

    assert get_true_barcodes(explicit_barcodes_counter, 3) == ["AAAA", "CCCC", "GGGG"]
