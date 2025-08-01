# Mirror Man

Mirror Man is a command-line tool to manage software mirror sources for your Linux distribution. It simplifies the process of switching between different mirror sources, helping you to get faster package downloads.

## Features

*   Backup your current mirror sources before making changes.
*   Switch to Aliyun mirror sources for Ubuntu and CentOS.
*   Planned support for Huawei Cloud and other mirror sources.

## Installation

```bash
pip install mirror-man
```

## Usage

To switch to the Aliyun mirror source, run the following command:

```bash
mirror-man aliyun
```

This will automatically detect your operating system and configure the appropriate Aliyun mirror source. Your existing sources file will be backed up with a timestamp.

### Supported Operating Systems

*   Ubuntu 22.04
*   Ubuntu 24.04
*   CentOS 7

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
