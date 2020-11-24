#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thunderstorm Detection and Tracking - DATing
============================================

This example shows how to use the thunderstorm DATing module. The example is based on
MeteoSwiss radar data and uses the Cartesian composite of maximum reflectivity on a
1 km grid. All default values are tuned to this grid, but can be modified.
The first section demonstrates thunderstorm cell detection and how to plot contours.
The second section demonstrates detection and tracking in combination,
as well as how to plot the resulting tracks.

@author: mfeldman
"""
################################################################################
# Import all required functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys
from datetime import datetime
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

from pysteps import io, rcparams
from pysteps.feature import tstorm as tstorm_detect
from pysteps.tracking import tdating as tstorm_dating
from pysteps.utils import to_reflectivity
from pysteps.visualization import plot_precip_field, plot_track, plot_cart_contour

################################################################################
# Read the radar input images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# A series of 20 files containing Swiss Cartesian gridded rainrate are imported. Since the
# algorithm is tuned to Swiss max-reflectivity data, the rainrate is transformed to
# reflectivity.

date = datetime.strptime("201607112100", "%Y%m%d%H%M")
data_source = rcparams.data_sources["mch"]

root_path = data_source["root_path"]
path_fmt = data_source["path_fmt"]
fn_pattern = data_source["fn_pattern"]
fn_ext = data_source["fn_ext"]
importer_name = data_source["importer"]
importer_kwargs = data_source["importer_kwargs"]
timestep = data_source["timestep"]

###############################################################################
# Load the data from the archive
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fns = io.archive.find_by_date(
    date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_next_files=20
)

importer = io.get_method(importer_name, "importer")
R, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)
Z, metadata = to_reflectivity(R, metadata)
timelist = metadata["timestamps"]

pprint(metadata)

###############################################################################
# Example of thunderstorm identification in a single timestep.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The function tstorm_detect.detection requires a 2-D input image, all further inputs are
# optional.


input_image = Z[2, :, :].copy()
time = timelist[2]
cells_id, labels = tstorm_detect.detection(
    input_image,
    dyn_thresh=True,
    time=time,
)

###############################################################################
# Example of thunderstorm tracking over a timeseries.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The tstorm-dating function requires the entire pre-loaded time series.
# The first two timesteps are required to initialize the
# flow prediction and are not used to compute tracks.

track_list, cell_list, label_list = tstorm_dating.dating(
    input_video=Z,
    timelist=timelist,
    dyn_thresh=False,
)

###############################################################################
# Plotting the results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Plot precipitation field
plot_precip_field(Z[2, :, :], geodata=metadata, units=metadata["unit"])

# Add the identified cells
plot_cart_contour(cells_id.cont, geodata=metadata)

# Filter the tracks to only contain cells existing in this timestep

IDs=cells_id.ID.values
track_filt=[]
for track in track_list:
    if np.unique(track.ID) in IDs: track_filt.append(track)

# Add their tracks
plot_track(track_filt, geodata=metadata)
plt.show()

#%%
################################################################################
# Example with US MRMS data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This example applies the same algorithm to US MRMS data. As previously, the rainrate
# is transformed to reflectivity.

date = datetime.strptime("201906100000", "%Y%m%d%H%M")
data_source = rcparams.data_sources["mrms"]

root_path = data_source["root_path"]
path_fmt = data_source["path_fmt"]
fn_pattern = data_source["fn_pattern"]
fn_ext = data_source["fn_ext"]
importer_name = data_source["importer"]
importer_kwargs = data_source["importer_kwargs"]
timestep = data_source["timestep"]

###############################################################################
# Load the data from the archive
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fns = io.archive.find_by_date(
    date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_next_files=20
)

importer = io.get_method(importer_name, "importer")
R, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)
Z, metadata = to_reflectivity(R, metadata)
timelist = metadata["timestamps"]

pprint(metadata)

###############################################################################
# Example of thunderstorm identification in a single timestep.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The function tstorm_detect.detection requires a 2-D input image, all further inputs are
# optional.

input_image = Z[2, :, :].copy()
time = timelist[2]
cells_id, labels = tstorm_detect.detection(
    input_image,
    dyn_thresh=False,
    minsize=4,
    time=time,
)

###############################################################################
# Example of thunderstorm tracking over a timeseries.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The tstorm-dating function requires the entire pre-loaded time series.
# The first two timesteps are required to initialize the
# flow prediction and are not used to compute tracks.

track_list, cell_list, label_list = tstorm_dating.dating(
    input_video=Z,
    timelist=timelist,
    dyn_thresh=False,
    minsize=4
)

###############################################################################
# Plotting the results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Plot precipitation field
plot_precip_field(Z[2, :, :], geodata=metadata, units=metadata["unit"])

# Add the identified cells
plot_cart_contour(cells_id.cont, geodata=metadata)

# Filter the tracks to only contain cells existing in this timestep

IDs=cells_id.ID.values
track_filt=[]
for track in track_list:
    if np.unique(track.ID) in IDs: track_filt.append(track)

# Add their tracks
plot_track(track_filt, geodata=metadata)
plt.show()