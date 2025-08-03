# GEMF

Python package for the GEMF map format. From the format [specification](https://www.cgtk.co.uk/gemf):

> This tile store format is intended to provide a static (i.e. cannot be updated without regenerating from scratch) file containing a large number of tiles, stored
> in a manner that makes efficient use of SD cards and with which it is easy to access individual tiles very quickly. It is intended to overcome the existing issues
> with the way tiles are stored in most existing Android map applications as these are not very scalable.


# Installation
```cmd
pip install gemf-map
```


# Features
Core features are...
- reading `.gemf` map files via the `GEMF.from_file()` classmethod
- creating a GEMF object from PNG or JPG tiles via the `GEMF.from_tiles()` classmethod
- writing a newly created GEMF object to file via the `write()` method

Further features are...
- extracting tiles (PNG or JPG) from binary `.gemf` files via the `save_tiles()` method
- adding tiles to an existing `.gemf` file (TODO)


# Usage
```python
from gemf import GEMF


my_gemf = GEMF.from_file("MY_GEMF.gemf")            # load an existing .gemf file

new_gemf = GEMF.from_tiles("PATH/TO/TILEDIR")        # create a GEMF object from tiles on disk
new_gemf.write("PATH/TO/GEMF_FILE.gemf")             # write GEMF object to .gemf file
```

`.gemf` files may be used in mobile mapping applications like [Locus](https://www.locusmap.app/)
