import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import matplotlib as mpl
import pylab as plt
from provider import Provider
from shapely.geometry import MultiPoint

class Map(object):
    """Creates map chart with varied levels of granuality.

    Main method is `plot_map` which takes dict `region`:`value`
    and produces map chart. In first instance user needs to
    define granuality of the data ('NUTS' is recommended).

    If shapefile data is not stored locally `Provider` class is
    used to download from EuroStats webpage and save in home dir.

    Class depends heavily on `cartopy` module.
    """

    def __init__(self):
        self.tight_boundary = False
        self.absolute = False

        self.cmap = plt.cm.RdYlBu_r
        self.xyMP = lambda b: MultiPoint([b[:2], b[2:]])

    def map_type(self, unit_type, year=None, resolution="20M"):
        self.unit_type = unit_type

        if year is None:
            year = "2013" #TODO: Should this be current year?

        p = Provider(unit_type, year, resolution)
        self.path = p.get_path()

    def add_land(self, ax):
        return ax.add_feature(cfeature.LAND)

    def add_coastline(self, ax):
        return ax.add_feature(cfeature.COASTLINE)

    def plot_map(self, d_val):
        """Plots map which regions are coloured with value intensities.

        Args:
            d_val (dict): Data to plot with 'regions` as keys.

        Returns:
            ax: Matplotlib axis containg map.
        """
        countries = d_val.keys()
        values = d_val.values()
        _min, _max = min(values), max(values)
        if self.absolute: _min = 0

        print(self.path['region'])
        reader = shapereader.Reader(self.path['region'])

        norm = mpl.colors.Normalize(vmin=_min, vmax=_max)

        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        actual_max = 0

        plot_bounds = MultiPoint()

        # Set up boundaries
        self.add_coastline(ax)
        self.add_land(ax)

        # Key depends on unit type, i.e. {UNIT}_ID
        ID_NAME = Provider._unit_types_dict[self.unit_type.upper()]+"_ID"

        for idx, record in enumerate(reader.records()):
            attr = record.attributes
            cntr_id = attr[ID_NAME]

            if not cntr_id in countries: continue
            if self.tight_boundary:
                bound = self.xyMP(record.geometry.bounds)
                plot_bounds = plot_bounds.union(bound).bounds
                plot_bounds = self.xyMP(plot_bounds)

            val = d_val[cntr_id]
            val = self.cmap(norm(val))
            ax.add_geometries([record.geometry],
                    ccrs.PlateCarree(),
                    facecolor=val)

        if self.tight_boundary:
            bound = plot_bounds.bounds
            ax.set_ylim((bound[1], bound[3]))
            ax.set_xlim((bound[0], bound[2]))

        return ax

if __name__ == "__main__":
    import json
    with open('data.json','r') as f:
        data = json.loads(f.read())
    unit_type = data['map_type']
    year = data['year']
    resolution = data['resolution']
    data_val = data['data']

    map_data = Map()
    map_data.tight_boundary = True
    map_data.map_type(unit_type, year, resolution)
    ax = map_data.plot_map(data_val)
    plt.tight_layout()
    plt.show()
