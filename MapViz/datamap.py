import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import json
import matplotlib as mpl
import pylab as plt
from provider import Provider
from shapely.geometry import MultiPoint

class Map(object):
    def __init__(self):
        self.tight = False
        self.absolute = False

    def map_type(self, unit_type, year=None, resolution=None):
        self.unit_type = unit_type

        if year is None:
            year = "2013" #TODO: Should this be current year?

        if resolution is None:
            resolution = "20M"

        p = Provider(unit_type, year, resolution)
        self.path = p.get_path()

    def add_land(self, ax):
        return ax.add_feature(cfeature.LAND)

    def add_coastline(self, ax):
        return ax.add_feature(cfeature.COASTLINE)

    def plot_map(self, d_val):
        """
        Input is a map, with keys being 'iso_a2' countries.
        """
        countries = d_val.keys()
        values = d_val.values()
        _min, _max = min(values), max(values)
        if self.absolute: _min = 0

        reader = shapereader.Reader(self.path['region'])

        norm = mpl.colors.Normalize(vmin=_min, vmax=_max)
        cmap = plt.cm.RdYlBu_r

        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        actual_max = 0

        plot_bounds = MultiPoint()

        # Set up boundaries
        self.add_coastline(ax)
        self.add_land(ax)
        ID_NAME = Provider._unit_types_dict[self.unit_type.upper()]+"_ID"
        xyMP = lambda b: MultiPoint([b[:2], b[2:]])
        for idx, record in enumerate(reader.records()):
            attr = record.attributes
            cntr_id = attr[ID_NAME]

            if not cntr_id in countries: continue
            if self.tight:
                bound = xyMP(record.geometry.bounds)
                plot_bounds = plot_bounds.union(bound).bounds
                plot_bounds = xyMP(plot_bounds)

            val = d_val[cntr_id]
            val = cmap(norm(val))
            ax.add_geometries([record.geometry],
                    ccrs.PlateCarree(),
                   facecolor=val,
                    alpha=0.8)

        if self.tight:
            bound = plot_bounds.bounds
            ax.set_ylim((bound[1], bound[3]))
            ax.set_xlim((bound[0], bound[2]))
        return ax

if __name__ == "__main__":
    with open('data.json','r') as f:
        data = json.loads(f.read())
    unit_type = data['map_type']
    year = data['year']
    resolution = data['resolution']
    data_val = data['data']

    map_data = Map()
    map_data.tight = True
    map_data.map_type(unit_type)
    ax = map_data.plot_map(data_val)
    plt.tight_layout()
    plt.show()
