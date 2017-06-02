from __future__ import print_function
import os

class Provider(object):

    _unit_types_dict = {"COUNTRY": "CNTR", "NUTS": "NUTS"}
    _unit_types_list = _unit_types_dict.keys()

    def __init__(self, unit_type=None, year=None, resolution=None):

        self.unit_type = unit_type
        self.year = year
        self.resolution = resolution

        self.save_template = "{UNIT}_{YEAR}_{RES}_SH"

        self.home_path = "~/.shapefile"

        self._url = "http://ec.europa.eu/eurostat/cache/GISCO/geodatafiles/"

    def _download_template(self, **options):
        """
        Eurostat is inconsistent with its naming convention.
        """
        unit = options["UNIT"]
        year = str(options["YEAR"])
        res = options["RES"]

        file_template = "{UNIT}_{YEAR}_{RES}_SH.zip"

        if unit=="CNTR" and year=="2013":
            file_template = "{UNIT}-{RES}-{YEAR}-SH.zip"

        return file_template.format(**options)

    def download_shapefile(self, **options):
        import sys
        if sys.version[0]=="2":
            from urllib2 import urlopen
        else:
            from urllib.request import urlopen

        for key in options.keys():
            if key in self.__dict__.keys() and not options[key] is None:
                setattr(self, key, options[key])

        # This is the convention we'll use to save:
        # UNIT_YEAR_RES_SH
        settings = dict()
        settings["UNIT"] = self._unit_types_dict[self.unit_type]
        settings["YEAR"] = self.year
        settings["RES"] = self.resolution.upper().zfill(3)

        save_filename = self.save_template.format(**settings)

        # Unfortunately, there's a bit inconsistency in uploading 
        # The goal is permutate and find one that fits, and save correctly.
        download_filename = self._download_template(**settings)
        url = self._url + download_filename
        print(url)

        # Downloading a file
        u = urlopen(url)

        f = open(save_filename, 'wb')
        meta = u.info()
        if hasattr(meta, 'getheaders'):
            meta_length = meta.getheaders("Content-Length")
        else:
            meta_length = meta.get_all("Content-Length")
        file_size = int(meta_length[0])
        print("Downloading: %s Bytes: %s" % (download_filename, file_size))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            # Progress bar
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print(status, end="")

        f.close()

        # Unzip downloaded file
        import zipfile
        zip_ref = zipfile.ZipFile(save_filename, 'r')
        zip_ref.extractall(os.path.expanduser(self.home_path))
        zip_ref.close()

        # TODO:
        # When moving files make sure that are saved in consistent format

        # Delete tmp zip file
        os.remove(save_filename)

    def get_path(self, unit_type=None, year=None, resolution=None):
        if not unit_type is None:
            self.unit_type = unit_type

        if not year is None:
            self.year = str(year)

        if not resolution is None:
            self.resolution = resolution

        if not all((self.unit_type, self.year, self.resolution)):
            raise ValueError("One of the options is incorrect")

        self.unit_type = self.unit_type.upper()
        self.year = str(self.year)
        self.resolution = self.resolution.upper()

        # Filepath depends on options
        settings = dict()
        settings["UNIT"] = self._unit_types_dict[self.unit_type]
        settings["YEAR"] = str(self.year)
        settings["RES"] = self.resolution.zfill(3)

        setname = self.save_template.format(**settings)
        print(setname)

        # Expand path
        path = os.path.join(self.home_path, setname)
        path = os.path.expanduser(path)

        if not os.path.isdir(path):
            options = {"unit_type":unit_type, "year":year, "resolution":resolution}
            self.download_shapefile(**options)

        # Another inconsistency. Some dir have 'data', some 'Data' and some 'DATA' ... check for either and append
        for fname in os.listdir(path):
            if fname.upper()=="DATA":
                path = os.path.join(path, fname)
                break

        # Check that there was actually any `data` dir
        if path[-4:].upper()!="DATA":
            msg = "There is no `data` dir inside path: "+str(path)
            raise ValueError(msg)


        # And the final RG file
        filename_template = "{UNIT}_{T}_{RES}_{YEAR}.shp"
        path = os.path.join(path, filename_template)

        paths_dict = {"region": "RG", "boundary": "BN"}
        for name in paths_dict.keys():
            T = paths_dict[name]
            paths_dict[name] = path.format(T=T,**settings)

        return paths_dict

if __name__ == "__main__":
    p = Provider("nuts", 2010, "20m")
    print(p.get_path())


