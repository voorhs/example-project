from copy import deepcopy

import numpy as np

from .convex_hull import jarvis_algorithm
from .data import ColoredPoint


def remove_elements_by_indexes(original_list: list, indexes_to_remove: list[int]):
    indexes_to_remove.sort(reverse=True)

    for index in indexes_to_remove:
        if 0 <= index < len(original_list):
            original_list.pop(index)

    return original_list


def has_duplicates(float_list):
    return len(float_list) != len(set(float_list))


def find_closest_to_middle(lst: list[bool]) -> int | None:
    n = len(lst)
    if n == 0:
        return None

    middle = n // 2
    left = middle
    right = middle

    while left >= 0 or right < n:
        if left >= 0 and lst[left]:
            return left
        if right < n and lst[right]:
            return right
        left -= 1
        right += 1

    return None


def connect_points(
    points: list[ColoredPoint],
) -> list[tuple[ColoredPoint, ColoredPoint]]:
    points = deepcopy(points)
    res = []  # list of tuples[point_id, point_id]
    n = len([p for p in points if p.black])
    assert n == len([p for p in points if not p.black])

    while len(points) > 0:
        hull_ids = jarvis_algorithm(points)
        if all(points[point_id].black for point_id in hull_ids) or all(
            not points[point_id].black for point_id in hull_ids
        ):
            # the same color
            coords = [p.x for p in points]
            if has_duplicates(coords):
                coords = [p.y for p in points]
            left_to_right_ids = np.argsort(coords)
            black_counter = 0
            white_counter = 0
            trace = []
            for border, point_id in enumerate(left_to_right_ids):
                if points[point_id].black:
                    black_counter += 1
                else:
                    white_counter += 1
                trace.append(black_counter == white_counter)

            border = find_closest_to_middle(trace)
            if border is None:
                raise RuntimeError("something's wrong")
            left_set = [points[i] for i in left_to_right_ids[: border + 1]]
            right_set = [points[i] for i in left_to_right_ids[border + 1 :]]
            res.extend(connect_points(left_set))
            res.extend(connect_points(right_set))
            return res
        else:
            # both blacks and whites are present in the hull
            ids_to_remove = []
            i = 0
            while i < len(hull_ids) - 1:
                a_point_id, b_point_id = hull_ids[i], hull_ids[i + 1]
                if points[a_point_id].black != points[b_point_id].black:
                    # different color -> we can connect them
                    res.append((points[a_point_id], points[b_point_id]))
                    ids_to_remove.extend([a_point_id, b_point_id])
                    i += 1
                i += 1

            # exclude connected points
            remove_elements_by_indexes(points, ids_to_remove)
    return res
