### ULU PIXELWISE TASKS (WIP)

_Urban Land Use Predictions with DLTasks_

___

* https://github.com/wri/UrbanLandUse
* https://github.com/wri/dl_jobs

---

```bash
# create product, bands and upload model
$ dl_jobs run setup test_prod

# predict (save to dl catalog)
$ dl_jobs run predict test_prod --dev f

# delete product (includes bands)
$ dl_jobs run product.delete test_prod confirm=True
```

---

#### ENV NOTES

* using py36 with TF-1.12 to math DL py36-gpu image.
* need to use prompt_kit=1 to get rid of `ensure_dir_exists` bug
* then a new error appeared `AttributeError: type object 'IOLoop' has no attribute 'initialized'`
* had a pip version of pyzqm which i removed and it worked correctly
*
#### NOTES

https://nominatim.openstreetmap.org/search.php?q=mumbai+india&polygon_geojson=1&format=geojson
