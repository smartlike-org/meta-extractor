# Meta data extractor

[![Blog](https://img.shields.io/badge/blog-blog%2esmartlike%2eorg-blue.svg?style=flat-square)](https://smartlike.org/channel/blog.smartlike.org)
[![Forum](https://img.shields.io/badge/forum-github%20discussions-blue.svg?style=flat-square)](https://github.com/smartlike-org/meta-extractor/discussions)
[![Project](https://img.shields.io/badge/explore-smartlike%2eorg-blue.svg?style=flat-square)](https://smartlike.org/)
[![License: AGPL 3](https://img.shields.io/badge/license-AGPL%203-blue.svg)](https://github.com/smartlike-org/smartlike/LICENSE)

Browser extensions enable two-click donation checkout.

## Install

```
sudo apt-get install python3-venv
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Test

```
python extract.py -test cfg/crawl.toml
```

## Contribute

Smartlike is an open source project. We welcome all sorts of participation. If you notice that a website you care about is not properly parsed, please help us fix it. Let's discuss on our [forum](https://github.com/smartlike-org/meta-extractor/discussions).

## License

[![License: AGPL 3](https://img.shields.io/badge/License-AGPL%203-blue.svg)](https://github.com/smartlike-org/smartlike/LICENSE)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
