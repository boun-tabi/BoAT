# BoAT
BOUN Annotation Tool for Dependency Parsing

This tool is written in Python3 with PySide2 library. You can run it with:
```
python3 main.py
```
If you use this tool for a specific language, giving the language as an argument will check your sentences through validation code of https://github.com/universaldependencies/tools. For example:
```
python3 main.py tr
```

Required libraries:
```
PySide2
```

## Validation Check
Required resources for validation check(data folder and validate.py) is borrowed from https://github.com/universaldependencies/tools. Some changes are made to validate.py code.

## Screenshots

![](https://live.staticflickr.com/65535/48015158961_238975f2d8.jpg)

Loading page
<br/><br/><br/>


![](https://live.staticflickr.com/65535/48015171563_6c2b4d6ac0_b.jpg)

Main page

# Citation

If you use our data or code for academic work, please cite (Not Final Yet):

```
@inproceedings{turk2019efforts,
    Author = {T\"{u}rk, Utku and Atmaca, Furkan and \"{O}zate\c{s}, \c{S}aziye Bet\"{u}l and K\"{o}ksal, Abdullatif and \"{O}zt\"{u}rk, Balk{\i}z and G\"{u}ng\"{o}r, Tunga and \"{O}zg\"{u}r, Arzucan},
    booktitle = {Proceedings of the 13$^{th}$ Linguistic Annotation Workshop},
    Title = {{Turkish Treebanking: Unifying and Constructing Efforts}},
    Pages = {},
    Year = {2019},
    Organization = {Association for Computational Linguistcs}
}
```
