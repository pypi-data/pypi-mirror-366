"""
Text alignment functionality for matching source and target texts.
"""

import math
from typing import List, Optional, Tuple

import scipy.stats as stats


class Aligner:
    """
    A class for aligning source and target texts using the Gale-Church algorithm.

    This class provides functionality to align segments of text between
    source and target languages, creating parallel corpora for translation
    and analysis purposes.
    """

    def __init__(
        self,
        language_pair: str = "en-es",
        c: Optional[float] = None,
        s2: Optional[float] = None,
        gap_penalty: Optional[float] = None,
    ):
        """
        Initialize the Aligner with language-specific parameters.

        Args:
            language_pair: Language pair code (e.g., "en-es", "en-fr", "en-de").
                          Defaults to "en-es" (English-Spanish).
            c: Optional mean length ratio override.
            s2: Optional variance of the difference override.
            gap_penalty: Optional gap penalty override.
        """
        # Language-specific parameters for the Gale-Church algorithm
        self.language_params = {
            "en-es": {"c": 1.0, "s2": 6.8, "gap_penalty": 3.0},
            "en-fr": {"c": 1.1, "s2": 7.2, "gap_penalty": 3.0},
            "en-de": {"c": 1.2, "s2": 8.1, "gap_penalty": 3.0},
            "en-it": {"c": 1.05, "s2": 7.0, "gap_penalty": 3.0},
        }
        self.params = self.language_params.get(
            language_pair, self.language_params["en-es"]
        )
        self.c = c if c is not None else self.params["c"]
        self.s2 = s2 if s2 is not None else self.params["s2"]
        self.gap_penalty = (
            gap_penalty if gap_penalty is not None else self.params["gap_penalty"]
        )
        # Pre-calculate gap penalty costs
        self._gap_cost = self._gap_penalty_cost()
        self._double_gap_cost = 2 * self._gap_cost

    def align(
        self, source_sentences: List[str], target_sentences: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Align source and target sentences into parallel segments.

        Args:
            source_sentences: List of source language sentences (pre-tokenized).
            target_sentences: List of target language sentences (pre-tokenized).

        Returns:
            A list of tuples containing aligned (source_segment, target_segment) pairs.
        """
        # Handle empty sentence lists
        if not source_sentences or not target_sentences:
            return []

        # Filter out empty sentences
        source_sentences = [s.strip() for s in source_sentences if s.strip()]
        target_sentences = [s.strip() for s in target_sentences if s.strip()]

        if not source_sentences or not target_sentences:
            return []

        # For perfectly matched sentences, align 1-1
        if source_sentences == target_sentences:
            return self._align_perfect_match(source_sentences)

        # Use Gale-Church algorithm for different sentences
        return self._align_gale_church(source_sentences, target_sentences)

    def _align_perfect_match(self, sentences: List[str]) -> List[Tuple[str, str]]:
        """
        Align perfectly matched sentences 1-1.

        Args:
            sentences: List of sentences to align.

        Returns:
            List of (sentence, sentence) tuples for perfect alignment.
        """
        # Create 1-1 alignments for each sentence
        alignments = []
        for sentence in sentences:
            if sentence.strip():
                alignments.append((sentence, sentence))

        return alignments

    def _align_gale_church(
        self, source_sentences: List[str], target_sentences: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Align sentences using the Gale-Church algorithm.

        Args:
            source_sentences: List of source language sentences.
            target_sentences: List of target language sentences.

        Returns:
            List of aligned (source_segment, target_segment) tuples.
        """
        if not source_sentences or not target_sentences:
            return []

        # Calculate sentence lengths (in characters)
        source_lengths = [len(s) for s in source_sentences]
        target_lengths = [len(s) for s in target_sentences]

        # Find optimal alignment using dynamic programming
        alignment = self._gale_church_dp(source_lengths, target_lengths)

        # Convert alignment indices to actual sentence pairs
        result = []
        for src_start, src_end, tgt_start, tgt_end in alignment:
            src_segment = " ".join(source_sentences[src_start:src_end])
            tgt_segment = " ".join(target_sentences[tgt_start:tgt_end])
            result.append((src_segment, tgt_segment))

        return result

    def _gale_church_dp(
        self, source_lengths: List[int], target_lengths: List[int]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Dynamic programming implementation of Gale-Church algorithm.
        """
        m, n = len(source_lengths), len(target_lengths)
        dp = [[float("inf")] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = 0
        backtrack: List[List] = [[None] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 and j == 0:
                    continue
                candidates = []
                # 1-1 alignment
                if i > 0 and j > 0:
                    cost = self._alignment_cost(
                        source_lengths[i - 1], target_lengths[j - 1]
                    )
                    candidates.append((dp[i - 1][j - 1] + cost, (i - 1, j - 1, 1, 1)))
                # 1-0 alignment (source sentence with no target)
                if i > 0:
                    cost = self._gap_cost
                    candidates.append((dp[i - 1][j] + cost, (i - 1, j, 1, 0)))
                # 0-1 alignment (target sentence with no source)
                if j > 0:
                    cost = self._gap_cost
                    candidates.append((dp[i][j - 1] + cost, (i, j - 1, 0, 1)))
                # 2-1 alignment (two source sentences with one target)
                if i > 1 and j > 0:
                    src_len = source_lengths[i - 2] + source_lengths[i - 1]
                    cost = self._alignment_cost(src_len, target_lengths[j - 1])
                    candidates.append((dp[i - 2][j - 1] + cost, (i - 2, j - 1, 2, 1)))
                # 1-2 alignment (one source sentence with two target)
                if i > 0 and j > 1:
                    tgt_len = target_lengths[j - 2] + target_lengths[j - 1]
                    cost = self._alignment_cost(source_lengths[i - 1], tgt_len)
                    candidates.append((dp[i - 1][j - 2] + cost, (i - 1, j - 2, 1, 2)))
                # 2-2 alignment (two source sentences with two target)
                if i > 1 and j > 1:
                    src_len = source_lengths[i - 2] + source_lengths[i - 1]
                    tgt_len = target_lengths[j - 2] + target_lengths[j - 1]
                    cost = self._alignment_cost(src_len, tgt_len)
                    candidates.append((dp[i - 2][j - 2] + cost, (i - 2, j - 2, 2, 2)))
                # 2-0 alignment (two source sentences deleted)
                if i > 1:
                    cost = self._double_gap_cost
                    candidates.append((dp[i - 2][j] + cost, (i - 2, j, 2, 0)))
                # 0-2 alignment (two target sentences inserted)
                if j > 1:
                    cost = self._double_gap_cost
                    candidates.append((dp[i][j - 2] + cost, (i, j - 2, 0, 2)))
                if candidates:
                    best_cost, best_move = min(candidates, key=lambda x: x[0])
                    dp[i][j] = best_cost
                    backtrack[i][j] = best_move
        return self._reconstruct_alignment(backtrack, m, n)

    def _alignment_cost(self, src_len: int, tgt_len: int) -> float:
        """
        Calculate alignment cost using the correct Gale-Church statistical model.

        Args:
            src_len: Source sentence length.
            tgt_len: Target sentence length.

        Returns:
            Alignment cost (negative log probability).
        """
        if src_len == 0 and tgt_len == 0:
            return 0.0

        # Calculate delta using the correct Gale-Church formula:
        # delta = (tgt_len - src_len * c) / sqrt(src_len * s²)
        # where c is the mean length ratio and s² is the variance of the difference
        if src_len == 0:
            delta = float("inf")
        else:
            delta = abs(tgt_len - src_len * self.c) / math.sqrt(src_len * self.s2)

        # Calculate two-tailed probability using normal distribution
        # P(|X| >= delta) = 2 * (1 - CDF(delta))
        if delta > 10:
            # Very unlikely match - use a small but finite probability
            probability = 1e-12
        else:
            # Use scipy's normal CDF for accurate calculation
            # Add epsilon to prevent numerical instability
            probability = 2 * (1 - stats.norm.cdf(delta)) + 1e-12

        # Convert probability to cost (negative log probability)
        # Ensure probability is never exactly zero to prevent infinite cost
        # Also ensure probability doesn't exceed 1 to prevent negative cost
        probability = min(probability, 1.0 - 1e-12)
        cost = -math.log(probability)

        return cost

    def _gap_penalty_cost(self) -> float:
        """
        Calculate the cost for gap alignments (1-0 or 0-1).

        Returns:
            Gap penalty cost.
        """
        # Convert gap penalty (in standard deviations) to two-tailed probability
        # A gap penalty of 3.0 means the cost is equivalent to a 3-sigma deviation
        # Add epsilon to prevent numerical instability
        probability = 2 * (1 - stats.norm.cdf(self.gap_penalty)) + 1e-12

        # Convert to cost
        # Ensure probability is never exactly zero to prevent infinite cost
        # Also ensure probability doesn't exceed 1 to prevent negative cost
        probability = min(probability, 1.0 - 1e-12)
        cost = -math.log(probability)

        return cost

    def _reconstruct_alignment(
        self, backtrack: List[List], m: int, n: int
    ) -> List[Tuple[int, int, int, int]]:
        """
        Reconstruct the alignment path from the backtracking table.

        Args:
            backtrack: Backtracking table.
            m: Number of source sentences.
            n: Number of target sentences.

        Returns:
            List of (src_start, src_end, tgt_start, tgt_end) tuples.
        """
        alignment = []
        i, j = m, n

        while i > 0 or j > 0:
            if backtrack[i][j] is None:
                break

            prev_i, prev_j, src_count, tgt_count = backtrack[i][j]

            # Add alignment segment
            alignment.append((prev_i, i, prev_j, j))

            # Move to previous position
            i, j = prev_i, prev_j

        # Reverse to get correct order
        alignment.reverse()
        return alignment
