# PostOMC

A Python package for reading and analyzing OpenMC `depletion_results.h5` files.

# Installation

PostOMC is available on PyPI:

```sh
pip install postomc
```

This installs the `postomc` python package as well as the `pomc` command line script.

# API Usage

PostOMC revolves around the `DepletionResults` class which can be instantiated from a `depletion_results.h5` file:

```python
from postomc import DepletionResults
res = DepletionResults("path/to/depletion_results.h5")
```

To get the isotopic composition over time simply call the `DepletionResults` like a function, and provide the desired unit as argument:

```python
res("g/cm**3")
```

If your result file contains only a single medium, this returns a Pandas dataframe with nuclide names as row index and timestamps as columns:

```text
          0.0           1.0           2.0           3.0
H1        0.0  8.546804e-11  1.710615e-10  2.561159e-10
H2        0.0  9.163202e-17  3.674525e-16  8.276545e-16
H3        0.0  7.819664e-26  6.288458e-25  2.128727e-24
H4        0.0  0.000000e+00  0.000000e+00  0.000000e+00
H5        0.0  0.000000e+00  0.000000e+00  0.000000e+00
...       ...           ...           ...           ...
Ds271_m1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds272     0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds273     0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds279_m1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Rg272     0.0  0.000000e+00  0.000000e+00  0.000000e+00

[3820 rows x 4 columns]
```

If your result file contains multiple media, it will return a dictionary mapping medium id to results dataframes.
If you want to look at derived quantities like decay heat or activity, you'll need to provide an OpenMC decay chain to get decay constant and energy release values:

```python
from postomc import DepletionResults
res = DepletionResults("path/to/depletion_results.h5", chain="path/to/chain.xml")
res("W")
res("W/cm**3")
res("Bq")
res("Bq/cm**3")
```

You can also set the time unit to whatever you prefer:

```python
res("W", time_unit="s")
```

PostOMC uses [pint](https://pint.readthedocs.io/en/latest/index.html) for unit management so any unit from the default `pint` definition file is valid as long as it is homogeneous to mass, number of atoms, power, activity, or their volumic counterparts.

We also define the `atom` unit as an alias for the `count` unit so you can do:

```python
res("atom/beer_barrel", time_unit="fortnight")
```

Sometimes you may want to get information like total mass of a certain element, regardless of isotope.
You can facilitate this treatment by providing the `multiindex=True` argument to the call, this will result in dataframes using [multiindex](https://pandas.pydata.org/docs/user_guide/advanced.html).

```text
          0.0           1.0           2.0           3.0
Z  A   I
H  1   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   2   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   3   0  0.0  4.284350e-12  3.445411e-11  1.166318e-10
   4   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   5   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
...       ...           ...           ...           ...
Ds 271 1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   272 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   273 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   279 1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Rg 272 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00

[3820 rows x 4 columns]
```

In addition to isotopic composition you can retrieve:

* Reaction rates in $\mathrm{reaction}/s$ with `DepletionResults.rr(time_unit="s")`
* $k_\mathrm{eff}$ using `DepletionResults.keffs(time_unit="s")`
* Reactivity using `DepletionResults.rhos(time_unit="s")`

Time units are always "day" by default.

# CLI Usage

PostOMC provides some CLI commands to perform common analysis tasks without having to create a python script.

## Printing Information

You can print a short summary of a `depletion_results.h5` file using the `pomc info` command:

```console
$ pomc info data/depletion_results.h5
Depletion File       data/depletion_results.h5
Summary File         data/summary.h5

                  Depletion Steps                   
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Step # ┃ t(i) [days] ┃ t(i+1) [days] ┃ Power [W] ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1      │ 0.00        │ 30.00         │ 174.00    │
│ 2      │ 30.00       │ 60.00         │ 174.00    │
│ 3      │ 60.00       │ 90.00         │ 174.00    │
│ 4      │ 90.00       │ 120.00        │ 174.00    │
│ 5      │ 120.00      │ 120.00        │ 174.00    │
└────────┴─────────────┴───────────────┴───────────┘
                        Materials                        
┏━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Id ┃ Name       ┃ Nuclides ┃ Atom Density [atom/b/cm] ┃
┡━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ UO2 (2.4%) │ 4        │ 6.88e-02                 │
└────┴────────────┴──────────┴──────────────────────────┘
```

## Exporting data

PostOMC provides the `pomc export` command to export the depletion result data to Excel, CSV, or to print its content to the terminal:

```text
Usage: pomc export [OPTIONS] FILE

  Converts depletion_result.h5 files to various output formats.

Options:
  -s, --split-nuclides    Whether to create a nuclide indexed table or an
                          (Element, A, I) indexed table.
  -u, --unit TEXT         The desired unit.  [default: g/cm**3]
  -t, --time-unit TEXT    The desired time unit.  [default: d]
  -o, --output TEXT       Path to the output file.
  -c, --chain TEXT        Path to a depletion chain file.
  -m, --material INTEGER  Id of the desired material
  --help                  Show this message and exit.
```
### Examples

To create an Excel file with a tab for each material:

```console
$ pomc export path/to/depletion_results.h5 -o mass.xlsx -u "g/cm**3"
```

To create a CSV file of decay heat for a single material:

```console
$ pomc export data/depletion_results.h5 -o dh.csv -u "W" -m 1
```
 
By default PostOMC finds the required depletion chain using the `OPENMC_CHAIN_FILE` environment variable, to specify a depletion chain manually you can provide the `export` command with the `-c /path/to/chain/file` option.

### Plotting data

PostOMC provides the `pomc plot` command to quickly plot data from the `depletion_results.h5` file:

```text
Usage: pomc plot [OPTIONS] FILE

Options:
  -n, --nuclides TEXT
  -u, --unit TEXT         The desired unit.  [default: g/cm**3]
  -t, --time-unit TEXT    The desired time unit.  [default: d]
  -m, --material INTEGER  Id of the desired material
  -o, --output TEXT       Path to the output file.  [default: depletion.png]
  -c, --chain TEXT        Path to a depletion chain file.
  --help                  Show this message and exit.
```
### Examples

To plot the mass density of U235 and Pu239 from the `depletion_results.h5` file in SVG format:

```console
$ uv run pomc plot data/depletion_results.h5 -n "U235 Pu239" -o depletion.svg -u "g/cm**3"
```