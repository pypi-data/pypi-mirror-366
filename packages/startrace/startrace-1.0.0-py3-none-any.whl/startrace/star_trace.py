# This file contains data class definitions to help with file selection

# Used to create easier-to-read options
from enum import Enum

# Used to define the dataclasses
from dataclasses import dataclass
from typing import Optional, Tuple
from numbers import Number
from collections.abc import Iterable

# Needed to convert types when np arrays are passed into num
import numpy as np



def get_depth(obj) -> int:
    if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
        try:
            first = next(iter(obj))
        except StopIteration:
            return 1  # empty list: still 1D
        return 1 + get_depth(first)
    return 0



@dataclass
class Iter:
    start: Number
    end: Number
    step: Number

    def __post_init__(self):
        # Enforce same Number types
        types = {type(self.start), type(self.end), type(self.step)}
        if len(types) > 1:
            raise TypeError(f"Inconsistent number types in Iter: {types}")

        # Enforce iter ordering
        if self.start > self.end and self.step > 0:
            raise ValueError("`start` must be less than or equal to `end` when `step` is positive")
        if self.start < self.end and self.step < 0:
            raise ValueError("`start` must be greater than or equal to `end` when `step` is negative")

    def increment(self, num: Number):
        if type(num) != type(self.start):
            raise TypeError(f"Inconsistent number types in Iter: 'num':{type(num)} != 'start':{type(self.start)}")
        # We only need to check against one iter value because we enforced they are all the same type

        if ((self.step > 0 and num < self.end and num + self.step <= self.end) or
                (self.step < 0 and num > self.end and num + self.step >= self.end)):
            return num + self.step, True
        return self.start, False



@dataclass
class Token:
    phrases: str | Iterable
    num: Optional[Number] | Optional[Iterable[Number]] = None
    iter: Optional[Iter] | Optional[Tuple[Number, Number, Number]] = None

    def __post_init__(self):
        # Make sure the user can't put two iterables
        if (isinstance(self.phrases, Iterable) and not isinstance(self.phrases, str)) and isinstance(self.num, Iterable):
            raise ValueError("'phrases' and 'num' cannot both be iterable")

        # Normalize string or iterable input to list[str]
        if isinstance(self.phrases, str):
            self.phrases = [self.phrases]
        elif isinstance(self.phrases, Iterable):
            self.phrases = [str(item) for item in self.phrases]

        # If num is np array, convert to a normal python array
        if isinstance(self.num, np.ndarray):
            self.num = self.num.tolist()

        # Check shape
        if isinstance(self.num, Iterable) and not isinstance(self.num, (str, bytes)):
            if get_depth(self.num) != 1:
                raise ValueError("`num` must be a 1D array or number")

        # Normalize Iterable to Number and set iter
        if isinstance(self.num, Iterable) and not isinstance(self.num, (str, bytes)) and self.iter is None:
            values = list(self.num)
            len_values = len(values)
            self.num = values[0]
            self.iter = Iter(values[0], values[len_values - 1], 1)
        elif isinstance(self.num, Iterable) and not isinstance(self.num, (str, bytes)) and self.iter is not None:
            raise TypeError("`iter` must be None when `num` is an Iterable")

        len_phrases = len(self.phrases)

        # If multiple phrases
        if len_phrases > 1:
            if self.num is None:
                self.num = 0
            if self.iter is None:
                self.iter = Iter(0, len_phrases - 1, 1)

        # Build iter from tuple if the user inputs that way
        if isinstance(self.iter, tuple):
            self.iter = Iter(*self.iter)



        # Enforce that num and iter.* are all the same type
        num_type = type(self.num)
        if self.num is not None and self.iter is None:
            raise TypeError("`iter` must be provided when `num` is not None")
        if self.num is not None and self.iter is not None:
            iter_types = {type(self.iter.start), type(self.iter.end), type(self.iter.step)}
            if any(t != num_type for t in iter_types):
                raise TypeError(f"`num` is {num_type}, but `iter` contains {iter_types}")

        # Enforce proper Number values when there are multiple phrases
        if len_phrases > 1:
            # Enforce int Number values for indexing
            if isinstance(self.num, float):
                raise TypeError("`num` must be an int when `type` is PHRASE")
            if isinstance(self.iter.start, float):
                raise TypeError("`iter.*` must be an int when `type` is PHRASE")
            # Don't check other iter values because we already made sure they were the same type above

            # Enforce iter len values match with phrase len
            if self.num >= len_phrases:
                raise ValueError("`num` must be less than `len(phrase)` when `type` is PHRASE")
            if self.iter.start < 0 or self.iter.start >= len_phrases:
                raise ValueError("`iter.start` must be between 0 and `len(phrase)-1` when `type` is PHRASE")
            if self.iter.end < 0 or self.iter.end >= len_phrases:
                raise ValueError("`iter.end` must be between 0 and `len(phrase`)-1` when `type` is PHRASE")



@dataclass
class Pattern:
    tokens: list[Token]

    def get_pattern(self) -> str:
        parts = []

        for token in self.tokens:
            if len(token.phrases) > 1:
                parts.append(token.phrases[token.num])
            elif token.num is None:
                parts.append(token.phrases[0])
            else:
                parts.append(token.phrases[0] + str(token.num))

        return "".join(parts)

    # Return if any tokens were able to increment
    def increment(self) -> bool:
        for token in reversed(self.tokens):
            if token.num is not None:
                token.num, incremented = token.iter.increment(token.num)
                if incremented:
                    return True
        return False