# Good cat videos

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

We'll come up with a better name later.

## Things to fix so far
- add mechanism to check if row is already in saved dataset (just check if videoid exists in current csv)
- check if csv exists already (and if it does append to that instead of overwriting)

Packages managed using pipenv. Check the pipfile for list of dependencies.
If pipfile lock isn't working, use --pre (need it for the dev dependencies).