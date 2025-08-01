# QuantPunc

[![PyPI](https://img.shields.io/pypi/v/quantpunc.svg?color=green)](https://pypi.org/project/quantpunc)
[![Python Version](https://img.shields.io/pypi/pyversions/quantpunc.svg?color=green)](https://python.org)
[![License BSD-3](https://img.shields.io/pypi/l/quantpunc.svg?color=green)](https://github.com/tehahn/quantpunc/blob/main/LICENSE)

QuantPunc is a Napari plugin for puncta analysis and quantification in 2D microscopy images. A brief overview of QuantPunc's workflow can be found below. 

A comprehensive guide to QuantPunc can be found at https://tehahn.github.io/quantpunc/.

QuantPunc is currently in beta. Please report any problems to the [issues page].

## Features
1. Automated puncta labeling and counting
2. Watershed segmentation
3. Colocalization analysis 
4. Exportable counts and stats

## Installation
You can install `quantpunc` via Napari's plugin manager:

1. Click on "Plugins" in the toolbar.
2. Click on "Install/Uninstall Plugins..." in the context menu.
3. Type "quantpunc" in the searchbar.
4. Click install.

You can also install `quantpunc` via [pip]:

    pip install quantpunc

## Puncta Quantification and Workflow
Here’s an ideal, high-level workflow for puncta segmentation and quantification. This is the recommended way of using QuantPunc. However, QuantPunc’s widgets are modularly designed so that they can be used as standalone tools. If this is your first time working with these tools, you can access the more in-depth guide mentioned above [here].

### 1. Preprocessing (optional but recommended)
QuantPunc uses wavelet denoising and adaptive histogram equalization to enhance edge information and contrast in your image. If you feel that your image has sufficient contrast and minimal noise, feel free to skip this step.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/preprocessing_example.gif" 
alt="" 
width="1000"
style="border-radius: 10px; max-width: 100%;">

### 2. Automated labeling
There are two automated labeling methods. One of them uses [skimage’s blob detection] algorithms and the other uses a random forest classifier with features inspired by [ilastik]. You also have the option to only segment puncta within ROIs. You can provide your own ROIs or create them using a labels layer in Napari.

### Random forest classifier (RFC)
You can use Napari to create annotations or provide your own. After annotating your puncta and specifying your integer labels, you can then train the RFC. Click on *Label puncta* to segment your puncta.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/rfc_example.gif" 
alt="" 
width="1000"
style="border-radius: 10px; max-width: 100%;">

### Skimage blob detection
Select your favorite blob detection algorithm from the *Method* dropdown menu. After parameterizing it, click on *Label puncta*.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/skimage_blob_example.gif" 
alt="" 
width="1000"
style="border-radius: 10px; max-width: 100%;">

### 3. Manual labeling
You can remove any puncta labels you don’t want from automated segmentation by using Napari’s layer control toolbar. You also have the option to do a full manual segmentation using a labels layer and quantify your annotations after.

### 4. Watershed segmentation (optional)
If your puncta exhibits lots of clumping, you can use the watershed tool to perform instance segmentation on your puncta labels layer. You can choose either to use a distance transform or Sobel filter to generate the elevation map.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/watershed_example.gif"
alt="" 
width="1000"
style="border-radius: 10px; max-width: 100%;">

### Seed point generation
You can either provide your own seed points or generate them using skimage’s blob counting algorithms with a low min and max sigma.

### 5. Puncta counting
After you have a segmentation you’re happy with, select the image you want to quantify and click *Count puncta*. Make sure that your puncta labels layer is named after the image you’re quantifying with “_puncta” as its suffix, e.g., “your_img_puncta”.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/counts_example.gif" 
alt="" 
height="750"
style="border-radius: 10px; max-width: 100%;">

### 6. Colocalization analysis (optional)
Colocalization is measured using the intersection over union (IoU), aka the Jaccard Index. Select two puncta labels layers and click on *Compute IoU*.

<img 
src="https://raw.githubusercontent.com/tehahn/quantpunc/refs/heads/main/demo_imgs/coloc_example.gif" 
alt="" 
height="750"
style="border-radius: 10px; max-width: 100%;">

### 7. Displaying stats and saving
Click on any of the tabs in the table widget to view different summaries of the puncta you’ve quantified. To export the tables as a csv for the layer you’ve selected, click on *Save selected data*. If you want to save the data for all the images you’ve quantified click on *Save all data*.

## Contributing
Contributions are very, very welcome. QuantPunc allows you to implement your own automated puncta labeler. Look in the Github repo at [abstract_puncta_labeler] to see what methods need to be implemented and [default_puncta_labelers] for examples. If you're interested in making it available to everyone else or have any other improvements, feel free to send a pull request!

## License
Distributed under the terms of the [BSD-3] license,
QuantPunc is free and open source software

## Issues
QuantPunc is still in beta, so bugs are to be expected. Please report any problems to the [issues page].


[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[pip]: https://pypi.org/project/pip/

[ilastik]: https://www.ilastik.org/
[skimage’s blob detection]: https://scikit-image.org/docs/0.25.x/auto_examples/features_detection/plot_blob.html

[abstract_puncta_labeler]: https://github.com/tehahn/quantpunc/blob/main/src/quantpunc/quantification/abstract_puncta_labeler.py
[default_puncta_labelers]: https://github.com/tehahn/quantpunc/blob/main/src/quantpunc/quantification/default_puncta_labelers.py

[Napari hub]: https://napari-hub.org/plugins/quantpunc.html
[here]: https://tehahn.github.io/quantpunc/
[issues page]: https://github.com/tehahn/quantpunc/issues