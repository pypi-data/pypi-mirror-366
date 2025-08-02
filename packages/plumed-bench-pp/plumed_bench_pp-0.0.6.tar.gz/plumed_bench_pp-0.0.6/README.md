# Plumed-Bench-PP

[![PyPI - Version](https://img.shields.io/pypi/v/plumed-bench-pp.svg)](https://pypi.org/project/plumed-bench-pp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/plumed-bench-pp.svg)](https://pypi.org/project/plumed-bench-pp)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Documentation Status](https://readthedocs.org/projects/plumed-bench-pp/badge/?version=latest)](https://plumed-bench-pp.readthedocs.io/en/latest/?badge=latest)

A small toolset for postprocess `plumed benchmark` and the plumed time report at the end of the simulations

as now it can extract a dict from a file like:
```
BENCH:  Kernel:      this
BENCH:  Input:       plumed.dat
BENCH:  Comparative: 1.000 +- 0.000
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.214297     0.214297     0.214297     0.214297
BENCH:  B0 First step                                      1     0.062736     0.062736     0.062736     0.062736
BENCH:  B1 Warm-up                                       199    12.618833     0.063411     0.055884     0.076860
BENCH:  B2 Calculation part 1                            400    25.567659     0.063919     0.054110     0.113234
BENCH:  B3 Calculation part 2                            400    25.594014     0.063985     0.059516     0.102646
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1    64.054325    64.054325    64.054325    64.054325
PLUMED: 1 Prepare dependencies                          1000     0.003443     0.000003     0.000001     0.000013
PLUMED: 2 Sharing data                                  1000     0.305915     0.000306     0.000015     0.037867
PLUMED: 3 Waiting for data                              1000     0.003051     0.000003     0.000002     0.000013
PLUMED: 4 Calculating (forward loop)                    1000    63.459357     0.063459     0.054012     0.091577
PLUMED: 5 Applying (backward loop)                      1000     0.008520     0.000009     0.000005     0.000044
PLUMED: 6 Update                                        1000     0.043188     0.000043     0.000031     0.000080
BENCH:  
BENCH:  Kernel:      ../../src/lib/install/libplumedKernel.so
BENCH:  Input:       plumed.dat
BENCH:  Comparative: 0.941 +- 0.002
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.216190     0.216190     0.216190     0.216190
BENCH:  B0 First step                                      1     0.058967     0.058967     0.058967     0.058967
BENCH:  B1 Warm-up                                       199    11.983512     0.060219     0.056412     0.102643
BENCH:  B2 Calculation part 1                            400    24.035510     0.060089     0.056539     0.113900
BENCH:  B3 Calculation part 2                            400    24.084369     0.060211     0.056866     0.097184
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1    60.373083    60.373083    60.373083    60.373083
PLUMED: 1 Prepare dependencies                          1000     0.003351     0.000003     0.000001     0.000014
PLUMED: 2 Sharing data                                  1000     0.329323     0.000329     0.000015     0.032672
PLUMED: 3 Waiting for data                              1000     0.003078     0.000003     0.000001     0.000013
PLUMED: 4 Calculating (forward loop)                    1000    59.752459     0.059752     0.056310     0.083841
PLUMED: 5 Applying (backward loop)                      1000     0.008900     0.000009     0.000006     0.000034
PLUMED: 6 Update                                        1000     0.043015     0.000043     0.000032     0.000239
```

or 
```
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1    60.373083    60.373083    60.373083    60.373083
PLUMED: 1 Prepare dependencies                          1000     0.003351     0.000003     0.000001     0.000014
PLUMED: 2 Sharing data                                  1000     0.329323     0.000329     0.000015     0.032672
PLUMED: 3 Waiting for data                              1000     0.003078     0.000003     0.000001     0.000013
PLUMED: 4 Calculating (forward loop)                    1000    59.752459     0.059752     0.056310     0.083841
PLUMED: 5 Applying (backward loop)                      1000     0.008900     0.000009     0.000006     0.000034
PLUMED: 6 Update                                        1000     0.043015     0.000043     0.000032     0.000239
```

----

One way of extracting the timing from the ouput of the benchmark is:
`awk '/BENCH:  Kernel: /,EOF' benchmark.out > times_benchmark.out`

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install plumed-bench-pp
```

## License

`plumed-bench-pp` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
