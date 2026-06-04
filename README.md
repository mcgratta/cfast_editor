# cfast_editor

This repository is a sandbox for a new graphical user interface for CFAST.

The controlling script is called `Home_Page.py` and it is invoked simply by typing
```
python Home_Page.py
```
The script uses modules `PySide6` and `f90nml`.

For the moment, the script just reads in various namelist records as defined in `Home_Page.py` and types out all the parameters on each tab. Formatting will come later after reading and writing routines have been tested.
