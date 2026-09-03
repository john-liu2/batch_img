## batch_img

Batch process (**resize, rotate, remove background, remove GPS, add border,
set transparency, auto do all, get meta info**) image files (**HEIC, JPG, PNG**) by
utilizing **[Pillow / PIL](https://github.com/python-pillow/Pillow)** library.
It can apply the action(s) on a single image file or all image files in the input
folder / directory. Tested working on **macOS** and **Windows**.

### Installation

The `Remove background (make background transparent)` feature depends on `onnxruntime`
library. The 1.24.x and later versions support `Python 3.14`.

#### Requirements

```
python: >=3.12, <3.15
```

#### One-time Setup

Install the Astral's [`uv`](https://github.com/astral-sh/uv) tool once to
prepare for **all** Python tools and packages installation. Install the Astral's
[`uv`](https://github.com/astral-sh/uv) by its standalone installers:

```
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the latest Python by uv command
uv python install 3.13

# Create the Python virtualenv by uv command
uv venv

# Activate the Python virtualenv
source .venv/bin/activate
```

```
# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add uv command into environment search path
$env:Path = "C:\Users\{your_user_name}\.local\bin:$env:Path"

# Create the Python virtualenv by uv command
uv venv

# Activate the Python virtualenv
.venv\Scripts\activate
```

#### Install the `batch_img` tool

Install the `batch_img` tool from PyPI by the Astral's
[`uv`](https://github.com/astral-sh/uv) command:

```
uv pip install --upgrade batch_img
```

### Usage

#### Sample command line usage:

```
✗ batch_img --version
1.4.5


✗ batch_img auto ~/Documents
Resize to 1920-pixel max length. Remove GPS location info. Add 5-pixel width black color border.
...
Auto processed 8/8 files
✅ Processed the image file(s)


✗ batch_img info -i ~/Documents
...
Read meta info from 10/10 files
Elapsed time: 0.42 s
```

All image operations accept `-i` / `--input` for the input file or directory,
for example `batch_img resize -i ~/Pictures -l 1920`. You can get metadata info
from files with `batch_img info -i <file-or-directory>`.
Use `--quiet` with `info` sub-command to write the metadata to a local text file:
`batch_img --quiet info -i ~/Downloads` writes `img_meta_info.txt`
in the working directory.

### Contribution

Contributions are welcome!
Please see the details
in [Contribution Guidelines](https://github.com/john-liu2/batch_img/blob/main/CONTRIBUTING.md)

### Help

#### Top level commands help:

```
✗ batch_img --help
Usage: batch_img [OPTIONS] COMMAND [ARGS]...

  Batch image processing tool.

Options:
  -i, --input PATH  Input an image file or a directory.
  --quiet           Process image(s) with minimum stdout in quiet mode.
  --update          Update the tool to the latest version.
  --version         Show the tool's version.
  --help            Show this message and exit.

Commands:
  auto         Auto process (resize to 1920-px, remove GPS, add border)...
  border       Add internal border to image(s), not expand the size.
  do-effect    Do special effect to image(s).
  grayscale    Convert to grayscale image(s).
  info         Print EXIF information for the input image file(s).
  remove-bg    Remove background (make background transparent) in image(s).
  remove-gps   Remove GPS location info in image(s).
  resize       Resize image(s).
  rotate       Rotate image(s).
  transparent  Set transparency on image(s).
```

#### The `auto` sub-command CLI options:

```
✗ batch_img auto --help
Usage: batch_img auto [OPTIONS]

  Auto process (resize to 1920-px, remove GPS, add border) image file(s).

Options:
  -o, --output TEXT   Output file path. If not specified, replace the input
                      file.  [default: ""]
  -i, --input PATH    Input image file or directory.
  -ar, --auto_rotate  Auto-rotate image (experimental)
  --help              Show this message and exit.
```

#### The `border` sub-command CLI options:

```
✗ batch_img border --help
Usage: batch_img border [OPTIONS]

  Add internal border to image file(s), not expand the size.

Options:
  -o, --output TEXT               Output file path. If not specified, replace
                                  the input file.  [default: ""]
  -i, --input PATH                Input image file or directory.
  -bw, --border_width INTEGER RANGE
                                  Add border to image file(s) with the
                                  border_width. 0 - no border.  [default: 5;
                                  0<=x<=30]
  -bc, --border_color TEXT        Add border to image file(s) with the
                                  border_color string.  [default: gray]
  --help                          Show this message and exit.
```

#### The `do-effect` sub-command CLI options:

```
✗ batch_img do-effect --help
Usage: batch_img do-effect [OPTIONS]

  Do special effect to image file(s).

Options:
  -o, --output TEXT             Output file path. If not specified, replace
                                the input file.  [default: ""]
  -i, --input PATH              Input image file or directory.
  -e, --effect [blur|hdr|neon]  Do special effect to image file(s): blur, hdr,
                                neon.  [default: neon]
  --help                        Show this message and exit.
```

#### The `remove-bg` sub-command CLI options:

```
✗ batch_img remove-bg --help
Usage: batch_img remove-bg [OPTIONS]

  Remove background (make background transparent) in image file(s).

Options:
  -o, --output TEXT  Output file path. If not specified, replace the input
                     file.  [default: ""]
  -i, --input PATH   Input image file or directory.
  --help             Show this message and exit.
```

#### The `remove-gps` sub-command CLI options:

```
✗ batch_img remove-gps --help
Usage: batch_img remove-gps [OPTIONS]

  Remove GPS location info in image file(s).

Options:
  -o, --output TEXT  Output file path. If not specified, replace the input
                     file.  [default: ""]
  -i, --input PATH   Input image file or directory.
  --help             Show this message and exit.
```

#### The `resize` sub-command CLI options:

```
✗ batch_img resize --help
Usage: batch_img resize [OPTIONS]

  Resize image file(s).

Options:
  -o, --output TEXT           Output file path. If not specified, replace the
                              input file.  [default: ""]
  -i, --input PATH            Input image file or directory.
  -l, --length INTEGER RANGE  Resize image file(s) on original aspect ratio to
                              the max side length. 0 - no resize.  [default:
                              0; x>=0]
  --help                      Show this message and exit.
```

#### The `rotate` sub-command CLI options:

```
✗ batch_img rotate --help
Usage: batch_img rotate [OPTIONS]

  Rotate image file(s).

Options:
  -o, --output TEXT           Output file path. If not specified, replace the
                              input file.  [default: ""]
  -i, --input PATH            Input image file or directory.
  -a, --angle [0|90|180|270]  Rotate image file(s) to the clockwise angle. 0 -
                              no rotate.  [default: 0]
  --help                      Show this message and exit.
```

#### The `transparent` sub-command CLI options:

```
✗ batch_img transparent --help
Usage: batch_img transparent [OPTIONS]

  Set transparency on image file(s).

Options:
  -o, --output TEXT               Output file path. If not specified, replace
                                  the input file.  [default: ""]
  -i, --input PATH                Input image file or directory.
  -t, --transparency INTEGER RANGE
                                  Set transparency on image file(s). 0 - fully
                                  transparent, 255 - completely opaque.
                                  [default: 127; 0<=x<=255]
  -w, --white                     Make white pixels fully transparent.
  --help                          Show this message and exit.
```

### License

**batch_img** is distributed under MIT License. Please see details in
[LICENSE](https://github.com/john-liu2/batch_img/blob/main/LICENSE).
