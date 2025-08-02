Planetary coverage package
==========================

<img src="https://docs.planetary-coverage.org/1.2.0/_static/planetary-coverage-logo.svg" align="right" hspace="50" vspace="50" height="200" alt="Planetary coverage logo">

[
    ![CI/CD](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/badges/main/pipeline.svg)
    ![Coverage](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/badges/main/coverage.svg)
](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/pipelines/main/latest)
[
    ![Documentation Status](https://readthedocs.org/projects/planetary-coverage/badge/?version=latest)
](https://readthedocs.org/projects/planetary-coverage/builds/)

[
    ![PyPI](https://img.shields.io/pypi/v/planetary-coverage.svg?logo=pypi&logoColor=white)
](https://pypi.org/project/planetary-coverage/)
[
    ![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/planetary-coverage?logo=condaforge&logoColor=white)
](https://anaconda.org/conda-forge/planetary-coverage)
[
    ![Python](https://img.shields.io/pypi/pyversions/planetary-coverage.svg?logo=Python&logoColor=white)
](https://pypi.org/project/planetary-coverage/)
[
    ![License](https://img.shields.io/pypi/l/planetary-coverage.svg)
](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/blob/main/LICENSE.md)


[
    ![Docs](https://img.shields.io/badge/Docs-docs.planetary--coverage.org-blue?&color=orange&logo=Read%20The%20Docs&logoColor=white)
](https://docs.planetary-coverage.org)
[
    ![Software Heritage](https://archive.softwareheritage.org/badge/origin/https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/)
](https://archive.softwareheritage.org/browse/origin/?origin_url=https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/)
[
    ![DOI](https://data.caltech.edu/badge/DOI/10.60487/cgxm-grps.svg)
](https://doi.org/10.60487/cgxm-grps)


---

The [planetary-coverage](https://docs.planetary-coverage.org)
package is a toolbox to perform surface coverage analysis based on orbital trajectory calculations.
Its main intent is to provide an easy way to compute observation
opportunities of specific region of interest above the Galilean
satellites for the ESA-Juice mission but could be extended in the
future to other space mission.

It is actively developed by the
[Observatoire des Sciences de l'Univers Nantes Atlantique](https://osuna.univ-nantes.fr)
(OSUNA, CNRS-UAR 3281) and the
[Laboratory of Planetology and Geosciences](https://lpg-umr6112.fr)
(LPG, CNRS-UMR 6112) at Nantes University (France), under
[ESA-Juice](https://sci.esa.int/web/juice) and [CNES](https://cnes.fr) founding support.

<p align="center">
  <img src="https://docs.planetary-coverage.org/1.2.0/_images/logos.png" alt="logos"/>
</p>

📦 Installation
---------------

The package is available on [PyPI](https://pypi.org/project/planetary-coverage/) and can be installed very easily:

- If you are in a [`Jupyter environnement`](https://jupyter.org/), you can use the magic command `%pip` in a notebook cell and ▶️ `Run` it:
```bash
%pip install planetary-coverage
```

- or, if you are using a `terminal environment`, you can do:
```bash
pip install planetary-coverage
```

> __Note:__ If you plan to use this package with Juice and you want to enable [PTR simulation with AGM](https://esa-ptr.readthedocs.io/).
> You can add a `juice` extra parameter in the `pip` install command: `pip install planetary-coverage[juice]`


The package is also available on [conda-forge](https://anaconda.org/conda-forge/planetary-coverage)
and you can install it with `conda`:

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict

conda install planetary-coverage
```

✏️ How to cite this package
---------------------------

If you use this package for your analyses, please consider using the following citation:

> Seignovert _et al._ 2025,
> [Planetary coverage (1.2.0)](https://docs.planetary-coverage.org/1.2.0/),
> doi:[10.60487/cgxm-grps](https://doi.org/10.60487/cgxm-grps)

or can use either:
- [planetary-coverage.bib](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/raw/main/planetary-coverage.bib?inline=false)
- [citation.cff](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/raw/main/CITATION.cff?inline=false)
- [codemeta.json](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/raw/main/codemeta.json?inline=false)


⚡️ Issues and 💬 feedback
-------------------------

If you have any issue with this package, we highly recommend to take a look at:

- 📚 our [extended documentation online](https://docs.planetary-coverage.org/).
- 📓 the collection of [notebook examples](https://juigitlab.esac.esa.int/notebooks/planetary-coverage).

If you did not find a solution there, feel free to:

- 📝 [open an issue](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/issues/new) (if you have an account on the [Juice Gitlab](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage)).
- ✉️ send us an email at [&#99;&#111;&#110;&#116;&#97;&#99;&#116;&#64;&#112;&#108;&#97;&#110;&#101;&#116;&#97;&#114;&#121;&#45;&#99;&#111;&#118;&#101;&#114;&#97;&#103;&#101;&#46;&#111;&#114;&#103;](&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#99;&#111;&#110;&#116;&#97;&#99;&#116;&#64;&#112;&#108;&#97;&#110;&#101;&#116;&#97;&#114;&#121;&#45;&#99;&#111;&#118;&#101;&#114;&#97;&#103;&#101;&#46;&#111;&#114;&#103;
)


🎨 Contribution and 🐛 fix bugs
-------------------------------

Contributions are always welcome and appreciated.
An account on the [Juice Giltab](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage) is required.
You also need to install the recent version of [Poetry](https://python-poetry.org/docs/) (`2.x`), for example on _Linux/macOS/Windows (WSL)_, you can run this command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then you are good to go!

1. 🍴 [Fork this project](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/forks/new)

2. 🐑 Clone and 📦 install the repository locally:

```bash
git clone https://juigitlab.esac.esa.int/<YOUR_USERNAME>/planetary-coverage
cd planetary-coverage

poetry install --all-groups
```

3. ✍️ Make your edits and 🚧 write the tests.

4. 🚦 Check that the linter and formatter are happy 😱 🤔 😃 :
```bash
poetry run ruff format --diff
poetry run ruff check
```

5. 🛠 Check that your tests succeed 👍 and you have a coverage of 100% ✨ :

```bash
poetry run pytest
```

6. 📖 Complete and ⚙️ build the documentation (if needed):
```bash
cd docs/
poetry run make docs
```

7. 📤 Push your changes to your forked branch and 🚀 open a [new merge request](https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/merge_requests/new) explaining what you changed 🙌 👏 💪.


👽 Maintainer section
---------------------

- To add a new contributor, you need to edit the following files:
    - `CITATION.cff`
    - `codemeta.json`
    - `planetary-coverage.bib`

- To release a new version:
```bash
DOI='abcd-efgh' bump-my-version bump [patch|minor|major]
```

> [!note]
> A new tag and release will be published automatically when the bumped branch is merged in `main`.
