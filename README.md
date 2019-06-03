### ULU PIXELWISE TASKS (WIP)

_Urban Land Use Predictions with DLTasks_

Generates predictions for [wri/UrbanLandUse](https://github.com/wri/UrbanLandUse) using DescartesLabs' Task API.

___

INSTALL:

```bash
# INSTALL
git clone https://github.com/wri/ulu_pixelwise_tasks.git
cd ulu_pixelwise_tasks
pip install -e .
```

ENV:

* using py36 with TF-1.12

REQUIRED (non-pypi) MODULES:

* https://github.com/wri/dl_jobs
* https://github.com/brookisme/mproc

---

[YAML Config files](https://github.com/wri/ulu_pixelwise_tasks/tree/master/products), along with DLJobs are used to generate predictions. 

Here is an example walk through for [test_prod](https://github.com/wri/ulu_pixelwise_tasks/blob/master/products/test_prod.yaml).  Note I've included `--dev f` so that the jobs run on the DLPlatform.  This is required because my `dl_jobs.config.yaml` file has `dev=True`.

1. You can create the product, add bands to the product and upload the model by running this:

```bash
$ dl_jobs run setup test_prod
```

2. You then will need to generate the list of DLTiles to run.  For simple polygons: 

```bash
$ dl_jobs run setup.tiles test_prod --dev f
```

However for complicated polygons we are still managing tile creation by hand.  See this [notebook](https://github.com/wri/ulu_pixelwise_tasks/blob/master/nb_archive/UrbanIndiaTiles.ipynb) as an example.

3. Before prediction you have to select the S2-scenes of interest.  This can happen on the fly or be precomputed before hand. To compute the S2-scenes on the fly simply run:

```bash
$ dl_jobs run predict test_prod --dev f
```

To pre-compute the best S2-scenes run:

```bash
dl_jobs run setup.scenes test_prod --dev f
```

and then:

```bash
$ dl_jobs run predict test_prod --dev f
```

4. Finally if you want to delete the product:

```
$ dl_jobs run product.delete test_prod confirm=True
```

---

#### NOTES

https://nominatim.openstreetmap.org/search.php?q=mumbai+india&polygon_geojson=1&format=geojson
