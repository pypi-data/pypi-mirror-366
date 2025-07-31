# truewinds

True winds is still in beta and requires updated documentation, examples, and tests. Function output may change in future releases.

True winds provides vectorized versions of the true winds code provided by [SAMOS](https://samos.coaps.fsu.edu/html/tools_truewinds.php). 
It is important to note that there may be some floating point differences between this numpy-based code and the orignal legacy functions.
These differences occur at digits that are considered insignificant for wind speed and direction (< 1e-10). 

## Installation

`pip install truewinds`


## Documentation

Code documentation for truewinds is available here: https://iantblack.github.io/truewinds/

The code truewinds is based on can be found here: [SAMOS True Winds Tools](https://samos.coaps.fsu.edu/html/tools_truewinds.php)

The original manuscript for true winds computation can be found here: [True Winds Manuscript](`https://doi.org/10.1175/1520-0426(1999)016<0939:EMTITW>2.0.CO;2`)