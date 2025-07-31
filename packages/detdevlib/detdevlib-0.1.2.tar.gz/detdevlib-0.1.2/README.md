# detdevlib
Library containing functions and classes that can be used across all det repositories.

## Contributing
Any branch that creates a merge requests into master will be checked for:
- style (black, isort and pydocstyle)
- passing pytest
It is recommended to run these locally first before pushing.

## Documentation publication
Documentation is published to GitHub pages at https://dynamic-energy-trading.github.io/detdevlib/.
The source code for the site is on the `gh-pages` branch.
Any push to master (via merge request or directly) will automatically build documentation using mkdocs, and then push the changes to the site to `gh-pages` to reduce clutter on master.

## Package publication
Packages are published via GitHub releases