# Nema Python Extension

This library provides a set of classes and functions to work with Nema artifacts.

It provides both the `nema` library, as well as the `nema-python` CLI.

## Installation

To install the Nema Python extension, run the following command (you'll likely want to do this in a virtual environment):

```bash
pip install nema
```

This installs both the `nema` python package and the `nema-python` CLI tool.

Nema works for Python 3.8 and above.

## Usage

To login into Nema, run `nema-python login` from the command line. This will prompt you to enter your Nema credentials.

Then run `nema-python init` which will prompt you for your Nema project URL and create a `nema.toml` file in your current directory.

### Workflows

`nema-python workflow init` will then create a workflow in Nema.

You can then create the actual code that you want to run, for example:

```python
from nema.data.data_properties import IntegerValue, ArbitraryFile
from nema.data.tabular.tabular_data_properties import CSVData
from nema.data.plots.figure_data_properties import Image
from nema.run import workflow

import pandas as pd
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass
class Inputs:
    integer_1: IntegerValue
    integer_2: IntegerValue
    arbitrary_file: ArbitraryFile


@dataclass
class Output:
    result_table: CSVData
    result_data: IntegerValue
    image_result: Image


@workflow(
    input_global_id_mapping={ # this is the mapping of the input data to the global IDs (in the Nema project)
        # if they're 0, Nema will create the artifacts for you
        "integer_1": 0,
        "integer_2": 0,
        "arbitrary_file": 0,
    },
    output_global_id_mapping={ # this is the mapping of the output data to the global IDs (in the Nema project)
        "result_table": 0,
        "image_result": 0,
        "result_data": 0,
    },
)
def run(inputs: Inputs) -> Output: # this needs to be called `run` for the workflow to work
    result_value = IntegerValue(inputs.integer_1.value * inputs.integer_2.value)

    # output a table
    resulting_table = pd.DataFrame(
        {
            "test_data_1": [inputs.integer_1.value],
            "test_data_2": [inputs.integer_2.value],
            "result": [result_value.value],
        }
    )
    result_table = CSVData(df=resulting_table)

    # Create a simple plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.plot(x, y, label="Sine Wave")
    plt.title("Simple Sine Wave")
    plt.xlabel("x-axis")
    plt.ylabel("y-axis")
    plt.legend()

    plot_output = Image()

    plt.savefig(plot_output.get_file_name_to_save())

    # Read in an arbitrary file
    with inputs.arbitrary_file("r") as f:
        print(f.read())

    return Output(
        result_table=result_table, result_data=result_value, image_result=plot_output
    )

```

To run this workflow locally and upload the results to Nema, run `nema-python workflow run`.
