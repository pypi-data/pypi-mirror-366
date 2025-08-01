# Irreversibility Tests Library

The assessment of time irreversibility is the assessment of the lack of invariance of the statistical properties of a system under the operation of time reversal. As a simple example, suppose a movie of an ice cube melting in a glass, and one with the ice cube forming from liquid water: an observer can easily decide which one is the original and which the time-reversed one; in this case, the creation (or destruction) of entropy is what makes the process irreversible. On the other hand, the movement of a pendulum and its time-reversed version are undistinguishable, and hence the dynamics is reversible.

Irreversible dynamics have been found in many real-world systems, with alterations being connected to, for instance, pathologies in the human brain, heart and gait, or to inefficiencies in financial markets. Assessing irreversibility in time series is not an easy task, due to its many aetiologies and to the different ways it manifests in data.

This is a library that will (hopefully) make your life easier when it comes to the analysis of the irreveribility of real-world time series. It comprises a large number of tests (not all existing ones, but we are quite close to that); and utilities to simply the whole process.

If you are interested in the concept of irreversibility, you may start from our papers:

M. Zanin, D. Papo
Tests for assessing irreversibility in time series: review and comparison.
Entropy 2021, 23(11), 1474. https://www.mdpi.com/1099-4300/23/11/1474

Zanin, M., & Papo, D. (2025).
Algorithmic Approaches for Assessing Multiscale Irreversibility in Time Series: Review and Comparison.
Entropy, 27(2), 126. https://www.mdpi.com/1099-4300/27/2/126




## Setup

This package can be installed from PyPI using pip:

```bash
pip install irreversibility
```

This will automatically install all the necessary dependencies as specified in the
`pyproject.toml` file.



## Getting started

Check the files Example_*.py for examples on how to use each test, and also [here](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home#examples).

Information about all methods, parameters, and other relevant issues can be found both in the previous papers, and in the wiki: [Go to the wiki](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home). You can also check our take on the question: [why there are so many tests?](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Why-so-many-tests%3F)

Note that all implementations have been developed in-house, and as such may contain errors or inefficient code; we welcome readers to send us comments, suggestions and corrections, using the "Issues" feature.



## Change log

See the [Version History](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Version-History) section of the Wiki for details.


