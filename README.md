# Xonotic By The Numbers
### Yearly statistics pulled from XonStatDB and visualized with Matplotlib

Run this script to generate some visualizations of a year of activity in Xonotic. The following metrics are explored:

- The number of games played per month, by game type.
- The number of distinct players per month.
- A heatmap of how many games are played during a given hour of a given day of the week.
- How weapons are used, damage-wise, per month.
- How weapons are used, frag-wise, per month.

Running this script requires the numpy, pandas, psycopg2, and matplotlib (of course!) Python packages. 
It also requires a XonStatDB instance loaded with data! To access this data, one must export the PGPASS and PGUSER
environment variables. 

    usage: xonotic_by_the_numbers.py [-h] [--year YEAR]

    optional arguments:
      -h, --help   show this help message and exit
      --year YEAR  Year to calculate
