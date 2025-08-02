import json
import numpy as np
import scipy.sparse as sp
from collections import defaultdict
from genlm.control.potential.base import Potential
from genlm.backend.tokenization import decode_vocab
from genlm.control.potential.built_in.llm import PromptedLLM

VERYLARGE = 10000000


def _extract_bpe_merges(tokenizer):
    """
    Attempts to extract the ordered BPE merge rules from various tokenizer types.

    Args:
        tokenizer: Tokenizer instance.

    Returns:
        list[tuple[int, int, int]]: A list of merge rules as (u_id, v_id, uv_id) tuples,
                                     ordered by application priority. Returns empty list
                                     if merges cannot be extracted.
    """
    _merges = []
    V = tokenizer.get_vocab()  # Get token string -> ID map

    def _map_merges(merge_list_str):
        """Helper to convert string pairs to ID triples."""
        mapped = []
        for u_str, v_str in merge_list_str:
            u_id = V.get(u_str)
            v_id = V.get(v_str)
            uv_id = V.get(u_str + v_str)
            if u_id is not None and v_id is not None and uv_id is not None:
                mapped.append((u_id, v_id, uv_id))
            # else: ID mapping failed
        return mapped

    # fast tokenizer
    if tokenizer.is_fast and hasattr(tokenizer, "_tokenizer"):
        # fast tokenizer + direct access
        if hasattr(tokenizer._tokenizer, "model") and hasattr(
            tokenizer._tokenizer.model, "merges"
        ):
            hf_merges_list = tokenizer._tokenizer.model.merges
            _merges = _map_merges(hf_merges_list)
            if _merges or not hf_merges_list:
                return _merges
                # else: Accessed direct merges, but ID mapping failed for ALL pairs.
        elif hasattr(tokenizer._tokenizer, "to_str"):
            subtokenizer_dict = json.loads(tokenizer._tokenizer.to_str())
            if "model" in subtokenizer_dict and "merges" in subtokenizer_dict["model"]:
                hf_merges_list = subtokenizer_dict["model"]["merges"]
                _merges = _map_merges(hf_merges_list)
                if (
                    _merges or not hf_merges_list
                ):  # Return if successful or if there were no merges to begin with
                    return _merges
                # else: Parsed JSON merges, but ID mapping failed for ALL pairs.

    # slow tokenizer
    if not _merges and hasattr(
        tokenizer, "bpe_ranks"
    ):  # Only try if fast methods failed
        hf_merges_dict = tokenizer.bpe_ranks  # dict: (u_str, v_str) -> rank
        if hf_merges_dict:
            # Sort by rank to get merge order
            sorted_merges_str = sorted(
                hf_merges_dict.keys(), key=lambda p: hf_merges_dict[p]
            )
            _merges = _map_merges(sorted_merges_str)
            if _merges or not hf_merges_dict:
                return _merges
            # else: Tokenizer had bpe_ranks, but ID mapping failed for ALL pairs

    if not _merges:
        raise ValueError("Could not determine BPE merges.")


class FastCanonicalityFilterBPE:
    def __init__(self, _merges, _encode, _decode, _encode_byte, eos_token_ids):
        self._encode_byte = _encode_byte
        self._merges = _merges
        self._encode = _encode
        self._decode = _decode
        self.V = len(_decode)  # token vocabulary size

        # priority dict might still be useful if merges aren't strictly ordered
        # or for potential future optimizations, keep it for now.
        # self.priority = {(u, v): -i for i, (u, v, _) in enumerate(self._merges)}
        self.make_derivation_table()  # Call the rewritten method

        self.__left_spine, max_left_spine_width = self._left_spine_table()
        self.__right_spine, max_right_spine_width = self._right_spine_table()

        self.left_spine_vector = self.vectorize_spine(
            self.__left_spine, max_left_spine_width
        )
        self.right_spine_vector = self.vectorize_spine(
            self.__right_spine, max_right_spine_width
        )

        self.indices = np.array(
            [
                (index, j)
                for index in range(self.V)
                for j in range(len(self.__left_spine[index]) - 1)
            ]
        )

        self.vector_r = self.left_spine_vector[self.indices[:, 0], self.indices[:, 1]]
        self.vector_rp = self.left_spine_vector[
            self.indices[:, 0], self.indices[:, 1] + 1
        ]

        tmp = sp.dok_matrix((self.V, self.V), dtype=np.int32)
        for u, v, uv in _merges:
            tmp[u, v] = uv + 1  # +1 to avoid zero-indexing

        self.parent_l_matrix = tmp.tocsr()
        self.parent_l_matrix = self.parent_l_matrix[:, self.vector_r]

        self.eos_token_ids = set(eos_token_ids)
        self.overrides = defaultdict(lambda: set())

    def __call__(self, context):
        if context == ():
            mask = np.ones(self.V, dtype=bool)
        else:
            (_, last_token) = context
            try:
                left_id = self._encode[last_token]  # Get the ID of the last token
            except KeyError as e:
                raise KeyError(
                    f"Last token {last_token!r} not found in encode map."
                ) from e

            mask = self._vectorized_conflicting_next_tokens(
                left_id
            )  # Get base mask from BPE rules

            # Apply overrides: Ensure overridden tokens are allowed (True)
            if left_id in self.overrides:
                override_ids = [oid for oid in self.overrides[left_id] if oid < self.V]
                mask[override_ids] = True

            eos_indices = [e for e in self.eos_token_ids if e < self.V]
            mask[eos_indices] = True
        return mask

    def make_derivation_table(self):
        # Initialize left and right child lookup tables
        self._left = [None] * self.V
        self._right = [None] * self.V

        # Populate _left and _right based on the ordered merges
        # Assumes self._merges is ordered by priority (highest priority first) because of the way we build it in extract_bpe_merges
        for u, v, uv in self._merges:
            # Only record the first (highest priority) merge that forms uv
            if self._left[uv] is None and self._right[uv] is None:
                self._left[uv] = u
                self._right[uv] = v

    def vectorize_spine(self, spine, max_spine_width):
        new_spine = [
            [s[i] if i < len(s) else -VERYLARGE for i in range(max_spine_width)]
            for s in spine
        ]
        return np.array(new_spine, dtype=np.int32)

    def _left_spine_table(self):
        "Closure of the left tables."
        max_width = 0
        left_spine = [None] * self.V
        left = self._left
        for i in range(self.V):
            spine = [VERYLARGE, i]
            x = i
            while True:
                x = left[x]
                if x is None:
                    break
                spine.append(x)
            spine.reverse()
            left_spine[i] = spine
            max_width = max(max_width, len(spine))
        return left_spine, max_width

    def _right_spine_table(self):
        "Closure of the right tables."
        max_width = 0
        right_spine = [None] * self.V
        right = self._right
        for i in range(self.V):
            spine = [VERYLARGE, i]
            x = i
            while True:
                x = right[x]
                if x is None:
                    break
                spine.append(x)
            spine.reverse()
            right_spine[i] = spine
            max_width = max(max_width, len(spine))
        return right_spine, max_width

    def set_overrides(self, model_name):
        if "gpt2" in model_name:
            for left, right in [(198, 198), (2637, 82)]:
                self.overrides[left].add(right)

    def _vectorized_conflicting_next_tokens(self, left: int):
        spine_left = self.__right_spine[left]

        L = len(spine_left) - 1  # inf padding

        mask = np.ones(self.V, dtype=bool)

        np_matrix = self.parent_l_matrix[spine_left[:L]].toarray()

        for i in range(L):
            lp = spine_left[i + 1]

            vector_k = np_matrix[i]
            # convert 0 in vector_k to VERYLARGE
            vector_k = np.where(vector_k != 0, vector_k - 1, VERYLARGE)

            conflict_mask = vector_k < VERYLARGE
            conflict_mask &= vector_k <= self.vector_rp
            conflict_mask &= vector_k < lp
            mask[self.indices[conflict_mask][:, 0]] = False

        return mask

    @classmethod
    def from_tokenizer(cls, tokenizer, eos_token_ids=None):
        _decode, _ = decode_vocab(tokenizer)
        if len(_decode) != len(set(_decode)):
            raise ValueError(
                "Duplicate byte sequences found in vocabulary. Cannot create unique byte->ID mapping (_encode)."
            )

        _merges = _extract_bpe_merges(tokenizer)

        # Build _encode (bytes -> token_id map) from _decode
        _encode = {b: i for i, b in enumerate(_decode) if b is not None}

        # Build _encode_byte (single byte -> token_id map)
        _encode_byte = [None] * 256
        for i in range(256):
            byte_val = bytes([i])
            if byte_val in _encode:
                _encode_byte[i] = _encode[byte_val]

        if not eos_token_ids:
            eos_token_ids = [tokenizer.eos_token_id]

        return cls(_merges, _encode, _decode, _encode_byte, eos_token_ids)


class CanonicalTokenization(Potential):
    """
    A custom potential that enforces canonical BPE tokenization.

    This potential ensures that tokens follow the canonical tokenization rules
    by using the FastCanonicalityFilterBPE under the hood.
    """

    def __init__(self, canonicality_filter):
        """
        Initialize the Canonical Potential

        Args:
            canonicality_filter (FastCanonicalityFilterBPE): An initialized FastCanonicalityFilterBPE instance.
        """
        # Store the pre-initialized filter and tokenizer
        self.canonicality_filter = canonicality_filter

        # IMPORTANT: In the base Potential class, EOS will be added to vocab automatically
        # So we should NOT add it ourselves to the vocabulary we pass to super().__init__
        vocabulary = self.canonicality_filter._decode
        super().__init__(vocabulary)

    @classmethod
    def from_llm(cls, llm):
        """
        Factory method to create CanonicalTokenization from a PromptedLLM instance.

        Args:
            llm (PromptedLLM): An instance of PromptedLLM containing the model and tokenizer.

        Returns:
            (CanonicalTokenization): An initialized CanonicalTokenization instance.
        """
        if not isinstance(llm, PromptedLLM):
            raise TypeError(
                f"Expected llm to be an instance of PromptedLLM, got {type(llm)}"
            )

        # Extract necessary components from llm
        tokenizer = llm.model.tokenizer
        eos_token_ids = llm.token_maps.eos_idxs
        model_name = tokenizer.name_or_path

        # Create the filter using its factory method
        canonicality_filter = FastCanonicalityFilterBPE.from_tokenizer(
            tokenizer, eos_token_ids
        )

        # Set overrides on the filter
        canonicality_filter.set_overrides(model_name)

        # Call __init__ with the created filter and tokenizer
        return cls(canonicality_filter)

    async def complete(self, context):
        """
        Assess if a complete sequence follows canonical tokenization.

        Args:
            context (list): Sequence of tokens

        Returns:
            (float): 0.0 if canonical, float('-inf') otherwise
        """
        # Empty sequences are considered canonical
        if not context:
            return 0.0

        # Check if the sequence is canonical
        is_canonical = self._check_canonicality(context)
        return 0.0 if is_canonical else float("-inf")

    async def prefix(self, context):
        """
        Assess if a prefix sequence could potentially extend to a canonical sequence.
        For canonicality, this is the same as complete.

        Args:
            context (list): Sequence of tokens

        Returns:
            (float): 0.0 if potentially canonical, float('-inf') otherwise
        """
        return await self.complete(context)

    async def logw_next(self, context):
        """
        Compute weights for each possible next token given the context.

        Args:
            context (list): Sequence of tokens

        Returns:
            (LazyWeights): Weights for each token in the vocabulary and EOS
        """
        # Get the prefix weight (to check if context itself is canonical)
        ctx_log_w = await self.prefix(context)

        if ctx_log_w == float("-inf"):
            raise ValueError("Context is non-canonical")
        else:
            if context:
                t = (None, context[-1])
                filter_mask = self.canonicality_filter(t)
            else:
                filter_mask = np.ones(len(self.canonicality_filter._decode), dtype=bool)

            # Create log weights directly instead of using np.log(filter_mask)
            # This is more efficient, avoids torch (with torch can't combine with other potentials!)
            logws_no_eos = np.where(filter_mask, 0.0, float("-inf")).astype(np.float32)

            # append eos to the logws, always allow eos.
            # NOTE: concat is because ._decode does not include eos while .vocab_eos does
            logws = np.concatenate([logws_no_eos, np.array([0.0], dtype=np.float32)])

        return self.make_lazy_weights(logws)

    def _check_canonicality(self, context):
        """
        Check if a sequence follows canonical tokenization.

        Args:
            context (list): Sequence of tokens

        Returns:
            (bool): True if the sequence is canonical, False otherwise
        """
        # If we're checking a single token, it's always canonical
        if len(context) <= 1:
            return True

        # Check all adjacent token pairs for canonicality
        for i in range(1, len(context)):
            prev_token = context[i - 1]
            current_token = context[i]

            # Format expected by the filter: (None, previous_token)
            t = (None, prev_token)
            mask = self.canonicality_filter(t)
            # print("percent of mask: ", np.sum(mask)*100 / len(mask))

            # Find token_id in the canonicality filter's vocabulary
            token_id = self.canonicality_filter._encode[current_token]
            if not mask[token_id]:
                return False

        return True
