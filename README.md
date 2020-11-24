# judging cat videos

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Basically a site where you put in the title (or URL?) of a cat video and we'll tell you if it's good or not i.e. if you should watch it.

Basic frontend made for project. Still lots of tweaking to do (not to mention actual model building) but I just wanted to template out the flow of the site.

Now running on a very (very) simple linear regression model based on the input video title and most popular words.

The site is live here: https://judging-cat-videos.herokuapp.com/

## Running the site locally
- install all dependencies from pipfile
- run app.py
- check site running on localhost

Packages managed using pipenv. Check the pipfile for list of dependencies.
If pipfile lock isn't working, use --pre (usually need it for the dev dependencies).