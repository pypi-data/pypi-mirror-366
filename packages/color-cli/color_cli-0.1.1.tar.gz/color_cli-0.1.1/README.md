# <p align='center'>Color CLI</p>
A lightweight Python package to add color and character to your command-line output.

<details>

<summary>Table of Content</summary>

- [Description](#description)
- [Features](#features)
- [Usage](#usage)
- [Supported Colors & Attributes](#supported-colors--attributes)
- [License](#license)
- [Future Work](#future-work)

</details>


## Description
This package will house a utility package that will help the users to be able to customize and colorize their function outputs to better standout in their terminal.

## Features
- Support 8 colors and 4 styles
- Useful for CLI tools, scripts and developer logs
- Cross-platform via `termcolor`

## Installation

Install locally for development:
```bash
git clone https://github.com/Abdulrahman-K-S/color-CLI.git
cd colorME
pip install -e .
```

Or use it in your project:
```bash
pip install git+https://github.com/Abdulrahman-K-S/color-CLI.git
```

## Usage

```py
from color_cli import color_text

# Basic output
print(color_text('Hello World!', color='green'))

# With attributes
print(color_text('WARNING!', color='red', attrs=['bold', 'underline']))
```

## Supported Colors & Attributes
**Colors:**

`grey`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`

**Attributes:**

`bold`, `underline`, `reverse`, `blink`

## License
This project is licensed under the [Apache License 2.0](LICENSE).

## Future Work
- Add a support for background colors
- Add CLI features such as `color-cli 'hello' --color blue --attrs bold`
- Add more customization

## Contributors
<a href="https://github.com/Abdulrahman-K-S/colorME/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Abdulrahman-K-S/colorME" />
</a>

A huge thank you to all the contributors!

If you want to be a contributor check the [CONTRIBUTING.md](CONTRIBUTING.md) file.