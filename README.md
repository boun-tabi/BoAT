# BoAT
BOUN Annotation Tool for Dependency Parsing

This repository contains an implementation of the **BoAT** to annotate the CoNLL-U files (https://universaldependencies.org/format.html) easily for dependency parsing. It also visualizes the parse trees.

## Implementation

### Requirements
- Python 3.6.x
- PySide2 5.13.1
- regex 2019.06.19

### Installation of Python 3.6.x
To check your python3 version:
```
python3 —version
```
To install Python 3.6.x:
Mac OS X -> download from https://www.python.org/downloads/mac-osx/
Linux -> sudo apt install python3.6

### To work in the Virtual Environment (optional)
Go to the directory of BoAT-master
```
python3 -m venv boat_venv
source boat_venv/bin/activate
```

### Installation of the modules
- Install them one by one:
```
pip3 install PySide2==5.13.1
pip3 install regex==2019.06.19
```

- Or install using requirements.txt:
```
pip3 install -r requirements.txt
```

### Implementation Notes
Required resources for validation check(data folder and validate.py) is borrowed from https://github.com/universaldependencies/tools. Some changes are made to validate.py.

## How to run?
- Go to the directory of BoAT-master
- Run with:
```
python3 main.py
```

To use this tool for a specific language, giving the language as an argument will check your sentences through validation code of https://github.com/universaldependencies/tools. For example:
```
python3 main.py tr
```

## How to use?
Check the user manual.

## Citation
If you make use of the tool, please cite the following paper:

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
