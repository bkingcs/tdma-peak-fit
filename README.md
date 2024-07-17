# tdma-peak-fit
Software to determine growth factors from TDMA data

This is alpha software, a work in progress. It performs multi-peak fitting of TDMA data on a log-normal scale. 

The software is built on Python 3.10, with a variety of packages. The primary UI is built using Pyside2 bindings to PyQT5. I'll eventually move everything over to pure PyQT6. 

---

# TODO

- [ ] Upgrade to PyQT6
- [ ] Integrate bumpversion for versioning
- [ ] Clean up repo and remove old files, standardize for public release

- [ ] Add a place for user to enter RH. It's required for the Kappa calculation. Set a default value of 85%

- [ ] Compute growth factor 
- [ ] Compute Kappa from gf


- [ ] Can we create cm^3 as an exponent?
- [ ] Do not hard code skipping top 18 rows, but scan to look for "Sample #"

### Other TODOs

* Check Nahin's data

--- 

# Configuration

### Pycharm

* Add external documentation support so you can get quick links to PyQt5 reference material.   
  GO to File --> Settings --> Tools --> External Documentation. Then, add a new entry for PySide2, then for the value, enter the following:  
  `http://doc.qt.io/qtforpython-5/PySide2/{module.basename}/{class.name}.html#PySide2.{module.basename}.{element.qname}`

### Building Executable for Windows (taken from LILAC docs)
- [ ] Build EXE for Windows
  - Activate your HTDMA environment
  - `pyinstaller main.spec --workpath ./build --distpath ./dist --clean`

  
### PyQt5 / PySide2 Resources

* https://www.pythonguis.com/pyside-tutorial/

