## batch_img

Batch processing image files by utilizing **[Pillow / PIL](https://github.com/python-pillow/Pillow)** library.

### Usage

#### Sample command lines:

```
✗ batch_img --version
0.0.7

✗ batch_img action ~/Downloads/IMG_0070.HEIC --rotate 180
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
  action  Batch processing a image file or all image files in a folder path
```

#### The `action` command CLI options:

```
✗ batch_img action --help
Usage: batch_img action [OPTIONS] SRC_PATH

  Batch processing a image file or all image files in a folder path

Options:
  --add_border <INTEGER TEXT>...  Add border to the image file(s) with
                                  'border_width  border_color'.  [default: 0,
                                  red]
  --resize INTEGER                Resize the image file(s) on current aspect
                                  ratio to the width. 0 - no resize  [default:
                                  0]
  --rotate INTEGER                Rotate the image file(s) to the given degree
                                  clock-wise. 0 - no rotate  [default: 0]
  --help                          Show this message and exit.
```
