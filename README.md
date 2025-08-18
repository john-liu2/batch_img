## batch_img

Batch processing image files by utilizing **[Pillow / PIL](https://github.com/python-pillow/Pillow)** library.
Resize, rotate, add border or do default actions on a single image file or all image files in a folder.
Tested these image file formats (**HEIC, JPG, PNG**) on macOS.

### Usage

#### Sample command lines:

```
✗ batch_img --version
0.0.7

✗ batch_img rotate --degree 90 ~/Downloads/IMG_0070.HEIC
...
✅ Processed the image file(s)
```

### Help

#### Top level commands help:

```
✗ batch_img --help
Usage: batch_img [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show this tool's version
  --help     Show this message and exit.

Commands:
  border    Add border to image file(s)
  defaults  Process image file(s) with default actions: 1) resize to...
  resize    Resize image file(s)
  rotate    Rotate image file(s)
```

#### The `border` sub-command CLI options:

```
✗ batch_img border --help
Usage: batch_img border [OPTIONS] SRC_PATH

  Add border to image file(s)

Options:
  -bw, --border_width INTEGER RANGE
                                  Add border to image file(s) with the
                                  border_width. 0 - no border  [default: 5;
                                  x>=0]
  -bc, --border_color TEXT        Add border to image file(s) with the
                                  border_color string  [default: gray]
  --help                          Show this message and exit.
```

#### The `defaults` sub-command CLI options:

```
✗ batch_img defaults --help
Usage: batch_img defaults [OPTIONS] SRC_PATH

  Process image file(s) with default actions: 1) resize to 1280; 2) add
  5-pixel gray color border; 3) auto-rotate if needed

Options:
  --help  Show this message and exit.
```

#### The `resize` sub-command CLI options:

```
✗ batch_img resize --help
Usage: batch_img resize [OPTIONS] SRC_PATH

  Resize image file(s)

Options:
  -l, --length INTEGER RANGE  Resize image file(s) on original aspect ratio to
                              the length. 0 - no resize  [default: 0; x>=0]
  -o, --output TEXT           Output file path. If skipped, use the current
                              dir path  [default: ""]
  --help                      Show this message and exit.
```

#### The `rotate` sub-command CLI options:

```
✗ batch_img rotate --help
Usage: batch_img rotate [OPTIONS] SRC_PATH

  Rotate image file(s)

Options:
  -a, --angle INTEGER RANGE  Rotate image file(s) to the clockwise angle. 0 -
                             no rotate  [default: 0; x>=0]
  -o, --output TEXT          Output file path. If skipped, use the current dir
                             path  [default: ""]
  --help                     Show this message and exit.
```
