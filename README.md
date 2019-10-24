### ULU PIXELWISE TASKS (WIP)

_Urban Land Use Predictions with DLTasks_

Generates predictions for [wri/UrbanLandUse](https://github.com/wri/UrbanLandUse) using DescartesLabs' [Tasks API](https://docs.descarteslabs.com/descarteslabs/client/services/tasks/readme.html).

___

INSTALL:

```bash
# INSTALL
git clone https://github.com/wri/ulu_pixelwise_tasks.git
cd ulu_pixelwise_tasks
pip install -e .
```

ENV:

* py36 with TF-1.12

REQUIRED (non-pypi) MODULES:

* https://github.com/wri/dl_jobs
* https://github.com/brookisme/mproc

OTHER (version not included/may not be complete):

* rasterio
* requests
* geopandas
* geojson
* pandas
* numpy
* numba

---

[YAML Config](https://github.com/wri/ulu_pixelwise_tasks/tree/master/products) files are used to configure the product and control the arguments passed to the `dl_jobs`.

Here is an example walk through for [test_prod](https://github.com/wri/ulu_pixelwise_tasks/blob/master/products/test_prod.yaml).  Note I've included `--dev f` so that the jobs run on the DLPlatform.  This is required because my `dl_jobs.config.yaml` file has `is_dev: True`.

1. You can create the product, add bands to the product and upload the model by running this:

```bash
$ dl_jobs run setup mexico_city
# if creating a mode product also add that product and bands
$ dl_jobs run product.create mexico_city_mode --dev f
$ dl_jobs run product.add_bands mexico_city_mode --dev f
```

2. You then will need to generate the list of DLTiles to run.  For complicated polygons we are still managing tile creation by hand.  See this [notebook](https://nbviewer.jupyter.org/github/wri/ulu_pixelwise_tasks/blob/master/nb_archive/UrbanIndiaTiles.ipynb) as an example. For simple polygons you can pass `as_dl_job=True`: 

```bash
# this reminds you we are currently setting up complex tiling in notebooks
dl_jobs run setup.tiles test_prod --dev f
# this example runs based on local shape file (note: this may be a long running task)
dl_jobs run setup.tiles mexico_city as_dl_job=True --dev f
```

3. Before prediction you have to select the S2-scenes of interest.  This can happen on the fly or be precomputed before hand. 

We currently recommend computing on the fly but if you do want to pre-compute the best S2-scenes run the line below. Otherwise skip to prediction.

```bash
# it is recommended you skip this step
dl_jobs run scenes test_prod --dev f
```

Finally run the prediction task:

```bash
dl_jobs run predict test_prod --dev f
```

4. ~~Finally if you want to delete the product~~ DELETION DISABLED:

```bash
# deletion has been disabled to avoid accidents. delete product using DL web-UI
# dl_jobs run product.delete test_prod confirm=True
```

---

#### NOTES

https://nominatim.openstreetmap.org/search.php?q=mumbai+india&polygon_geojson=1&format=geojson
