# Bowser Walkthrough: Disp-S1

## 0. Environment Setup

This walkthrough assumes mamba (conda) is set up. If you don't have it installed:

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Clone the repository and create the environment:

```bash
git clone https://github.com/opera-adt/bowser.git && cd bowser
conda env create && conda activate bowser-env && python -m pip install "opera-utils[disp]>=0.22" dask
# Note: The extra pip installs are temporary and will be unnecessary soon
```

## 1. Download a Frame Subset Over New Orleans

This will require an Earthdata username/password, either as a `~/.netrc` file:

```
$ cat ~/.netrc
machine urs.earthdata.nasa.gov
        login your_username
        password your_password
```

or set as environment variables `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD`:

```bash
export EARTHDATA_USERNAME="your_username"
export EARTHDATA_PASSWORD="your_password"
```

Run the download and subset command using `opera-utils`:

```bash
mkdir data && cd data
opera-utils disp-s1-download --frame-id 44055 --wkt "POLYGON((-90.3919 29.8235,-89.7986 29.8235,-89.7986 30.1904,-90.3919 30.1904,-90.3919 29.8235))" --output-dir subsets-new-orleans
```

I found the WKT polygon by clicking around on [ASF search](https://search.asf.alaska.edu/#/?maxResults=250&polygon=POLYGON((-90.3919%2029.8235,-89.7986%2029.8235,-89.7986%2030.1904,-90.3919%2030.1904,-90.3919%2029.8235))&dataset=OPERA-S1&productTypes=DISP-S1&zoom=8.272&center=-90.008,29.439&resultsLoaded=true&granule=OPERA_L3_DISP-S1_IW_F44054_VV_20240415T000222Z_20241024T000222Z_v1.0_20250419T145258Z).

If you'd like to download less data, you can add a `--start-datetime` or `--end-datetime` parameter.

The download took about 15-20 minutes on my laptop on the east coast, or about 3-4 minutes on a JPL server.

The result should be:
- 209 files
- About 1400 x 1800 pixels each
- About 4 GB of disk space

## 2. Reformat the Data to Remove the "Moving Reference"

We'll create one 3D stack of data with all the layers in it that has taken care of the moving reference date. This lets us plot the continuous time series from the start without re-calculating it on every click.

```bash
opera-utils disp-s1-reformat --output-name new-orleans-F44055.zarr --input-files subsets-new-orleans/OPERA_L3_DISP-S1_IW_F44055*.nc
```

The reformatting takes approximately 80-90 seconds on my laptop.

## 3. Run Bowser

```bash
bowser run --workers 3 --stack-file new-orleans-F44055.zarr
```
