# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['amethyst_facet',
 'amethyst_facet.cli',
 'amethyst_facet.cli.commands',
 'amethyst_facet.cli.decorators',
 'amethyst_facet.cli.parse',
 'amethyst_facet.h5',
 'amethyst_facet.logging',
 'amethyst_facet.windows']

package_data = \
{'': ['*']}

install_requires = \
['click',
 'duckdb',
 'h5py',
 'hypothesis',
 'numpy<=1.26.4',
 'pandas',
 'parse',
 'polars-u64-idx',
 'pyarrow',
 'pytest']

entry_points = \
{'console_scripts': ['facet = amethyst_facet.cli.commands.facet:facet']}

setup_kwargs = {
    'name': 'amethyst-facet',
    'version': '1.1.9',
    'description': 'Compute window aggregations and alter contents of Amethyst HDF5 files',
    'long_description': '**Facet** is an efficient utility for computing window aggregations on Amethyst HDF5 files produced via the [premethyst](https://github.com/adeylab/premethyst) pipeline.\n\n\n### Create environment\n\nInstall `facet.py` dependencies using mamba:\n```\nmamba create -n facet pip && pip install amethyst-facet\n```\n\n### Ingest base-pair-resolution .parquet and .cov files\n\n`facet calls2h5` will ingest base-pair-resolution methylation observations in the Scale Bio .parquet format as well as the legacy plaintext .cov format to the HDF5 format used by Amethyst. This can then be used to compute window aggregations using `facet agg`. Context and barcode can be flexibly parsed from the filename.\n\nExample:\n\n```\nfacet calls2h5 --parse {barcode1}_{barcode2}_{barcode3}.{context}.cov output.h5 *.cov\n```\n\nThis will store any `*.cov` file with a name in the format to form datasets named `/{context}/{barcode1}{barcode2}{barcode3}/1`.\n\nTo specify how datasets are parsed, you can use the `--format` option to supply Python code that will format a list of strings `barcode` and a list of strings `context` into the group under which the dataset should be stored. Example:\n\n```\nfacet calls2h5 --parse {barcode1}_{barcode2}.{context}.cov --format "\'/{context[0]}/{barcode[0]}_{barcode[1]}\'" output.h5 *.cov\n```\n\nSince the Scale Bio parquet format has a context column, there is no need to parse the context from the filename for these files.\n\n```\nfacet calls2h5 --parse {barcode1}_{barcode2}.parquet output.h5 *.parquet\n```\n\nOther options for configuring input parsing and the output datset can be found using `facet calls2h5 --help`.\n\nThe expected schema for .cov files is headerless, tab-delimited files with the following columns:\n\n`chr  pos pct t c`\n\nOnly the `chr`, `pos`, `t`, and `c` columns will be written to the HDF5 file.\n\n\n### Compute Window Aggregations\n\n`facet agg` will add window aggregations to an existing HDF5 file in version 2.0.0 (see below for information on file format conversion). \n\nExample:\n```\nfacet agg -u 500 -u step_1000=1000:250 -w special_fancy_windows=windows.tsv -p 55 *.h5\n```\n\nThis computes several types of windows.\n\n+ `-u 500` computes uniform non-overlapping 500bp windows. These will be stored in `/[context]/[barcode]/[window_size]` by default. A custom name can be chosen by prepending `-u [dataset_name]=500`.\n+ `-u step_1000=1000:250` computes 1000bp windows with a 250bp step, so intervals will be computed at $[0, 1000), [250, 1250), ...$.  This example uses a custom name of `step_1000`. The default is to use `[window_size]_by_[step_size]`, which in this case would have been `1000_by_250`.\n+ `-w special_fancy_windows=windows.tsv` computes aggregations over custom windows defined in a CSV-like file. The headers `chr`, `start` and `end` are required but the file format is sniffed by DuckDB (csv, tsv etc are allowed). Intervals are left-closed right-open, i.e. $[start, end)$ and may be overlapping and gapped.\n\nThe `-p 55` option parallelizes the computation using 55 worker cores. All HDF5 files retrieved via `*.h5` will have windows computed in this case. Multiple globs can be specified, i.e. `-glob path1/*.h5 -glob path2/*.h5`.\n\nOther options are described in `facet agg --help`.\n\n### Help\n\nThe options for facet.py can be explored at the command line by appending `--help`.\n\nExample:\n```\n$ facet --help\nUsage: facet.py [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  agg      Compute window sums over methylation observations stored in...\n  convert  Convert an old Amethyst HDF5 file format to v2.0.0 format\n  delete   Delete contexts, barcodes, or datasets from an Amethyst 2.0.0...\n  version\n```\n\nYou can also call `--help` on subcommands. Example:\n\n```facet agg --help```\n\n### Convert old Amethyst HDF5 file format to version 2.0.0\n\nFile format conversion is necessary prior to computing window aggregations using `facet.py` for Amethyst HDF5 files produced using earlier scripts.\n\nExample:\n```\nfacet convert old_format.h5 new_format.h5\n```\n\n#### Explanation and schema comparison:\n\nThe old Amethyst HDF5 format stored datasets under a cell barcode under a context group:\n\n```\n/[context]/[barcode]\n```\n\n`context` values are typically CH and CG. The `barcode` values are unique identifiers attributed to single cells. Typically each value of `barcode` is found in both the CH and CG contexts.\n\nThe schema of `barcode` was `chr`, `pos`, `pct`, `c`, `t`, with `chr` the chromosome name, `pos` the bp position of the observation, `pct` equal to `c/(c+t)`, and `c` and `t` the methylated and unmethylated count at that position. \n\nThis gave no clear way to store window aggregations alongside the bp-resolution observations. We therefore altered the schema to:\n\n```\n/[context]/[barcode]/[dataset]\n```\n\nThe bp-resolution observations are stored under the dataset `1` by default. Window aggregations are stored under their context and barcode under other names. The schema for window aggregations is `chr`, `start`, `end`, `c`, `t`, `c_nz`, `t_nz`. The `start` and `end` values denote the interval $[start, end)$. The `c` and `t` values store the sum of `c` and `t` counts for observed positions on that interval. Intervals with no observations are not reported. The `c_nz` and `t_nz` fields store the count of positions where `c >= 1` or `t >= 1` respectively.\n\n### Delete datasets\n\nExamples:\n\n```\nfacet delete context CH *.h5\nfacet delete barcode AGCGAGCGAGCAHHCAHH *.h5\nfacet delete dataset 1 *.h5\n```\n',
    'author': 'Ben Skubi',
    'author_email': 'skubi@ohsu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.12,<4.0',
}


setup(**setup_kwargs)
