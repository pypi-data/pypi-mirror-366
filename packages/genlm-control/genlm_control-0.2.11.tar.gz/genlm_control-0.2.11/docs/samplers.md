# Token Samplers

[TokenSamplers][genlm.control.sampler.token.TokenSampler]  are the objects that propose new tokens during generation. They generate individual tokens $x$ given a `context` sequence. Each sample $x$ is attached with a log importance weight $w$.[^1]

[^1]: Tokens samplers also return a log-probability which corresponds to the log-probability of all the random choices made by the sampler. It is returned for testing purposes and is not used during generation.

## Direct Token Sampling

The simplest token sampler is the [`DirectTokenSampler`][genlm.control.sampler.token.DirectTokenSampler], which samples directly from the normalized version of a potential's `logw_next` method:

```python
# Create a direct token sampler for a potential
sampler = DirectTokenSampler(potential)

# Sample a token
token, logw, logp = await sampler.sample(context)
```

`DirectTokenSampler` is efficient when the potential's `logw_next` method is efficient (e.g., for language models). However, for potentials with large vocabularies or expensive `logw_next` computations, other sampling strategies may be more appropriate.


## Adaptive Weighted Rejection Sampling

When attempting to sample from the product of a potential (e.g., a language model) and a *boolean* constraint potential (e.g., a [CFG][genlm.control.potential.built_in.wcfg] or [JSON schema][genlm.control.potential.built_in.json] potential), the most efficient and lowest variance sampler is [`AWRS`][genlm.control.sampler.token.AWRS].[^2] This framework is described in detail in [Lipkin et al. (2025)](https://arxiv.org/abs/2504.05410).

```python
# Create a AWRS token sampler from an llm and a cfg
token_sampler = AWRS(llm, cfg)
# Sample a token and weight
token, logw, _ = await token_sampler.sample(context)
```

[^2]: "Higher variance" refers to the variance of the estimator, which is influenced by the variance of the importance weights. When a sampler has high variance, the importance weights can vary dramatically across different samples, leading to unstable estimates in downstream tasks. While high-variance samplers may generate samples efficiently, they often require more samples to achieve the same level of accuracy as lower-variance alternatives.

## Set-based Token Sampling

A [`SetTokenSampler`][genlm.control.sampler.token.SetTokenSampler] samples tokens by first sampling a weighted subset of tokens using a [`SetSampler`][genlm.control.sampler.set.SetSampler], and then selects one token from the set proportional to its weight. These samplers are commonly used to sample tokens from a language model while enforcing non-boolean byte-level constraints. This algorithm is described in Appendix C of [Loula et al. (2025)](https://openreview.net/pdf?id=xoXn62FzD0).

### Set Samplers

SetTokenSamplers wrap a SetSampler, which is responsible for sampling a weighted subset of tokens. Currently, `genlm-control` provides two set samplers:

1. [`EagerSetSampler`][genlm.control.sampler.set.EagerSetSampler] - Eagerly samples a set of tokens by sampling one "subtoken" (e.g., byte) at a time.
2. [`TopKSetSampler`][genlm.control.sampler.set.TopKSetSampler] - Lazily enumerates the top $K$ tokens by weight and samples an additional "wildcard" token to ensure absolute continuity. This sampler is typically slower than `EagerSetSampler`.

Both of these set samplers are designed to work with two types of potentials:

1. An **iterable potential** which has a vocabulary of iterable tokens (e.g., over byte sequences)
2. An **item potential** which has a vocabulary of items which form the elements of iterable tokens (e.g., over individual bytes)

In common scenarios, the iterable potential is a language model and the item potential is a byte-level potential.

```python
# Create a set-based token sampler using a set sampler
set_sampler = EagerSetSampler(llm, fsa)
token_sampler = SetTokenSampler(set_sampler)

# Sample a token and weight
token, logw, _ = await token_sampler.sample(context)
```

### Factory methods

For convenience, we provide factory methods for creating set token samplers from potentials.

```python
from genlm.control.sampler import topk_token_sampler, eager_token_sampler

topk_sampler = topk_token_sampler(llm, fsa, K=10)

eager_sampler = eager_token_sampler(llm, fsa)
```

## Sampler Selection Guide for Controlled Generation

The following table provides general guidelines for selecting a sampler in the context of controlled generation from an LLM. Note that the best sampler may vary depending on the specific controlled generation task.

| Scenario | Recommended Sampler | Notes |
|----------|-------------------|--------|
| No token-level constraints | `DirectTokenSampler` | Basic LM sampling; used when all constraints are enforced using `critics` |
| Boolean constraints (e.g., FSA, CFG, JSON schema) | `AWRS` | Efficient, low-variance, and exact sampling from product of a LLM and constraint |
| Byte-level non-boolean constraints| `eager_token_sampler` | Generally less efficient than `AWRS`, but more flexible |

## Custom Token Samplers

It is also possible to implement custom token samplers by subclassing the [`TokenSampler`][genlm.control.sampler.token.TokenSampler] class and implementing the [`sample`][genlm.control.sampler.token.TokenSampler.sample] method. These implementations must satisfy the following contract.

### Token Sampler Contract

All token samplers in `genlm-control` must generate properly weighted samples with respect to a target potential's next-token weights $\pot(\cdot \mid \bm{x})$ given a context $\xx$:

A weighted sample $(x, w) \sim q(\cdot \mid \xx)$ is properly weighted with respect to $\pot(\cdot \mid \xx)$ if, for any function $f$,

$$
\mathbb{E}_{(x,w) \sim q(\cdot \mid \xx)}[w f(x)] = \sum_{x \in \A \cup \{\eos\}} f(x)\cdot\pot(x \mid \xx)
$$

where $\mathcal{A}$ is the vocabulary of the target potenital $\pot$.
