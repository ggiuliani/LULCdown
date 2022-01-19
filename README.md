# LULCdown
This is the Python code implementation of Switzerland's downscaling aglorithm of Land Cover & Land Use data.
Dependencies: [GDAL](https://gdal.org), [NumPy](https://numpy.org), [xlrd](https://github.com/python-excel/xlrd), [Pandas](https://pandas.pydata.org)

Two versions of the code are available:
- a [single-node version](single) to be executed on a single computer
- a [parallelized version](parallel) to be executed on a cluster together with a script for merging the processed tiles
The [expert table](expert_table_72cat_v4.xls) is also provided.

The Land Use/Land Cover data are freely available at [Federal Office for Statistics](https://www.bfs.admin.ch/bfs/fr/home/statistiques/espace-environnement/enquetes/area.html) and the base map at swisstopo [TLM3D](https://www.swisstopo.admin.ch/en/geodata/landscape/tlm3d.html)

The outputs are available on the University of Geneva Digital Repository [Yareta](https://yareta.unige.ch/) and can be downloaded at: [https://doi.org/10.26037/yareta:dlx3hu54jfa3ne3c2xjfcnqpxm](https://doi.org/10.26037/yareta:dlx3hu54jfa3ne3c2xjfcnqpxm)

The methodology and results are presented in the following (submitted) paper:
*Giuliani G., Rodila D., Külling N., Maggini R., Lehmann A., Downscaling Switzerland Land Use/Land Cover data using nearest neighbors and an expert system. **Remote Sensing***
