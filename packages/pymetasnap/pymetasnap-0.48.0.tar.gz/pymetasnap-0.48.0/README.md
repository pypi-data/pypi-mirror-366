# pymetasnap [![PyPI version](https://badge.fury.io/py/pymetasnap.svg)](https://badge.fury.io/py/pymetasnap)

pymetasnap is a command-line tool that enables you to extract metadata from the Python Package Index (PyPI). It allows you to retrieve essential information about Python packages hosted on PyPI, including package names, versions, licenses, project URLs, and more.

By leveraging the PyPI API, pymetasnap automates the process of gathering package metadata, making it convenient for developers, researchers, and anyone interested in exploring package information in a structured manner.

## Features

- Retrieve metadata for Python packages from PyPI.
- Extract package names, versions, licenses, and other relevant information.
- Fetch project URLs and version-specific URLs for detailed package exploration.
- Store the extracted metadata in CSV or Excel format for further analysis.

## Installation

You can install pymetasnap using pip:

```bash
pip install pymetasnap
```

### Usage

#### Detached mode

To extract metadata for Python packages from PyPI, use the following command:

```bash
pymetasnap extract --source-path <path_of_the_txt_file> --output <output_path> --format <input_format>
```

Replace the following placeholders in the command:

- `<path_of_the_txt_file>`: Names of the packages to retrieve metadata for (separated by spaces).
- `<output_path>`: Path to store the extracted metadata file.
- `<input_format>`: Format of the input requirements file (pip_list or pip_freeze).

#### Interactive mode

Additionally, an interactive mode is available, allowing you to provide the required values through user prompts as follows:

[![asciicast](https://asciinema.org/a/4xs1k6elJ40kJ4YhKxuS93Rfh.svg)](https://asciinema.org/a/4xs1k6elJ40kJ4YhKxuS93Rfh)

## Output

The tool generates a file containing the extracted metadata for the specified packages in the provided output format (CSV or Excel). The output file includes columns for package name, version, license, repository URL, project URL, and version-specific URL. This information can be used for various purposes, such as dependency analysis, license compliance, or package research.

## Contributing

Contributions to pymetasnap are welcome! If you encounter any issues or have suggestions for improvements, please open an issue on the project's GitHub repository.

When contributing, please ensure that you follow the existing coding style, write tests for new features, and make sure the tests pass before submitting a pull request.

## License

pymetasnap is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

## Acknowledgments

The pymetasnap tool builds upon the PyPI API to provide a convenient way to access package metadata. We would like to express our gratitude to the PyPI maintainers and the Python community for their continuous efforts in maintaining and improving the Python Package Index.

## Contact

For any inquiries or feedback, please contact the project maintainer at using the issues tab.
