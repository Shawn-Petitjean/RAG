import json
from typing import List


def check_path(check_path: str, answer_path: str) -> bool:
    """Check if two file paths are equal.

    Args:
        answer_path: First file path.
        check_path: Second file path.

    Returns:
        True if paths are equal, False otherwise.
    """
    return answer_path == check_path


def check_iou(
    a_start: int, a_end: int, b_start: int, b_end: int
) -> float:
    """Calculate Intersection over Union (IoU) of two intervals.

    Args:
        a_start: Start of first interval.
        a_end: End of first interval.
        b_start: Start of second interval.
        b_end: End of second interval.

    Returns:
        IoU score between 0 and 1.
    """
    intersection = max(0, min(a_end, b_end) - max(a_start, b_start))

    if intersection == 0:
        return 0.0

    union = max(a_end, b_end) - min(a_start, b_start)

    return intersection / union


def find_recall_metric(
    answer_path: str, dataset_path: str, k: int
) -> float:
    """Calculate recall metric for retrieval evaluation.

    Args:
        answer_path: Path to answer file.
        dataset_path: Path to dataset file.
        k: Number of top chunks considered.

    Returns:
        Recall metric (0 to 1).

    Raises:
        ValueError: If k is larger than available retrieved sources.
    """
    with open(answer_path, "r") as f:
        answers = json.load(f)
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    recall_lst: List[float] = []
    for a_question in answers["rag_questions"]:
        for d_question in dataset["search_results"]:
            if a_question["question_id"] == d_question["question_id"]:
                nb_source_find = 0
                for a_source in a_question["sources"]:
                    found = False
                    if k > len(d_question["retrieved_sources"]):
                        raise ValueError("ERROR: k is too big")
                    for b_source in d_question["retrieved_sources"][:k]:
                        if (
                            check_path(
                                a_source["file_path"],
                                b_source["file_path"]
                            )
                            and (
                                check_iou(
                                    a_source["first_character_index"],
                                    a_source["last_character_index"],
                                    b_source["first_character_index"],
                                    b_source["last_character_index"],
                                )
                            )
                            >= 0.05
                        ):
                            found = True
                            break
                    if found:
                        nb_source_find += 1
            recall_lst.append(nb_source_find / len(a_question["sources"]))
    return sum(recall_lst) / len(recall_lst)
