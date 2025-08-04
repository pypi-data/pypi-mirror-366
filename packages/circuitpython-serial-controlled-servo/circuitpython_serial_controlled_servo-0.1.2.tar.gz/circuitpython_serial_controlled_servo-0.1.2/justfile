# SPDX-FileCopyrightText: Copyright (c) 2025 Jacques Supcik
#
# SPDX-License-Identifier: MIT

[working-directory: 'docs']
docs:
    make html

[working-directory: 'docs']
docs-clean:
    make clean


show-docs:
    python -m http.server 8000 --bind localhost --directory docs/_build/html
