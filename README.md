### ULU PIXELWISE TASKS (WIP)

_Urban Land Use Predictions with DLTasks_

___

* https://github.com/wri/UrbanLandUse
* https://github.com/wri/dl_jobs

---

```bash
# create product, bands and upload model
$ dl_jobs run setup

# predict (save to dl catalog)
$ dl_jobs run predict test_prod --dev f

# delete product (includes bands)
$ dl_jobs run product.delete test_prod confirm=True
```

