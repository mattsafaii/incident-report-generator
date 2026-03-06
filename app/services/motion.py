import numpy as np
from pathlib import Path
from PIL import Image

from app.config import MAX_FRAMES_TO_MODEL


def compute_motion_scores(frame_dir: Path) -> list[tuple[Path, float]]:
    """Compute motion score for each frame based on pixel diff with previous frame."""
    frames = sorted(frame_dir.glob("frame_*.jpg"))
    if len(frames) < 2:
        return [(f, 0.0) for f in frames]

    scores: list[tuple[Path, float]] = [(frames[0], 0.0)]
    prev_arr = np.array(Image.open(frames[0]).convert("L").resize((320, 240)))

    for frame_path in frames[1:]:
        curr_arr = np.array(Image.open(frame_path).convert("L").resize((320, 240)))
        diff = np.mean(np.abs(curr_arr.astype(float) - prev_arr.astype(float)))
        scores.append((frame_path, float(diff)))
        prev_arr = curr_arr

    return scores


def select_frames(
    scored_frames: list[tuple[Path, float]],
    max_frames: int = MAX_FRAMES_TO_MODEL,
) -> list[tuple[Path, float, bool]]:
    """Select up to max_frames with temporal spread.

    Always includes first and last frames. Fills remaining budget
    from highest motion-score frames, enforcing a minimum gap.
    """
    n = len(scored_frames)
    if n <= max_frames:
        return [(p, s, True) for p, s in scored_frames]

    selected_indices = {0, n - 1}
    remaining_budget = max_frames - 2

    # Sort middle frames by motion score descending
    candidates = [
        (i, score) for i, (_, score) in enumerate(scored_frames)
        if i not in selected_indices
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Enforce minimum temporal gap
    min_gap = max(1, n // max_frames)
    for idx, score in candidates:
        if remaining_budget <= 0:
            break
        if all(abs(idx - s) >= min_gap for s in selected_indices):
            selected_indices.add(idx)
            remaining_budget -= 1

    # If budget remains (gap was too strict), fill greedily
    if remaining_budget > 0:
        for idx, score in candidates:
            if remaining_budget <= 0:
                break
            if idx not in selected_indices:
                selected_indices.add(idx)
                remaining_budget -= 1

    return [
        (path, score, i in selected_indices)
        for i, (path, score) in enumerate(scored_frames)
    ]
