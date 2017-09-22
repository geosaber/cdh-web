# Deploy Notes

## 2.0

- Update default site in Django admin to match deployed site url
- Initialize admin and other users with createcasuser before running
  the data import.
- Import data from the previous version of the site (exported via Django
  dumpdata) using `python manage.py import_datav1 path_to_data.json`