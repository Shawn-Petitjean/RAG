import json
from typing import Any, List


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
    a_start: int,
    a_end: int,
    b_start: int,
    b_end: int,
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
    answer_path: str,
    dataset_path: str,
    k: int,
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
    for a_question in answers.get("rag_questions", []):
        matched_question = next(
            (
                d_question
                for d_question in dataset.get("search_results", [])
                if d_question.get("question_id")
                == a_question.get("question_id")
            ),
            None,
        )
        if matched_question is None:
            recall_lst.append(0.0)
            continue

        retrieved_sources = matched_question.get("retrieved_sources", [])
        if k > len(retrieved_sources):
            raise ValueError("ERROR: k is too big")

        nb_source_find = 0
        for a_source in a_question.get("sources", []):
            found = False
            for b_source in retrieved_sources[:k]:
                if (
                    check_path(
                        a_source["file_path"],
                        b_source["file_path"],
                    )
                    and check_iou(
                        a_source["first_character_index"],
                        a_source["last_character_index"],
                        b_source["first_character_index"],
                        b_source["last_character_index"],
                    )
                    >= 0.05
                ):
                    found = True
                    break
            if found:
                nb_source_find += 1

        source_count = len(a_question.get("sources", []))
        recall_lst.append(
            0.0 if source_count == 0 else nb_source_find / source_count
        )
    return sum(recall_lst) / len(recall_lst) if recall_lst else 0.0


def _sources_match(a_source: dict[str, Any], b_source: dict[str, Any]) -> bool:
    return (
        check_path(
            a_source.get("file_path", ""),
            b_source.get("file_path", ""),
        )
        and check_iou(
            a_source.get("first_character_index", 0),
            a_source.get("last_character_index", 0),
            b_source.get("first_character_index", 0),
            b_source.get("last_character_index", 0),
        )
        >= 0.05
    )


def find_recall_metric_from_student_results(
    student_results_path: str,
    dataset_path: str,
    k: int,
) -> float:
    """Calculate recall between student search results and a gold dataset."""
    with open(student_results_path, "r") as f:
        student_results = json.load(f)
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    dataset_by_id = {
        question.get("question_id"): question
        for question in dataset.get("rag_questions", [])
    }

    recall_lst: List[float] = []
    for d_question in student_results.get("search_results", []):
        answer_question = dataset_by_id.get(d_question.get("question_id"))
        if answer_question is None:
            recall_lst.append(0.0)
            continue

        retrieved_sources = d_question.get("retrieved_sources", [])
        if k > len(retrieved_sources):
            raise ValueError("ERROR: k is too big")

        nb_source_find = 0
        for a_source in answer_question.get("sources", []):
            found = False
            for b_source in retrieved_sources[:k]:
                if _sources_match(a_source, b_source):
                    found = True
                    break
            if found:
                nb_source_find += 1

        source_count = len(answer_question.get("sources", []))
        recall_lst.append(
            0.0 if source_count == 0 else nb_source_find / source_count
        )

    return sum(recall_lst) / len(recall_lst) if recall_lst else 0.0


def list_valid_questions(
    student_answer_path: str,
    dataset_path: str,
    k: int = 5,
) -> list[str]:
    """Return question texts whose retrieved sources overlap with gold
    sources."""
    with open(student_answer_path, "r") as f:
        student_results = json.load(f)
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    dataset_by_id = {
        question.get("question_id"): question
        for question in dataset.get("rag_questions", [])
    }

    valid_questions: list[str] = []
    for d_question in student_results.get("search_results", []):
        answer_question = dataset_by_id.get(d_question.get("question_id"))
        if answer_question is None:
            continue

        retrieved_sources = d_question.get("retrieved_sources", [])
        if k > len(retrieved_sources):
            continue

        if any(
            _sources_match(a_source, b_source)
            for a_source in answer_question.get("sources", [])
            for b_source in retrieved_sources[:k]
        ):
            question_text = d_question.get("question", "")
            valid_questions.append(question_text)

    return valid_questions


def evaluate_student_search_results(
    student_results_path: str,
    dataset_path: str,
    k: int = 5,
    max_context_length: int = 2000,
    threshold: float = 0.0,
) -> float:
    """Evaluate student search results and print pass/fail output."""
    score = find_recall_metric_from_student_results(
        student_results_path,
        dataset_path,
        k,
    )
    print(f"Recall@{k} = {score:.2f}")
    if score >= threshold:
        print(f"PASS: Recall@{k} >= {threshold}")
    else:
        print(f"FAIL: Recall@{k} < {threshold}")
    return score
