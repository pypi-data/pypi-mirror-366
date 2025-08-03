from enum import Enum
import warnings
import numpy as np
from typing import List, Union, Optional, Tuple
from lightbinpack import nf, ffd, bfd, obfd, obfdp, ogbfd, ogbfdp, ohgbfd, oshgbfd


class PackingStrategy(Enum):
    """Enum class for packing strategies"""

    NF = "nf"  # Next Fit
    FFD = "ffd"  # First Fit Decreasing
    BFD = "bfd"  # Best Fit Decreasing
    OBFD = "obfd"  # Optimized Best Fit Decreasing
    OBFDP = "obfdp"  # Parallel Optimized Best Fit Decreasing
    OGBFD = "ogbfd"  # Optimized Grouped Best Fit Decreasing
    OGBFDP = "ogbfdp"  # Parallel Optimized Grouped Best Fit Decreasing
    OHGBFD = "ohgbfd"  # Optimized Heterogeneous Grouped Best Fit Decreasing
    OSHGBFD = (
        "oshgbfd"  # Optimized Sequential Heterogeneous Grouped Best Fit Decreasing
    )


class PackingVariant(Enum):
    """Enum class for packing variants"""

    LINEAR = "linear"  # Linear time complexity
    SQUARE = "square"  # Square time complexity


def pack(
    lengths: List[Union[int, float]],
    batch_max_length: Union[float, int, List[int], List[List[int]]],
    strategy: Optional[Union[str, PackingStrategy]] = None,
    variant: Optional[Union[str, PackingVariant]] = None,
    dp_size: int = 1,
    item_max_length: int = -1,
    enable_parallel: bool = False,
    parallel_strategy: int = 0,
    weights: Optional[List[int]] = [],
    random_seed: Optional[int] = None,
    add_noise: bool = False,
    noise_scale: float = 0.01,
) -> Union[List[List[int]], List[List[List[int]]], List[Tuple[int, List[List[int]]]]]:
    """
    Unified packing function API

    Args:
        lengths: List of item lengths to be packed
        batch_max_length: Maximum capacity of bins.
            - For basic and grouped algorithms: single value
            - For OHGBFD: list of integers
            - For OSHGBFD: list of integer lists
        strategy: Packing strategy, can be PackingStrategy enum value or corresponding string
        variant: Packing variant, can be PackingVariant enum value or corresponding string ("linear"/"square")
        dp_size: Number of bins per group
        item_max_length: Maximum length of items. If -1, calculated automatically
        enable_parallel: Whether to enable parallel processing (for parallel algorithms)
        parallel_strategy: Strategy for parallel algorithms (0 or 1)
        weights: Optional weights for heterogeneous algorithms (OHGBFD/OSHGBFD)
        random_seed: Optional random seed for reproducible randomization. If None, uses system time
        add_noise: Whether to add small integer noise to lengths to create randomization
        noise_scale: Scale factor for noise (as fraction of max length), default 0.01

    Returns:
        Different formats of packing results based on strategy:
        - Basic algorithms (NF/FFD/BFD/OBFD/OBFDP): List[List[int]]
        - Grouped algorithms (OGBFD/OGBFDP): List[List[List[int]]]
        - Heterogeneous bin algorithms (OHGBFD/OSHGBFD): List[Tuple[int, List[List[int]]]]

    Raises:
        ValueError: When parameters are invalid
        RuntimeError: When packing process fails
    """
    if variant is not None:
        if isinstance(variant, str):
            try:
                variant = PackingVariant(variant.lower())
            except ValueError:
                raise ValueError(f"Invalid variant: {variant}")

    if strategy is None:
        if isinstance(batch_max_length, (list, tuple)):
            if all(isinstance(x, (list, tuple)) for x in batch_max_length):
                strategy = PackingStrategy.OSHGBFD
            elif all(isinstance(x, (int, float)) for x in batch_max_length):
                strategy = PackingStrategy.OHGBFD
            else:
                raise ValueError("Invalid batch_max_length format")
        else:
            if variant is None:
                strategy = PackingStrategy.OGBFD
            else:
                strategy = (
                    PackingStrategy.OGBFD
                    if variant == PackingVariant.SQUARE
                    else PackingStrategy.OBFD
                )
    else:
        if variant is not None:
            warnings.warn(
                "Both strategy and variant are specified. Using the specified strategy."
            )

        if isinstance(strategy, str):
            try:
                strategy = PackingStrategy(strategy.lower())
            except ValueError:
                raise ValueError(f"Invalid strategy: {strategy}")

    if not lengths:
        return []

    working_lengths = lengths
    if add_noise and lengths:
        if (
            strategy == PackingStrategy.NF
            or strategy == PackingStrategy.FFD
            or strategy == PackingStrategy.BFD
        ):
            raise ValueError("add_noise is not supported for NF, FFD, and BFD")
        if random_seed is not None:
            np.random.seed(random_seed)
        lengths_array = np.array(lengths, dtype=int)
        max_length = np.max(lengths_array)
        noise_magnitude = max(1, int(max_length * noise_scale))
        noise = np.random.randint(
            -noise_magnitude, noise_magnitude + 1, size=len(lengths_array)
        )
        noisy_lengths = lengths_array + noise
        if strategy == PackingStrategy.OSHGBFD:
            min_batch_max = min(min(sublist) for sublist in batch_max_length if sublist)
            noisy_lengths = np.minimum(noisy_lengths, min_batch_max)
        elif strategy == PackingStrategy.OHGBFD:
            min_batch_max = min(batch_max_length)
            noisy_lengths = np.minimum(noisy_lengths, min_batch_max)
        else:
            noisy_lengths = np.minimum(noisy_lengths, int(batch_max_length))
        working_lengths = np.maximum(noisy_lengths, 1).astype(int).tolist()

    if strategy == PackingStrategy.OSHGBFD:
        if not isinstance(batch_max_length, (list, tuple)) or not all(
            isinstance(sublist, (list, tuple))
            and all(isinstance(x, int) for x in sublist)
            for sublist in batch_max_length
        ):
            raise ValueError(
                "batch_max_length must be a list of integer lists for OSHGBFD"
            )
    elif strategy == PackingStrategy.OHGBFD:
        if not isinstance(batch_max_length, (list, tuple)) or not all(
            isinstance(x, int) for x in batch_max_length
        ):
            raise ValueError("batch_max_length must be a list of integers for OHGBFD")
    else:
        if isinstance(batch_max_length, (list, tuple)):
            raise ValueError(
                "batch_max_length must be a single value for non-heterogeneous bin algorithms"
            )

    if enable_parallel:
        if strategy == PackingStrategy.OBFD:
            strategy = PackingStrategy.OBFDP
        elif strategy == PackingStrategy.OGBFD:
            strategy = PackingStrategy.OGBFDP

    try:
        if strategy == PackingStrategy.NF:
            return nf(working_lengths, batch_max_length)

        elif strategy == PackingStrategy.FFD:
            return ffd(working_lengths, batch_max_length)

        elif strategy == PackingStrategy.BFD:
            return bfd(working_lengths, batch_max_length)

        elif strategy == PackingStrategy.OBFD:
            return obfd(working_lengths, batch_max_length, item_max_length)

        elif strategy == PackingStrategy.OBFDP:
            return obfdp(
                working_lengths, batch_max_length, item_max_length, parallel_strategy
            )

        elif strategy == PackingStrategy.OGBFD:
            return ogbfd(working_lengths, batch_max_length, dp_size, item_max_length)

        elif strategy == PackingStrategy.OGBFDP:
            return ogbfdp(
                working_lengths,
                batch_max_length,
                dp_size,
                item_max_length,
                parallel_strategy,
            )

        elif strategy == PackingStrategy.OHGBFD:
            return ohgbfd(working_lengths, batch_max_length, item_max_length, weights)

        elif strategy == PackingStrategy.OSHGBFD:
            return oshgbfd(working_lengths, batch_max_length, item_max_length, weights)

    except Exception as e:
        raise RuntimeError(f"Packing failed with strategy {strategy}: {str(e)}")
