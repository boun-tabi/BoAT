# BoAT

Boğaziçi University Annotation Tool for Dependency Parsing

This repository contains an implementation of **BoAT** to easily annotate CoNLL-U files (see https://universaldependencies.org/format.html) for dependency parsing. It also visualizes the parse trees.

## Implementation

### Requirements

- Python 3.6 or higher

### Installation of Python

To check your `python3` version:

```
python3 —version
```

To install Python 3.6:

- On Mac OS X, download from [python.org/downloads/mac-osx](https://www.python.org/downloads/mac-osx/).
- On Linux, run: `sudo apt install python3.6`.

### To work with a virtual Python environment (optional)

Go to the directory of BoAT-master and run the following:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Installation of the modules

- Using requirements.txt:

```bash
pip3 install -r requirements.txt
```

### Implementation Notes

Required resources for validation check (data folder and `validate.py`) are taken from [github.com/universaldependencies/tools](https://github.com/universaldependencies/tools). Some changes are made to the script `validate.py`.

## How to run?

- Go to the directory of BoAT-master
- Run with: `python3 main.py`

To use this tool for a specific language, giving the language as an argument will check your sentences through validation code. For example:

```bash
python3 main.py -lang tr
```

## How to use?

Check the user manual.

## Citation

If you make use of the tool, please cite the following papers:

```bib
to be added
```

```bib
@inproceedings{turk-etal-2019-turkish,
    title = "{T}urkish Treebanking: Unifying and Constructing Efforts",
    author = {T{\"u}rk, Utku  and
      Atmaca, Furkan  and
      {\"O}zate{\c{s}}, {\c{S}}aziye Bet{\"u}l  and
      K{\"o}ksal, Abdullatif  and
      Ozturk Basaran, Balkiz  and
      Gungor, Tunga  and
      {\"O}zg{\"u}r, Arzucan},
    booktitle = "Proceedings of the 13th Linguistic Annotation Workshop",
    month = aug,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W19-4019",
    doi = "10.18653/v1/W19-4019",
    pages = "166--177",
}
```
