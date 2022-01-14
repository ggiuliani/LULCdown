# LULCdown
This is the Python code implementation of Switzerland's downscaling aglorithm of Land Cover & Land Use data.
Dependencies: [GDAL](https://gdal.org), [NumPy](https://numpy.org), [xlrd](https://github.com/python-excel/xlrd), [Pandas](https://pandas.pydata.org)

Two versions of the code are available:
- a static version to be executed on a single computer
- a parallelized version to be executed on a cluster together with a script for merging the processed tiles
The expert table is also provided.

The methodology and results are presented in the following (submitted) paper:
*Giuliani G., Rodila D., Külling N., Maggini R., Lehmann A., Downscaling Switzerland Land Use/Land Cover data using nearest neighbors and an expert system. **Remote Sensing***
