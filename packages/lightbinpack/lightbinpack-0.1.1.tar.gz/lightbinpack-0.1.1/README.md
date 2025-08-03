# LightBinPack

LightBinPack is a lightweight library for solving bin packing problems, implementing core algorithms in C++ and providing a Python interface, and has been optimized for bin packing algorithms in both pre-training and post-training scenarios for LLMs.

## Installation

```bash
pip install lightbinpack
```

If you want to use the latest features, you can install the development version from GitHub:

```bash
pip install git+https://github.com/TechxGenus/LightBinPack.git
```

## Usage

Here is a simple example:

```python
from lightbinpack import pack

lengths = [20, 20, 10, 10, 10, 10]
batch_max_length = 40

# For linear attention or disabled document mask
results = pack(lengths, batch_max_length, variant="linear")
print(results)

# For attention with document mask enabled
results = pack(lengths, batch_max_length, variant="square", dp_size=2)
print(results)
```

The library also includes optimizations for heterogeneous nodes, prefix sharing, and context parallelism scenarios. You can find more examples and documentation in the `docs` and `examples` directories.

## Acknowledgements

- [Multipack Sampler](https://github.com/imoneoi/multipack_sampler)
- [OBFD](https://arxiv.org/abs/2404.10830)
- Claude and GPT(o1)

## Contribution

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.
