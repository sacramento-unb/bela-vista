# Bela Vista environmental dashboard

Legacy Streamlit study application for uploading a geospatial file, intersecting
it with bundled embargo data and viewing tables, charts and a Folium map. The
repository also contains MapBiomas/Indigenous-land layers, farm-specific files
under `fazendas/` and CAR download helpers.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run Home.py
```

`Homev2.py` and `teste.py` are alternative historical entry points. No automated
tests or CI are present, and the application was not run during this audit.

## Security and data hold

The repository contains property-identifying filenames and farm GeoJSON/GPKG
artifacts. The bundled embargo schema includes identity/contact-related fields;
the UI drops selected columns only after reading them. Do not publish,
redistribute or demonstrate this repository with real data until ownership,
provenance, legal basis and minimization are confirmed.

`car_downloader.py` disables TLS verification, prints a URL containing a property
identifier and writes to a machine-specific Windows path. It is not safe to run
in its current form. Rotate any related credentials or access tokens if the
source review finds exposure; history sanitization is a separate approved task.

The existing license applies only as stated there and does not establish rights
to third-party environmental or farm datasets.
