#!/bin/bash
for file in cat_id_*.gpkg; do
    ogr2ogr $(echo $file | sed s/gpkg/geojsonl/) $file
done
for file in cat_id_*.geojsonl; do
    sed -i"" 's/.*/{ "type": "FeatureCollection", "features": [ & ] }/' $file
done

