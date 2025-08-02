# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

"""This module contains the constants used in the benchmarks.

TIMINGCOLS are the columns in the timing report at the end of each plumed run

The other variables are the common row names in the benchmark output (the `BM_` ones) or
the common rows in the time report.

If the user uses `DEBUG DETAILED_TIMERS` the extra names are not liste here, but they are still processed by plumed_benc_pp and can be accessed by hand.
"""

#: List of the column names in the benchmark output
TIMINGCOLS = ["Cycles", "Total", "Average", "Minimum", "Maximum"]
# These are the common row names in the benchmark output
#: time for initialization in the benchmarks
BM_INIT = "A Initialization"
#: time for the first step in the benchmarks
BM_FIRSTSTEP = "B0 First step"
#: time for the warmup in the benchmarks
BM_WARMUP = "B1 Warm-up"
#: time for the calculation part 1 in the benchmarks
BM_CALCULATION_PART1 = "B2 Calculation part 1"
#: time for the calculation part 2 in the benchmarks
BM_CALCULATION_PART2 = "B3 Calculation part 2"
#: total time registere dby the plumed internal (is a empty row in the report)
TOTALTIME = "Plumed"
#: time passed in PlumedMain::prepareDependencies()
PREPARE = "1 Prepare dependencies"
#: time passed in PlumedMain::shareData()
SHARE = "2 Sharing data"
#: time passed in PlumedMain::waitData()
WAIT = "3 Waiting for data"
#: time passed in PlumedMain::justCalculate()
CALCULATE = "4 Calculating (forward loop)"
#: time passed in PlumedMain::backwardPropagate()
APPLY = "5 Applying (backward loop)"
#: time passed in PlumedMain::update()
UPDATE = "6 Update"
