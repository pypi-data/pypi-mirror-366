# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

import pytest

from plumed_bench_pp.types import BenchmarkRow, BenchmarkRun, BenchmarkSettings, KernelBenchmark

output_noheader = {
    "file": r"""PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: b52ce2675-dirty) compiled on Jul 10 2024 at 11:30:47
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /plumed2-dev/
PLUMED: LibraryPath: /plumed2-dev/src/lib/libplumedKernel.so
PLUMED: For installed feature, see /src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: plumed.dat
PLUMED: Action DEBUG
PLUMED:   with label @0
PLUMED:   with stride 1
PLUMED:   Detailed timing on
PLUMED:   on plumed log file
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @3
PLUMED:   with stride 1
PLUMED: END FILE: plumed.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
BENCH:  Starting MD loop
BENCH:  Use CTRL+C to stop at any time and collect timers (not working in MPI runs)
BENCH:  Warm-up completed
BENCH:  60% completed
BENCH:  Single run, skipping comparative analysis
BENCH:  
BENCH:  Kernel:      this
BENCH:  Input:       plumed.dat
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001654     0.001654     0.001654     0.001654
BENCH:  B0 First step                                      1     0.001588     0.001588     0.001588     0.001588
BENCH:  B1 Warm-up                                       999     1.630039     0.001632     0.001513     0.002375
BENCH:  B2 Calculation part 1                           2000     3.219555     0.001610     0.001502     0.002428
BENCH:  B3 Calculation part 2                           2000     3.110648     0.001555     0.001491     0.002460
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     7.959897     7.959897     7.959897     7.959897
PLUMED: 1 Prepare dependencies                          5000     0.002370     0.000000     0.000000     0.000009
PLUMED: 2 Sharing data                                  5000     0.010464     0.000002     0.000001     0.000024
PLUMED: 3 Waiting for data                              5000     0.003127     0.000001     0.000000     0.000008
PLUMED: 4 Calculating (forward loop)                    5000     7.868715     0.001574     0.001479     0.002362
PLUMED: 4A  1 posx                                      5000     0.000612     0.000000     0.000000     0.000004
PLUMED: 4A  2 posy                                      5000     0.000279     0.000000     0.000000     0.000006
PLUMED: 4A  3 posz                                      5000     0.000265     0.000000     0.000000     0.000004
PLUMED: 4A  4 Masses                                    5000     0.000288     0.000000     0.000000     0.000005
PLUMED: 4A  5 Charges                                   5000     0.000294     0.000000     0.000000     0.000007
PLUMED: 4A  6 Box                                       5000     0.000342     0.000000     0.000000     0.000008
PLUMED: 4A  7 benchmarks                                5000     0.000406     0.000000     0.000000     0.000001
PLUMED: 4A  8 @0                                        5000     0.000226     0.000000     0.000000     0.000001
PLUMED: 4A  9 cpu                                       5000     7.849295     0.001570     0.001476     0.002354
PLUMED: 4A 10 @2                                        5000     0.000440     0.000000     0.000000     0.000004
PLUMED: 4A 11 @3                                        5000     0.000314     0.000000     0.000000     0.000007
PLUMED: 5 Applying (backward loop)                      5000     0.017107     0.000003     0.000003     0.000053
PLUMED: 5A  0 @3                                        5000     0.000255     0.000000     0.000000     0.000006
PLUMED: 5A  1 @2                                        5000     0.000123     0.000000     0.000000     0.000003
PLUMED: 5A  2 cpu                                       5000     0.000516     0.000000     0.000000     0.000006
PLUMED: 5A  3 @0                                        5000     0.000331     0.000000     0.000000     0.000006
PLUMED: 5A  4 benchmarks                                5000     0.002406     0.000000     0.000000     0.000007
PLUMED: 5A  5 Box                                       5000     0.000468     0.000000     0.000000     0.000006
PLUMED: 5A  6 Charges                                   5000     0.000212     0.000000     0.000000     0.000001
PLUMED: 5A  7 Masses                                    5000     0.000161     0.000000     0.000000     0.000006
PLUMED: 5A  8 posz                                      5000     0.000119     0.000000     0.000000     0.000005
PLUMED: 5A  9 posy                                      5000     0.000127     0.000000     0.000000     0.000000
PLUMED: 5A 10 posx                                      5000     0.000130     0.000000     0.000000     0.000000
PLUMED: 5B Update forces                                5000     0.000119     0.000000     0.000000     0.000002
PLUMED: 6 Update                                        5000     0.041863     0.000008     0.000005     0.000098
""",
    "parsed": BenchmarkRun(
        BenchmarkSettings(),
        {
            "this+plumed.dat": KernelBenchmark(
                kernel="this",
                input="plumed.dat",
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Average": 0.001654,
                            "Cycles": 1,
                            "Maximum": 0.001654,
                            "Minimum": 0.001654,
                            "Total": 0.001654,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Average": 0.001588,
                            "Cycles": 1,
                            "Maximum": 0.001588,
                            "Minimum": 0.001588,
                            "Total": 0.001588,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Average": 0.001632,
                            "Cycles": 999,
                            "Maximum": 0.002375,
                            "Minimum": 0.001513,
                            "Total": 1.630039,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Average": 0.00161,
                            "Cycles": 2000,
                            "Maximum": 0.002428,
                            "Minimum": 0.001502,
                            "Total": 3.219555,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Average": 0.001555,
                            "Cycles": 2000,
                            "Maximum": 0.00246,
                            "Minimum": 0.001491,
                            "Total": 3.110648,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 7.959897,
                            "Average": 7.959897,
                            "Minimum": 7.959897,
                            "Maximum": 7.959897,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.00237,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 9e-06,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.010464,
                            "Average": 2e-06,
                            "Minimum": 1e-06,
                            "Maximum": 2.4e-05,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.003127,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 8e-06,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 7.868715,
                            "Average": 0.001574,
                            "Minimum": 0.001479,
                            "Maximum": 0.002362,
                        }
                    ),
                    "4A  1 posx": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000612,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 4e-06,
                        }
                    ),
                    "4A  2 posy": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000279,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "4A  3 posz": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000265,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 4e-06,
                        }
                    ),
                    "4A  4 Masses": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000288,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 5e-06,
                        }
                    ),
                    "4A  5 Charges": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000294,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 7e-06,
                        }
                    ),
                    "4A  6 Box": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000342,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 8e-06,
                        }
                    ),
                    "4A  7 benchmarks": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000406,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 1e-06,
                        }
                    ),
                    "4A  8 @0": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000226,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 1e-06,
                        }
                    ),
                    "4A  9 cpu": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 7.849295,
                            "Average": 0.00157,
                            "Minimum": 0.001476,
                            "Maximum": 0.002354,
                        }
                    ),
                    "4A 10 @2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.00044,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 4e-06,
                        }
                    ),
                    "4A 11 @3": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000314,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 7e-06,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.017107,
                            "Average": 3e-06,
                            "Minimum": 3e-06,
                            "Maximum": 5.3e-05,
                        }
                    ),
                    "5A  0 @3": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000255,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "5A  1 @2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000123,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 3e-06,
                        }
                    ),
                    "5A  2 cpu": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000516,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "5A  3 @0": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000331,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "5A  4 benchmarks": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.002406,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 7e-06,
                        }
                    ),
                    "5A  5 Box": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000468,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "5A  6 Charges": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000212,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 1e-06,
                        }
                    ),
                    "5A  7 Masses": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000161,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 6e-06,
                        }
                    ),
                    "5A  8 posz": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000119,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 5e-06,
                        }
                    ),
                    "5A  9 posy": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000127,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 0.0,
                        }
                    ),
                    "5A 10 posx": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.00013,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 0.0,
                        }
                    ),
                    "5B Update forces": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.000119,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 2e-06,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 5000,
                            "Total": 0.041863,
                            "Average": 8e-06,
                            "Minimum": 5e-06,
                            "Maximum": 9.8e-05,
                        }
                    ),
                },
            )
        },
    ),
    "colums": {
        "this+plumed.dat": {
            "A Initialization": [1, 0.001654, 0.001654, 0.001654, 0.001654],
            "B0 First step": [1, 0.001588, 0.001588, 0.001588, 0.001588],
            "B1 Warm-up": [999, 1.630039, 0.001632, 0.001513, 0.002375],
            "B2 Calculation part 1": [2000, 3.219555, 0.001610, 0.001502, 0.002428],
            "B3 Calculation part 2": [2000, 3.110648, 0.001555, 0.001491, 0.002460],
            "Plumed": [1, 7.959897, 7.959897, 7.959897, 7.959897],
            "1 Prepare dependencies": [5000, 0.002370, 0.000000, 0.000000, 0.000009],
            "2 Sharing data": [5000, 0.010464, 0.000002, 0.000001, 0.000024],
            "3 Waiting for data": [5000, 0.003127, 0.000001, 0.000000, 0.000008],
            "4 Calculating (forward loop)": [
                5000,
                7.868715,
                0.001574,
                0.001479,
                0.002362,
            ],
            "4A  1 posx": [5000, 0.000612, 0.000000, 0.000000, 0.000004],
            "4A  2 posy": [5000, 0.000279, 0.000000, 0.000000, 0.000006],
            "4A  3 posz": [5000, 0.000265, 0.000000, 0.000000, 0.000004],
            "4A  4 Masses": [5000, 0.000288, 0.000000, 0.000000, 0.000005],
            "4A  5 Charges": [5000, 0.000294, 0.000000, 0.000000, 0.000007],
            "4A  6 Box": [5000, 0.000342, 0.000000, 0.000000, 0.000008],
            "4A  7 benchmarks": [5000, 0.000406, 0.000000, 0.000000, 0.000001],
            "4A  8 @0": [5000, 0.000226, 0.000000, 0.000000, 0.000001],
            "4A  9 cpu": [5000, 7.849295, 0.001570, 0.001476, 0.002354],
            "4A 10 @2": [5000, 0.000440, 0.000000, 0.000000, 0.000004],
            "4A 11 @3": [5000, 0.000314, 0.000000, 0.000000, 0.000007],
            "5 Applying (backward loop)": [
                5000,
                0.017107,
                0.000003,
                0.000003,
                0.000053,
            ],
            "5A  0 @3": [5000, 0.000255, 0.000000, 0.000000, 0.000006],
            "5A  1 @2": [5000, 0.000123, 0.000000, 0.000000, 0.000003],
            "5A  2 cpu": [5000, 0.000516, 0.000000, 0.000000, 0.000006],
            "5A  3 @0": [5000, 0.000331, 0.000000, 0.000000, 0.000006],
            "5A  4 benchmarks": [5000, 0.002406, 0.000000, 0.000000, 0.000007],
            "5A  5 Box": [5000, 0.000468, 0.000000, 0.000000, 0.000006],
            "5A  6 Charges": [5000, 0.000212, 0.000000, 0.000000, 0.000001],
            "5A  7 Masses": [5000, 0.000161, 0.000000, 0.000000, 0.000006],
            "5A  8 posz": [5000, 0.000119, 0.000000, 0.000000, 0.000005],
            "5A  9 posy": [5000, 0.000127, 0.000000, 0.000000, 0.000000],
            "5A 10 posx": [5000, 0.000130, 0.000000, 0.000000, 0.000000],
            "5B Update forces": [5000, 0.000119, 0.000000, 0.000000, 0.000002],
            "6 Update": [5000, 0.041863, 0.000008, 0.000005, 0.000098],
        }
    },
}

output_1k2f = {
    "file": r"""BENCH:  Welcome to PLUMED benchmark
BENCH:  Using --kernel=this
BENCH:  Using --plumed=Coord.dat:CoordNL.dat
BENCH:  Using --nsteps=2500
BENCH:  Using --natoms=500
BENCH:  Using --maxtime=-1
BENCH:  Using --domain-decomposition
BENCH:  Using --sleep=0
BENCH:  Using --atom-distribution=line
BENCH:  Initializing the setup of the kernel(s)
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /scratch/drapetti/repos/plumed2-dev/
PLUMED: LibraryPath: /u/d/drapetti/scratch/repos/plumed2-dev/src/lib/libplumedKernel.so
PLUMED: For installed feature, see /scratch/drapetti/repos/plumed2-dev//src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: CoordNL.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   using neighbor lists with
PLUMED:   update every 10 steps and cutoff 1.100000
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: CoordNL.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /scratch/drapetti/repos/plumed2-dev/
PLUMED: LibraryPath: /u/d/drapetti/scratch/repos/plumed2-dev/src/lib/libplumedKernel.so
PLUMED: For installed feature, see /scratch/drapetti/repos/plumed2-dev//src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: Coord.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: Coord.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
BENCH:  Starting MD loop
BENCH:  Use CTRL+C to stop at any time and collect timers (not working in MPI runs)
BENCH:  Warm-up completed
BENCH:  60% completed
BENCH:  Running comparative analysis, 1600 blocks with size 1
BENCH:  
BENCH:  Kernel:      this
BENCH:  Input:       Coord.dat
BENCH:  Comparative: 1.000 +- 0.000
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001307     0.001307     0.001307     0.001307
BENCH:  B0 First step                                      1     0.001008     0.001008     0.001008     0.001008
BENCH:  B1 Warm-up                                       399     0.431797     0.001082     0.000986     0.001924
BENCH:  B2 Calculation part 1                            800     0.838702     0.001048     0.000986     0.001809
BENCH:  B3 Calculation part 2                            800     0.847325     0.001059     0.000983     0.001823
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     2.118805     2.118805     2.118805     2.118805
PLUMED: 1 Prepare dependencies                          2000     0.000742     0.000000     0.000000     0.000004
PLUMED: 2 Sharing data                                  2000     0.004366     0.000002     0.000001     0.000098
PLUMED: 3 Waiting for data                              2000     0.001090     0.000001     0.000000     0.000008
PLUMED: 4 Calculating (forward loop)                    2000     2.086534     0.001043     0.000972     0.001885
PLUMED: 5 Applying (backward loop)                      2000     0.001861     0.000001     0.000001     0.000060
PLUMED: 6 Update                                        2000     0.017886     0.000009     0.000005     0.000068
BENCH:  
BENCH:  Kernel:      this
BENCH:  Input:       CoordNL.dat
BENCH:  Comparative: 0.125 +- 0.007
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001542     0.001542     0.001542     0.001542
BENCH:  B0 First step                                      1     0.001072     0.001072     0.001072     0.001072
BENCH:  B1 Warm-up                                       399     0.053350     0.000134     0.000021     0.001604
BENCH:  B2 Calculation part 1                            800     0.105425     0.000132     0.000021     0.001481
BENCH:  B3 Calculation part 2                            800     0.104763     0.000131     0.000021     0.001653
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     0.264850     0.264850     0.264850     0.264850
PLUMED: 1 Prepare dependencies                          2000     0.024299     0.000012     0.000007     0.000069
PLUMED: 2 Sharing data                                  2000     0.004324     0.000002     0.000001     0.000017
PLUMED: 3 Waiting for data                              2000     0.001242     0.000001     0.000000     0.000005
PLUMED: 4 Calculating (forward loop)                    2000     0.215402     0.000108     0.000005     0.001609
PLUMED: 5 Applying (backward loop)                      2000     0.001299     0.000001     0.000000     0.000124
PLUMED: 6 Update                                        2000     0.011222     0.000006     0.000003     0.000057
""",
    "parsed": BenchmarkRun(
        BenchmarkSettings(
            kernels=["this"],
            inputs=["Coord.dat", "CoordNL.dat"],
            steps=2500,
            atoms=500,
            maxtime=-1.0,
            sleep=0.0,
            atom_distribution="line",
            domain_decomposition=True,
        ),
        {
            "this+Coord.dat": KernelBenchmark(
                kernel="this",
                input="Coord.dat",
                compare={"fraction": 1.0, "error": 0.0},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001307,
                            "Average": 0.001307,
                            "Minimum": 0.001307,
                            "Maximum": 0.001307,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001008,
                            "Average": 0.001008,
                            "Minimum": 0.001008,
                            "Maximum": 0.001008,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 399,
                            "Total": 0.431797,
                            "Average": 0.001082,
                            "Minimum": 0.000986,
                            "Maximum": 0.001924,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.838702,
                            "Average": 0.001048,
                            "Minimum": 0.000986,
                            "Maximum": 0.001809,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.847325,
                            "Average": 0.001059,
                            "Minimum": 0.000983,
                            "Maximum": 0.001823,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 2.118805,
                            "Average": 2.118805,
                            "Minimum": 2.118805,
                            "Maximum": 2.118805,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.000742,
                            "Average": 0.0,
                            "Minimum": 0.0,
                            "Maximum": 4e-06,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.004366,
                            "Average": 2e-06,
                            "Minimum": 1e-06,
                            "Maximum": 9.8e-05,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.00109,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 8e-06,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 2.086534,
                            "Average": 0.001043,
                            "Minimum": 0.000972,
                            "Maximum": 0.001885,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001861,
                            "Average": 1e-06,
                            "Minimum": 1e-06,
                            "Maximum": 6e-05,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.017886,
                            "Average": 9e-06,
                            "Minimum": 5e-06,
                            "Maximum": 6.8e-05,
                        }
                    ),
                },
            ),
            "this+CoordNL.dat": KernelBenchmark(
                kernel="this",
                input="CoordNL.dat",
                compare={"fraction": 0.125, "error": 0.007},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001542,
                            "Average": 0.001542,
                            "Minimum": 0.001542,
                            "Maximum": 0.001542,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001072,
                            "Average": 0.001072,
                            "Minimum": 0.001072,
                            "Maximum": 0.001072,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 399,
                            "Total": 0.05335,
                            "Average": 0.000134,
                            "Minimum": 2.1e-05,
                            "Maximum": 0.001604,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.105425,
                            "Average": 0.000132,
                            "Minimum": 2.1e-05,
                            "Maximum": 0.001481,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.104763,
                            "Average": 0.000131,
                            "Minimum": 2.1e-05,
                            "Maximum": 0.001653,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.26485,
                            "Average": 0.26485,
                            "Minimum": 0.26485,
                            "Maximum": 0.26485,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.024299,
                            "Average": 1.2e-05,
                            "Minimum": 7e-06,
                            "Maximum": 6.9e-05,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.004324,
                            "Average": 2e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.7e-05,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001242,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 5e-06,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.215402,
                            "Average": 0.000108,
                            "Minimum": 5e-06,
                            "Maximum": 0.001609,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001299,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 0.000124,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.011222,
                            "Average": 6e-06,
                            "Minimum": 3e-06,
                            "Maximum": 5.7e-05,
                        }
                    ),
                },
            ),
        },
    ),
    "colums": {
        "this+Coord.dat": {
            "A Initialization": [1, 0.001307, 0.001307, 0.001307, 0.001307],
            "B0 First step": [1, 0.001008, 0.001008, 0.001008, 0.001008],
            "B1 Warm-up": [399, 0.431797, 0.001082, 0.000986, 0.001924],
            "B2 Calculation part 1": [800, 0.838702, 0.001048, 0.000986, 0.001809],
            "B3 Calculation part 2": [800, 0.847325, 0.001059, 0.000983, 0.001823],
            "Plumed": [1, 2.118805, 2.118805, 2.118805, 2.118805],
            "1 Prepare dependencies": [2000, 0.000742, 0.000000, 0.000000, 0.000004],
            "2 Sharing data": [2000, 0.004366, 0.000002, 0.000001, 0.000098],
            "3 Waiting for data": [2000, 0.001090, 0.000001, 0.000000, 0.000008],
            "4 Calculating (forward loop)": [
                2000,
                2.086534,
                0.001043,
                0.000972,
                0.001885,
            ],
            "5 Applying (backward loop)": [
                2000,
                0.001861,
                0.000001,
                0.000001,
                0.000060,
            ],
            "6 Update": [2000, 0.017886, 0.000009, 0.000005, 0.000068],
        },
        "this+CoordNL.dat": {
            "A Initialization": [1, 0.001542, 0.001542, 0.001542, 0.001542],
            "B0 First step": [1, 0.001072, 0.001072, 0.001072, 0.001072],
            "B1 Warm-up": [399, 0.053350, 0.000134, 0.000021, 0.001604],
            "B2 Calculation part 1": [800, 0.105425, 0.000132, 0.000021, 0.001481],
            "B3 Calculation part 2": [800, 0.104763, 0.000131, 0.000021, 0.001653],
            "Plumed": [1, 0.264850, 0.264850, 0.264850, 0.264850],
            "1 Prepare dependencies": [2000, 0.024299, 0.000012, 0.000007, 0.000069],
            "2 Sharing data": [2000, 0.004324, 0.000002, 0.000001, 0.000017],
            "3 Waiting for data": [2000, 0.001242, 0.000001, 0.000000, 0.000005],
            "4 Calculating (forward loop)": [
                2000,
                0.215402,
                0.000108,
                0.000005,
                0.001609,
            ],
            "5 Applying (backward loop)": [
                2000,
                0.001299,
                0.000001,
                0.000000,
                0.000124,
            ],
            "6 Update": [2000, 0.011222, 0.000006, 0.000003, 0.000057],
        },
    },
}

output_2k1f = {
    "file": r"""BENCH:  Welcome to PLUMED benchmark
BENCH:  Using --kernel=this:../../src/lib/install/libplumedKernel.so
BENCH:  Using --plumed=Coord.dat
BENCH:  Using --nsteps=2000
BENCH:  Using --natoms=500
BENCH:  Using --maxtime=-1
BENCH:  Using --sleep=0
BENCH:  Using --atom-distribution=line
BENCH:  Using --shuffled
BENCH:  Initializing the setup of the kernel(s)
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /usr/local/lib/plumed
PLUMED: LibraryPath: ../../src/lib/install/libplumedKernel.so
PLUMED: For installed feature, see /usr/local/lib/plumed/src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: Coord.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: Coord.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /scratch/drapetti/repos/plumed2-dev/
PLUMED: LibraryPath: /u/d/drapetti/scratch/repos/plumed2-dev/src/lib/libplumedKernel.so
PLUMED: For installed feature, see /scratch/drapetti/repos/plumed2-dev//src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: Coord.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: Coord.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
BENCH:  Starting MD loop
BENCH:  Use CTRL+C to stop at any time and collect timers (not working in MPI runs)
BENCH:  Warm-up completed
BENCH:  60% completed
BENCH:  Running comparative analysis, 1600 blocks with size 1
BENCH:  
BENCH:  Kernel:      this
BENCH:  Input:       Coord.dat
BENCH:  Comparative: 1.000 +- 0.000
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001329     0.001329     0.001329     0.001329
BENCH:  B0 First step                                      1     0.001004     0.001004     0.001004     0.001004
BENCH:  B1 Warm-up                                       399     0.412732     0.001034     0.000967     0.001826
BENCH:  B2 Calculation part 1                            800     0.817150     0.001021     0.000976     0.001606
BENCH:  B3 Calculation part 2                            800     0.838765     0.001048     0.000977     0.001706
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     2.069485     2.069485     2.069485     2.069485
PLUMED: 1 Prepare dependencies                          2000     0.001352     0.000001     0.000000     0.000016
PLUMED: 2 Sharing data                                  2000     0.004684     0.000002     0.000001     0.000032
PLUMED: 3 Waiting for data                              2000     0.001436     0.000001     0.000000     0.000009
PLUMED: 4 Calculating (forward loop)                    2000     2.034346     0.001017     0.000952     0.001778
PLUMED: 5 Applying (backward loop)                      2000     0.001992     0.000001     0.000001     0.000012
PLUMED: 6 Update                                        2000     0.016534     0.000008     0.000005     0.000161
BENCH:  
BENCH:  Kernel:      ../../src/lib/install/libplumedKernel.so
BENCH:  Input:       Coord.dat
BENCH:  Comparative: 1.021 +- 0.003
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001409     0.001409     0.001409     0.001409
BENCH:  B0 First step                                      1     0.001141     0.001141     0.001141     0.001141
BENCH:  B1 Warm-up                                       399     0.420014     0.001053     0.000993     0.001765
BENCH:  B2 Calculation part 1                            800     0.836896     0.001046     0.000999     0.001651
BENCH:  B3 Calculation part 2                            800     0.852747     0.001066     0.001000     0.001831
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     2.109832     2.109832     2.109832     2.109832
PLUMED: 1 Prepare dependencies                          2000     0.001274     0.000001     0.000000     0.000011
PLUMED: 2 Sharing data                                  2000     0.004684     0.000002     0.000001     0.000042
PLUMED: 3 Waiting for data                              2000     0.001590     0.000001     0.000000     0.000011
PLUMED: 4 Calculating (forward loop)                    2000     2.074114     0.001037     0.000980     0.001722
PLUMED: 5 Applying (backward loop)                      2000     0.001959     0.000001     0.000001     0.000016
PLUMED: 6 Update                                        2000     0.016623     0.000008     0.000004     0.000127
""",
    "parsed": BenchmarkRun(
        BenchmarkSettings(
            kernels=["this", "../../src/lib/install/libplumedKernel.so"],
            inputs=["Coord.dat"],
            steps=2000,
            atoms=500,
            maxtime=-1.0,
            sleep=0.0,
            atom_distribution="line",
            shuffled=True,
        ),
        {
            "this+Coord.dat": KernelBenchmark(
                kernel="this",
                input="Coord.dat",
                compare={"fraction": 1.0, "error": 0.0},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001329,
                            "Average": 0.001329,
                            "Minimum": 0.001329,
                            "Maximum": 0.001329,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001004,
                            "Average": 0.001004,
                            "Minimum": 0.001004,
                            "Maximum": 0.001004,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 399,
                            "Total": 0.412732,
                            "Average": 0.001034,
                            "Minimum": 0.000967,
                            "Maximum": 0.001826,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.81715,
                            "Average": 0.001021,
                            "Minimum": 0.000976,
                            "Maximum": 0.001606,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.838765,
                            "Average": 0.001048,
                            "Minimum": 0.000977,
                            "Maximum": 0.001706,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 2.069485,
                            "Average": 2.069485,
                            "Minimum": 2.069485,
                            "Maximum": 2.069485,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001352,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 1.6e-05,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.004684,
                            "Average": 2e-06,
                            "Minimum": 1e-06,
                            "Maximum": 3.2e-05,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001436,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 9e-06,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 2.034346,
                            "Average": 0.001017,
                            "Minimum": 0.000952,
                            "Maximum": 0.001778,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001992,
                            "Average": 1e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.2e-05,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.016534,
                            "Average": 8e-06,
                            "Minimum": 5e-06,
                            "Maximum": 0.000161,
                        }
                    ),
                },
            ),
            "../../src/lib/install/libplumedKernel.so+Coord.dat": KernelBenchmark(
                kernel="../../src/lib/install/libplumedKernel.so",
                input="Coord.dat",
                compare={"fraction": 1.021, "error": 0.003},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001409,
                            "Average": 0.001409,
                            "Minimum": 0.001409,
                            "Maximum": 0.001409,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.001141,
                            "Average": 0.001141,
                            "Minimum": 0.001141,
                            "Maximum": 0.001141,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 399,
                            "Total": 0.420014,
                            "Average": 0.001053,
                            "Minimum": 0.000993,
                            "Maximum": 0.001765,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.836896,
                            "Average": 0.001046,
                            "Minimum": 0.000999,
                            "Maximum": 0.001651,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 800,
                            "Total": 0.852747,
                            "Average": 0.001066,
                            "Minimum": 0.001,
                            "Maximum": 0.001831,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 2.109832,
                            "Average": 2.109832,
                            "Minimum": 2.109832,
                            "Maximum": 2.109832,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001274,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 1.1e-05,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.004684,
                            "Average": 2e-06,
                            "Minimum": 1e-06,
                            "Maximum": 4.2e-05,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.00159,
                            "Average": 1e-06,
                            "Minimum": 0.0,
                            "Maximum": 1.1e-05,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 2.074114,
                            "Average": 0.001037,
                            "Minimum": 0.00098,
                            "Maximum": 0.001722,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.001959,
                            "Average": 1e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.6e-05,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 2000,
                            "Total": 0.016623,
                            "Average": 8e-06,
                            "Minimum": 4e-06,
                            "Maximum": 0.000127,
                        }
                    ),
                },
            ),
        },
    ),
    "colums": {
        "this+Coord.dat": {
            "A Initialization": [1, 0.001329, 0.001329, 0.001329, 0.001329],
            "B0 First step": [1, 0.001004, 0.001004, 0.001004, 0.001004],
            "B1 Warm-up": [399, 0.412732, 0.001034, 0.000967, 0.001826],
            "B2 Calculation part 1": [800, 0.817150, 0.001021, 0.000976, 0.001606],
            "B3 Calculation part 2": [800, 0.838765, 0.001048, 0.000977, 0.001706],
            "Plumed": [1, 2.069485, 2.069485, 2.069485, 2.069485],
            "1 Prepare dependencies": [2000, 0.001352, 0.000001, 0.000000, 0.000016],
            "2 Sharing data": [2000, 0.004684, 0.000002, 0.000001, 0.000032],
            "3 Waiting for data": [2000, 0.001436, 0.000001, 0.000000, 0.000009],
            "4 Calculating (forward loop)": [
                2000,
                2.034346,
                0.001017,
                0.000952,
                0.001778,
            ],
            "5 Applying (backward loop)": [
                2000,
                0.001992,
                0.000001,
                0.000001,
                0.000012,
            ],
            "6 Update": [2000, 0.016534, 0.000008, 0.000005, 0.000161],
        },
        "../../src/lib/install/libplumedKernel.so+Coord.dat": {
            "A Initialization": [1, 0.001409, 0.001409, 0.001409, 0.001409],
            "B0 First step": [1, 0.001141, 0.001141, 0.001141, 0.001141],
            "B1 Warm-up": [399, 0.420014, 0.001053, 0.000993, 0.001765],
            "B2 Calculation part 1": [800, 0.836896, 0.001046, 0.000999, 0.001651],
            "B3 Calculation part 2": [800, 0.852747, 0.001066, 0.001000, 0.001831],
            "Plumed": [1, 2.109832, 2.109832, 2.109832, 2.109832],
            "1 Prepare dependencies": [2000, 0.001274, 0.000001, 0.000000, 0.000011],
            "2 Sharing data": [2000, 0.004684, 0.000002, 0.000001, 0.000042],
            "3 Waiting for data": [2000, 0.001590, 0.000001, 0.000000, 0.000011],
            "4 Calculating (forward loop)": [
                2000,
                2.074114,
                0.001037,
                0.000980,
                0.001722,
            ],
            "5 Applying (backward loop)": [
                2000,
                0.001959,
                0.000001,
                0.000001,
                0.000016,
            ],
            "6 Update": [2000, 0.016623, 0.000008, 0.000004, 0.000127],
        },
    },
}

output_2k1f_override = {
    "file": r"""BENCH:  Welcome to PLUMED benchmark
BENCH:  Using --kernel=this:../../src/lib/install/libplumedKernel.so
BENCH:  Using --plumed=Coord.dat
BENCH:  Using --nsteps=2000
BENCH:  Using --natoms=5
BENCH:  Using --maxtime=-1
BENCH:  Using --sleep=0
BENCH:  Using --atom-distribution=line
BENCH:  Using --shuffled
BENCH:  Distribution overrode --natoms, Using --natoms=500
BENCH:  Initializing the setup of the kernel(s)
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /usr/local/lib/plumed
PLUMED: LibraryPath: ../../src/lib/install/libplumedKernel.so
PLUMED: For installed feature, see /usr/local/lib/plumed/src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: Coord.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: Coord.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
PLUMED: PLUMED is starting
PLUMED: Version: 2.10.0-dev (git: 639e81047-dirty) compiled on Jul 12 2024 at 11:29:54
PLUMED: Please cite these papers when using PLUMED [1][2]
PLUMED: For further information see the PLUMED web page at http://www.plumed.org
PLUMED: Root: /scratch/drapetti/repos/plumed2-dev/
PLUMED: LibraryPath: /u/d/drapetti/scratch/repos/plumed2-dev/src/lib/libplumedKernel.so
PLUMED: For installed feature, see /scratch/drapetti/repos/plumed2-dev//src/config/config.txt
PLUMED: Molecular dynamics engine: benchmarks
PLUMED: Precision of reals: 8
PLUMED: Running over 1 node
PLUMED: Number of threads: 1
PLUMED: Cache line size: 512
PLUMED: Number of atoms: 500
PLUMED: File suffix: 
PLUMED: FILE: Coord.dat
PLUMED: Action COORDINATION
PLUMED:   with label cpu
PLUMED:   between two groups of 500 and 0 atoms
PLUMED:   first group:
PLUMED:   1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  
PLUMED:   25  26  27  28  29  30  31  32  33  34  35  36  37  38  39  40  41  42  43  44  45  46  47  48  49  
PLUMED:   50  51  52  53  54  55  56  57  58  59  60  61  62  63  64  65  66  67  68  69  70  71  72  73  74  
PLUMED:   75  76  77  78  79  80  81  82  83  84  85  86  87  88  89  90  91  92  93  94  95  96  97  98  99  
PLUMED:   100  101  102  103  104  105  106  107  108  109  110  111  112  113  114  115  116  117  118  119  120  121  122  123  124  
PLUMED:   125  126  127  128  129  130  131  132  133  134  135  136  137  138  139  140  141  142  143  144  145  146  147  148  149  
PLUMED:   150  151  152  153  154  155  156  157  158  159  160  161  162  163  164  165  166  167  168  169  170  171  172  173  174  
PLUMED:   175  176  177  178  179  180  181  182  183  184  185  186  187  188  189  190  191  192  193  194  195  196  197  198  199  
PLUMED:   200  201  202  203  204  205  206  207  208  209  210  211  212  213  214  215  216  217  218  219  220  221  222  223  224  
PLUMED:   225  226  227  228  229  230  231  232  233  234  235  236  237  238  239  240  241  242  243  244  245  246  247  248  249  
PLUMED:   250  251  252  253  254  255  256  257  258  259  260  261  262  263  264  265  266  267  268  269  270  271  272  273  274  
PLUMED:   275  276  277  278  279  280  281  282  283  284  285  286  287  288  289  290  291  292  293  294  295  296  297  298  299  
PLUMED:   300  301  302  303  304  305  306  307  308  309  310  311  312  313  314  315  316  317  318  319  320  321  322  323  324  
PLUMED:   325  326  327  328  329  330  331  332  333  334  335  336  337  338  339  340  341  342  343  344  345  346  347  348  349  
PLUMED:   350  351  352  353  354  355  356  357  358  359  360  361  362  363  364  365  366  367  368  369  370  371  372  373  374  
PLUMED:   375  376  377  378  379  380  381  382  383  384  385  386  387  388  389  390  391  392  393  394  395  396  397  398  399  
PLUMED:   400  401  402  403  404  405  406  407  408  409  410  411  412  413  414  415  416  417  418  419  420  421  422  423  424  
PLUMED:   425  426  427  428  429  430  431  432  433  434  435  436  437  438  439  440  441  442  443  444  445  446  447  448  449  
PLUMED:   450  451  452  453  454  455  456  457  458  459  460  461  462  463  464  465  466  467  468  469  470  471  472  473  474  
PLUMED:   475  476  477  478  479  480  481  482  483  484  485  486  487  488  489  490  491  492  493  494  495  496  497  498  499  
PLUMED:   500  
PLUMED:   second group:
PLUMED:   
PLUMED:   without periodic boundary conditions
PLUMED:   contacts are counted with cutoff 1.  Using rational switching function with parameters d0=0 nn=6 mm=12
PLUMED: Action PRINT
PLUMED:   with label @1
PLUMED:   with stride 1
PLUMED:   with arguments : 
PLUMED:    scalar with label cpu 
PLUMED:   on file Colvar
PLUMED:   with format  %8.4f
PLUMED: Action FLUSH
PLUMED:   with label @2
PLUMED:   with stride 1
PLUMED: END FILE: Coord.dat
PLUMED: Timestep: 1.000000
PLUMED: KbT has not been set by the MD engine
PLUMED: It should be set by hand where needed
PLUMED: Relevant bibliography:
PLUMED:   [1] The PLUMED consortium, Nat. Methods 16, 670 (2019)
PLUMED:   [2] Tribello, Bonomi, Branduardi, Camilloni, and Bussi, Comput. Phys. Commun. 185, 604 (2014)
PLUMED: Please read and cite where appropriate!
PLUMED: Finished setup
BENCH:  Starting MD loop
BENCH:  Use CTRL+C to stop at any time and collect timers (not working in MPI runs)
BENCH:  Warm-up completed
BENCH:  60% completed
BENCH:  Running comparative analysis, 1600 blocks with size 1
BENCH:  
BENCH:  Kernel:      this
BENCH:  Input:       Coord.dat
BENCH:  Comparative: 1.000 +- 0.000
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001329     0.001329     0.001329     0.001329
BENCH:  B0 First step                                      1     0.001004     0.001004     0.001004     0.001004
BENCH:  B1 Warm-up                                       399     0.412732     0.001034     0.000967     0.001826
BENCH:  B2 Calculation part 1                            800     0.817150     0.001021     0.000976     0.001606
BENCH:  B3 Calculation part 2                            800     0.838765     0.001048     0.000977     0.001706
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     2.069485     2.069485     2.069485     2.069485
PLUMED: 1 Prepare dependencies                          2000     0.001352     0.000001     0.000000     0.000016
PLUMED: 2 Sharing data                                  2000     0.004684     0.000002     0.000001     0.000032
PLUMED: 3 Waiting for data                              2000     0.001436     0.000001     0.000000     0.000009
PLUMED: 4 Calculating (forward loop)                    2000     2.034346     0.001017     0.000952     0.001778
PLUMED: 5 Applying (backward loop)                      2000     0.001992     0.000001     0.000001     0.000012
PLUMED: 6 Update                                        2000     0.016534     0.000008     0.000005     0.000161
BENCH:  
BENCH:  Kernel:      ../../src/lib/install/libplumedKernel.so
BENCH:  Input:       Coord.dat
BENCH:  Comparative: 1.021 +- 0.003
BENCH:                                                Cycles        Total      Average      Minimum      Maximum
BENCH:  A Initialization                                   1     0.001409     0.001409     0.001409     0.001409
BENCH:  B0 First step                                      1     0.001141     0.001141     0.001141     0.001141
BENCH:  B1 Warm-up                                       399     0.420014     0.001053     0.000993     0.001765
BENCH:  B2 Calculation part 1                            800     0.836896     0.001046     0.000999     0.001651
BENCH:  B3 Calculation part 2                            800     0.852747     0.001066     0.001000     0.001831
PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     2.109832     2.109832     2.109832     2.109832
PLUMED: 1 Prepare dependencies                          2000     0.001274     0.000001     0.000000     0.000011
PLUMED: 2 Sharing data                                  2000     0.004684     0.000002     0.000001     0.000042
PLUMED: 3 Waiting for data                              2000     0.001590     0.000001     0.000000     0.000011
PLUMED: 4 Calculating (forward loop)                    2000     2.074114     0.001037     0.000980     0.001722
PLUMED: 5 Applying (backward loop)                      2000     0.001959     0.000001     0.000001     0.000016
PLUMED: 6 Update                                        2000     0.016623     0.000008     0.000004     0.000127
""",
    "parsed": output_2k1f["parsed"],
    "colums": output_2k1f["colums"],
}


@pytest.fixture
def full_benchmark_output_noheader():
    return output_noheader["file"], output_noheader["parsed"]


@pytest.fixture
def extracted_rows_output_noheader():
    return output_noheader["parsed"], output_noheader["colums"]


@pytest.fixture
def full_benchmark_output_1k2f():
    return output_1k2f["file"], output_1k2f["parsed"]


@pytest.fixture
def extracted_rows_output_1k2f():
    return output_1k2f["parsed"], output_1k2f["colums"]


@pytest.fixture
def full_benchmark_output_2k1f():
    return output_2k1f["file"], output_2k1f["parsed"]


@pytest.fixture
def extracted_rows_output_2k1f():
    return output_2k1f["parsed"], output_2k1f["colums"]


@pytest.fixture
def full_benchmark_output_2k1f_override():
    return output_2k1f_override["file"], output_2k1f_override["parsed"]


@pytest.fixture
def extracted_rows_output_2k1f_override():
    return output_2k1f_override["parsed"], output_2k1f_override["colums"]


@pytest.fixture
def readme_example_benchmark_output():
    return (
        r"""BENCH:  Kernel:      this
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
    """,
        {
            "this+plumed.dat": KernelBenchmark(
                kernel="this",
                input="plumed.dat",
                compare={"fraction": 1.0, "error": 0.0},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.214297,
                            "Average": 0.214297,
                            "Minimum": 0.214297,
                            "Maximum": 0.214297,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.062736,
                            "Average": 0.062736,
                            "Minimum": 0.062736,
                            "Maximum": 0.062736,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 199,
                            "Total": 12.618833,
                            "Average": 0.063411,
                            "Minimum": 0.055884,
                            "Maximum": 0.07686,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 400,
                            "Total": 25.567659,
                            "Average": 0.063919,
                            "Minimum": 0.05411,
                            "Maximum": 0.113234,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 400,
                            "Total": 25.594014,
                            "Average": 0.063985,
                            "Minimum": 0.059516,
                            "Maximum": 0.102646,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 64.054325,
                            "Average": 64.054325,
                            "Minimum": 64.054325,
                            "Maximum": 64.054325,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.003443,
                            "Average": 3e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.3e-05,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.305915,
                            "Average": 0.000306,
                            "Minimum": 1.5e-05,
                            "Maximum": 0.037867,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.003051,
                            "Average": 3e-06,
                            "Minimum": 2e-06,
                            "Maximum": 1.3e-05,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 63.459357,
                            "Average": 0.063459,
                            "Minimum": 0.054012,
                            "Maximum": 0.091577,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.00852,
                            "Average": 9e-06,
                            "Minimum": 5e-06,
                            "Maximum": 4.4e-05,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.043188,
                            "Average": 4.3e-05,
                            "Minimum": 3.1e-05,
                            "Maximum": 8e-05,
                        }
                    ),
                },
            ),
            "../../src/lib/install/libplumedKernel.so+plumed.dat": KernelBenchmark(
                kernel="../../src/lib/install/libplumedKernel.so",
                input="plumed.dat",
                compare={"fraction": 0.941, "error": 0.002},
                rows={
                    "A Initialization": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.21619,
                            "Average": 0.21619,
                            "Minimum": 0.21619,
                            "Maximum": 0.21619,
                        }
                    ),
                    "B0 First step": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 0.058967,
                            "Average": 0.058967,
                            "Minimum": 0.058967,
                            "Maximum": 0.058967,
                        }
                    ),
                    "B1 Warm-up": BenchmarkRow.from_dict(
                        {
                            "Cycles": 199,
                            "Total": 11.983512,
                            "Average": 0.060219,
                            "Minimum": 0.056412,
                            "Maximum": 0.102643,
                        }
                    ),
                    "B2 Calculation part 1": BenchmarkRow.from_dict(
                        {
                            "Cycles": 400,
                            "Total": 24.03551,
                            "Average": 0.060089,
                            "Minimum": 0.056539,
                            "Maximum": 0.1139,
                        }
                    ),
                    "B3 Calculation part 2": BenchmarkRow.from_dict(
                        {
                            "Cycles": 400,
                            "Total": 24.084369,
                            "Average": 0.060211,
                            "Minimum": 0.056866,
                            "Maximum": 0.097184,
                        }
                    ),
                    "Plumed": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1,
                            "Total": 60.373083,
                            "Average": 60.373083,
                            "Minimum": 60.373083,
                            "Maximum": 60.373083,
                        }
                    ),
                    "1 Prepare dependencies": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.003351,
                            "Average": 3e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.4e-05,
                        }
                    ),
                    "2 Sharing data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.329323,
                            "Average": 0.000329,
                            "Minimum": 1.5e-05,
                            "Maximum": 0.032672,
                        }
                    ),
                    "3 Waiting for data": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.003078,
                            "Average": 3e-06,
                            "Minimum": 1e-06,
                            "Maximum": 1.3e-05,
                        }
                    ),
                    "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 59.752459,
                            "Average": 0.059752,
                            "Minimum": 0.05631,
                            "Maximum": 0.083841,
                        }
                    ),
                    "5 Applying (backward loop)": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.0089,
                            "Average": 9e-06,
                            "Minimum": 6e-06,
                            "Maximum": 3.4e-05,
                        }
                    ),
                    "6 Update": BenchmarkRow.from_dict(
                        {
                            "Cycles": 1000,
                            "Total": 0.043015,
                            "Average": 4.3e-05,
                            "Minimum": 3.2e-05,
                            "Maximum": 0.000239,
                        }
                    ),
                },
            ),
        },
    )


@pytest.fixture
def plumed_time_report():
    return (
        r"""PLUMED:                                               Cycles        Total      Average      Minimum      Maximum
PLUMED:                                                    1     7.959897     7.959897     7.959897     7.959897
PLUMED: 1 Prepare dependencies                          5000     0.002370     0.000000     0.000000     0.000009
PLUMED: 2 Sharing data                                  5000     0.010464     0.000002     0.000001     0.000024
PLUMED: 3 Waiting for data                              5000     0.003127     0.000001     0.000000     0.000008
PLUMED: 4 Calculating (forward loop)                    5000     7.868715     0.001574     0.001479     0.002362
PLUMED: 4A  1 posx                                      5000     0.000612     0.000000     0.000000     0.000004
PLUMED: 4A  2 posy                                      5000     0.000279     0.000000     0.000000     0.000006
PLUMED: 4A  3 posz                                      5000     0.000265     0.000000     0.000000     0.000004
PLUMED: 4A  4 Masses                                    5000     0.000288     0.000000     0.000000     0.000005
PLUMED: 4A  5 Charges                                   5000     0.000294     0.000000     0.000000     0.000007
PLUMED: 4A  6 Box                                       5000     0.000342     0.000000     0.000000     0.000008
PLUMED: 4A  7 benchmarks                                5000     0.000406     0.000000     0.000000     0.000001
PLUMED: 4A  8 @0                                        5000     0.000226     0.000000     0.000000     0.000001
PLUMED: 4A  9 cpu                                       5000     7.849295     0.001570     0.001476     0.002354
PLUMED: 4A 10 @2                                        5000     0.000440     0.000000     0.000000     0.000004
PLUMED: 4A 11 @3                                        5000     0.000314     0.000000     0.000000     0.000007
PLUMED: 5 Applying (backward loop)                      5000     0.017107     0.000003     0.000003     0.000053
PLUMED: 5A  0 @3                                        5000     0.000255     0.000000     0.000000     0.000006
PLUMED: 5A  1 @2                                        5000     0.000123     0.000000     0.000000     0.000003
PLUMED: 5A  2 cpu                                       5000     0.000516     0.000000     0.000000     0.000006
PLUMED: 5A  3 @0                                        5000     0.000331     0.000000     0.000000     0.000006
PLUMED: 5A  4 benchmarks                                5000     0.002406     0.000000     0.000000     0.000007
PLUMED: 5A  5 Box                                       5000     0.000468     0.000000     0.000000     0.000006
PLUMED: 5A  6 Charges                                   5000     0.000212     0.000000     0.000000     0.000001
PLUMED: 5A  7 Masses                                    5000     0.000161     0.000000     0.000000     0.000006
PLUMED: 5A  8 posz                                      5000     0.000119     0.000000     0.000000     0.000005
PLUMED: 5A  9 posy                                      5000     0.000127     0.000000     0.000000     0.000000
PLUMED: 5A 10 posx                                      5000     0.000130     0.000000     0.000000     0.000000
PLUMED: 5B Update forces                                5000     0.000119     0.000000     0.000000     0.000002
PLUMED: 6 Update                                        5000     0.041863     0.000008     0.000005     0.000098
    """,
        KernelBenchmark(
            kernel="",
            input="",
            rows={
                "Plumed": BenchmarkRow.from_dict(
                    {
                        "Cycles": 1,
                        "Total": 7.959897,
                        "Average": 7.959897,
                        "Minimum": 7.959897,
                        "Maximum": 7.959897,
                    }
                ),
                "1 Prepare dependencies": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.00237,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 9e-06,
                    }
                ),
                "2 Sharing data": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.010464,
                        "Average": 2e-06,
                        "Minimum": 1e-06,
                        "Maximum": 2.4e-05,
                    }
                ),
                "3 Waiting for data": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.003127,
                        "Average": 1e-06,
                        "Minimum": 0.0,
                        "Maximum": 8e-06,
                    }
                ),
                "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 7.868715,
                        "Average": 0.001574,
                        "Minimum": 0.001479,
                        "Maximum": 0.002362,
                    }
                ),
                "4A  1 posx": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000612,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 4e-06,
                    }
                ),
                "4A  2 posy": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000279,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "4A  3 posz": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000265,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 4e-06,
                    }
                ),
                "4A  4 Masses": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000288,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 5e-06,
                    }
                ),
                "4A  5 Charges": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000294,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 7e-06,
                    }
                ),
                "4A  6 Box": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000342,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 8e-06,
                    }
                ),
                "4A  7 benchmarks": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000406,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 1e-06,
                    }
                ),
                "4A  8 @0": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000226,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 1e-06,
                    }
                ),
                "4A  9 cpu": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 7.849295,
                        "Average": 0.00157,
                        "Minimum": 0.001476,
                        "Maximum": 0.002354,
                    }
                ),
                "4A 10 @2": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.00044,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 4e-06,
                    }
                ),
                "4A 11 @3": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000314,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 7e-06,
                    }
                ),
                "5 Applying (backward loop)": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.017107,
                        "Average": 3e-06,
                        "Minimum": 3e-06,
                        "Maximum": 5.3e-05,
                    }
                ),
                "5A  0 @3": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000255,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "5A  1 @2": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000123,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 3e-06,
                    }
                ),
                "5A  2 cpu": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000516,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "5A  3 @0": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000331,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "5A  4 benchmarks": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.002406,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 7e-06,
                    }
                ),
                "5A  5 Box": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000468,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "5A  6 Charges": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000212,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 1e-06,
                    }
                ),
                "5A  7 Masses": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000161,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 6e-06,
                    }
                ),
                "5A  8 posz": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000119,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 5e-06,
                    }
                ),
                "5A  9 posy": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000127,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 0.0,
                    }
                ),
                "5A 10 posx": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.00013,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 0.0,
                    }
                ),
                "5B Update forces": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.000119,
                        "Average": 0.0,
                        "Minimum": 0.0,
                        "Maximum": 2e-06,
                    }
                ),
                "6 Update": BenchmarkRow.from_dict(
                    {
                        "Cycles": 5000,
                        "Total": 0.041863,
                        "Average": 8e-06,
                        "Minimum": 5e-06,
                        "Maximum": 9.8e-05,
                    }
                ),
            },
        ),
    )


@pytest.fixture
def incremental_output():
    """
    incremental_output acts as list of preparsed files
    it only has the BENCHSETTINGS and the total Plumed time  and the calcupate time for two kernels with the same file
    """
    # this only mock a "Plumed" output, used for testing the creation of a series of benchmarks with different number of atoms
    toret = {}
    import string

    nfiles = 6
    for i, name in enumerate(list(string.ascii_lowercase)[:nfiles], 1):
        toret[name + ".out"] = BenchmarkRun(
            BenchmarkSettings(
                kernels=["this"],
                inputs=[f"Coord{i}.dat"],
                steps=2000,
                atoms=i * 500,
                maxtime=-1.0,
                sleep=0.0,
                atom_distribution="line",
            ),
            {
                f"this+Coord{i}.dat": KernelBenchmark(
                    kernel="this",
                    input=f"Coord{i}.dat",
                    compare={"fraction": 1.0, "error": 0.0},
                    rows={
                        "Plumed": BenchmarkRow.from_dict(
                            {
                                "Cycles": 1,
                                "Total": i * 2.0,
                                "Average": i * 2.0,
                                "Minimum": i * 2.0,
                                "Maximum": i * 2.0,
                            }
                        ),
                        "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                            {
                                "Cycles": 100,
                                "Total": i * 1.5,
                                "Average": i * 1.5 / 100,
                                "Minimum": i * 1.5 / 100,
                                "Maximum": i * 1.5 / 100,
                            }
                        ),
                    },
                ),
                f"that+Coord{i}.dat": KernelBenchmark(
                    kernel="that",
                    input=f"Coord{i}.dat",
                    compare={"fraction": 2.0, "error": 0.0},
                    rows={
                        "Plumed": BenchmarkRow.from_dict(
                            {
                                "Cycles": 1,
                                "Total": i * 4.0,
                                "Average": i * 4.0,
                                "Minimum": i * 4.0,
                                "Maximum": i * 4.0,
                            }
                        ),
                        "4 Calculating (forward loop)": BenchmarkRow.from_dict(
                            {
                                "Cycles": 100,
                                "Total": i * 3.5,
                                "Average": i * 3.5 / 100,
                                "Minimum": i * 3.5 / 100,
                                "Maximum": i * 3.5 / 100,
                            }
                        ),
                    },
                ),
            },
        )
    # parsed input, kernels, filelist
    return toret, ["this", "that"], [f"Coord{i}.dat" for i in range(1, 1 + nfiles)]
