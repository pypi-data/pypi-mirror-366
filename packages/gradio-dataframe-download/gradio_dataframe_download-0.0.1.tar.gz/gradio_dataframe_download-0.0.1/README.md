
# `gradio_dataframe_download`

![Static Badge](https://img.shields.io/badge/version%20-%200.0.1%20-%20orange)

A `gradio` component for stateless DataFrame download as CSV.

Gradio's built-in components for file handling, primarily `DownloadButton` and `File`, are designed around a server-centric paradigm. The fundamental operational model of gr.DownloadButton involves its `value` parameter, which expects a string representing a file path or a URL that points to a file accessible by the server. When a Gradio function returns a file path to a `DownloadButton`, the Gradio backend makes this file available for download through a specialized `file=` endpoint, effectively serving it to the user's browser.

When dealing with dynamic data objects like a Pandas `DataFrame` that exists only in the server's memory, a developer must explicitly serialize and save it to the server's filesystem, for instance, by calling a method like `df.to_csv("temp.csv")`. The path to this file is then returned to the `DownloadButton`. This server-side I/O operation and creation of a physical file on the server's disk, is what this custom component seeks to circumvent.

In ephemeral systems like Docker containers, serverless platforms (e.g., AWS Lambda, Google Cloud Functions), or read-only filesystems common in managed hosting, writing to the local disk is often restricted, non-persistent, or entirely disallowed.

## Installation

```bash
pip install gradio_dataframe_download
```

## Usage

```python
"""Custom component demo module.

Functions:
    generate_dataframe: Generate a `pandas.DataFrame` for display & download.
"""
import pathlib

import gradio as gr
import numpy as np
from pandas import DataFrame, date_range

from gradio_dataframe_download import DataFrameDownload


def generate_dataframe(nrows: int) -> tuple[DataFrame, DataFrame]:
    """Generate a `pandas.DataFrame` for display & download.
    
    Args:
        nrows: Number of rows to generate for the DataFrame.
    
    Returns:
        A tuple of duplicate generated DataFrame objects.
    """
    data = {
        "ID": np.arange(nrows),
        "Name": map(lambda x: f"NAME_{x}",  range(nrows)),
        "Value": np.random.randn(nrows),
        "Timestamp": date_range(start="2024-01-01", periods=nrows, freq="D"),
        "Category": np.random.choice(range(10), size=nrows),
    }
    dataframe = DataFrame(data)
    return dataframe, dataframe


with gr.Blocks() as demo:
    gr.Markdown("""
    # DataFrame Download Button Demo

    This application demonstrates a custom Gradio component that allows downloading a Pandas DataFrame
    as a CSV file, directly from the client-side, without saving the file on the server.

    1. Adjust the slider to set the number of rows for the DataFrame.
    2. Click 'Generate Data' to create the DataFrame and display it.
    3. The 'Download DataFrame' button will become active.
    4. Click 'Download DataFrame' to download the data as a CSV file.
    """)

    with gr.Row(equal_height=True):
        with gr.Column():
            row_slider = gr.Slider(
                minimum=10,
                maximum=1000,
                value=10,
                step=10,
                label="Row count",
                scale=1
            )
        with gr.Column():
            generate_btn = gr.Button("Generate DataFrame", scale=1)
            download_btn = DataFrameDownload(
                label="Download DataFrame",
                variant="huggingface",
                size="lg",
                scale=1,
            )

    with gr.Column():
        display = gr.Dataframe(label="DataFrame Preview")

    generate_btn.click(
        fn=generate_dataframe, inputs=row_slider, outputs=[display, download_btn]
    )

if __name__ == "__main__":
    demo.launch()

```

## `DataFrameDownload`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"Download DataFrame"</code></td>
<td align="left">Component label text.</td>
</tr>

<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
IntoFrame | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A DataFrame to be serialised for download or a callable.</td>
</tr>

<tr>
<td align="left"><code>variant</code></td>
<td align="left" style="width: 25%;">

```python
Literal["primary", "secondary", "stop"]
```

</td>
<td align="left"><code>"secondary"</code></td>
<td align="left">Style variant; 'primary', 'secondary' or 'stop'.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">Component visibility flag.</td>
</tr>

<tr>
<td align="left"><code>size</code></td>
<td align="left" style="width: 25%;">

```python
Literal["sm", "md", "lg"]
```

</td>
<td align="left"><code>"lg"</code></td>
<td align="left">Size of the button; 'sm', 'md' or 'lg'.</td>
</tr>

<tr>
<td align="left"><code>icon</code></td>
<td align="left" style="width: 25%;">

```python
str | Path | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">URL or path to the icon file to display within the button.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Relative size compared to adjacent Components.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Minimum pixel width (if sufficient screen space).</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">Component interactivity flag.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Optional string assigned as component ID in the HTML DOM.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">CSS classes assigned to component in HTML DOM.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">`Blocks` context render flag.</td>
</tr>
</tbody></table>

### Events

| name | description |
|:-----|:------------|
| `click` | Triggered when the DataFrameDownload is clicked. |

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, none.
- **As input:** Should return, a DataFrame object.

 ```python
 def predict(
     value: None
 ) -> IntoFrame | None:
     return value
 ```
