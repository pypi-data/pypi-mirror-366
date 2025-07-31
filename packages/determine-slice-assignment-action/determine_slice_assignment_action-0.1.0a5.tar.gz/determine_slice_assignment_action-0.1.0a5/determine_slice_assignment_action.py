# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from operator import gt, lt

from canonical_range import canonicalize_stop, slice_to_offset_range
from split_interval import split_interval


class SliceAssignmentAction(object): pass


class NoAction(SliceAssignmentAction): pass


class ReplaceOffsetRange(SliceAssignmentAction):
    __slots__ = ('offset_start', 'offset_stop', 'offset_step')

    def __new__(cls, offset_start, offset_stop, offset_step):
        instance = super(ReplaceOffsetRange, cls).__new__(cls)
        instance.offset_start = offset_start
        instance.offset_stop = canonicalize_stop(offset_start, offset_stop, offset_step)
        instance.offset_step = offset_step
        return instance


class Insert(SliceAssignmentAction):
    __slots__ = ('index', 'reverse')

    def __new__(cls, index, reverse):
        instance = super(Insert, cls).__new__(cls)
        instance.index = index
        instance.reverse = reverse
        return instance


def determine_slice_assignment_action(sequence_length, slice_object):
    # type: (int, slice) -> SliceAssignmentAction
    if sequence_length < 0:
        raise ValueError('sequence length must be non-negative')

    # `step > 0, start_offset <= stop_offset; step < 0, start_offset >= stop_offset`
    start_offset, stop_offset, step = slice_to_offset_range(sequence_length, slice_object)

    # No elements selected
    if start_offset == stop_offset:
        if start_offset < 0:
            return Insert(0, reverse=step < 0)
        elif start_offset < sequence_length:
            return Insert(start_offset, reverse=step < 0)
        else:
            return Insert(sequence_length, reverse=step < 0)
    # The sequence is empty
    elif sequence_length == 0:
        return Insert(0, reverse=step < 0)
    else:
        if step > 0:
            # `start_offset < stop_offset`
            left, intersection, right = split_interval((0, sequence_length), (start_offset, stop_offset), lt)
            if intersection is not None:
                intersection_start, intersection_stop = intersection
                return ReplaceOffsetRange(intersection_start, intersection_stop, step)
            elif left is not None:
                return Insert(0, reverse=False)
            else:
                return Insert(sequence_length, reverse=False)
        else:
            # `start_offset > stop_offset`
            reverse_left, reverse_intersection, reverse_right = split_interval((sequence_length - 1, -1),
                                                                               (start_offset, stop_offset), gt)
            if reverse_intersection is not None:
                reverse_intersection_start, reverse_intersection_stop = reverse_intersection
                return ReplaceOffsetRange(reverse_intersection_start, reverse_intersection_stop, step)
            elif reverse_left is not None:
                return Insert(sequence_length, reverse=True)
            else:
                return Insert(0, reverse=True)
