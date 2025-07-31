﻿############################################################################
#                               Libraries                                  #
############################################################################
import numpy as np

import os

from pathlib import Path

import itertools

from astropy.visualization import (
    ImageNormalize,
    ZScaleInterval,
    simple_norm,
)
from astropy.table import Table
from astropy.stats import sigma_clip as sigma_clipping
from astropy.stats import sigma_clipped_stats
from astropy.modeling import fitting
from astropy.time import Time
from astropy.timeseries import aggregate_downsample
import astropy.units as u
from astropy.timeseries import TimeSeries
from astropy import wcs
from astropy.coordinates import SkyCoord

from photutils.aperture import CircularAperture, CircularAnnulus
from photutils.psf import EPSFStars, ImagePSF
from photutils.utils import ImageDepth

from scipy.spatial import KDTree

from itertools import cycle

from .. import checks, style, terminal_output, calibration_parameters
from .. import utilities as base_utilities

import matplotlib.colors as mcol
import matplotlib.cm as cm
from matplotlib import rcParams, gridspec
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
# from matplotlib.patches import Circle

plt.switch_backend('Agg')


# plt.switch_backend('TkAgg')

############################################################################
#                           Routines & definitions                         #
############################################################################


def compare_images(
        output_dir: str, original_image: np.ndarray,
        comparison_image: np.ndarray, file_type: str = 'pdf') -> None:
    """
    Plot two images for comparison

    Parameters
    ----------
    output_dir
        Output directory

    original_image
        Original image data

    comparison_image
        Comparison image data

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Prepare plot
    plt.figure(figsize=(12, 7))
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2, sharex=ax1, sharey=ax1)

    #   Original image: normalize and plot
    norm = simple_norm(original_image.data, 'log', percent=99.)
    ax1.imshow(original_image.data, norm=norm, cmap='gray')
    ax1.set_axis_off()
    ax1.set_title('Original image')

    #   Comparison image: normalize and plot
    norm = simple_norm(comparison_image, 'log', percent=99.)
    ax2.imshow(comparison_image, norm=norm, cmap='gray')
    ax2.set_axis_off()
    ax2.set_title('Downloaded image')

    #   Save the plot
    plt.savefig(
        f'{output_dir}/img_comparison.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()

def starmap(
        output_dir: str, image: np.ndarray, filter_: str, tbl: Table,
        tbl_2: Table = None, label: str = 'Identified stars',
        label_2: str = 'Identified stars (set 2)', rts: str | None = None,
        mode: str | None = None, name_object: str | None = None,
        wcs_image: wcs.WCS = None, use_wcs_projection: bool = True,
        terminal_logger: terminal_output.TerminalLog | None = None,
        file_type: str = 'pdf', indent: int = 2) -> None:
    """
    Plot star maps  -> overlays of the determined star positions on FITS
                    -> supports different versions

    Parameters
    ----------
    output_dir
        Output directory

    image
        The image data

    filter_
        Filter identifier

    tbl
        Astropy table with data of the objects

    tbl_2
        Second astropy table with data of special objects
        Default is ``None``

    label
        Identifier for the objects in `tbl`
        Default is ``Identified stars``

    label_2
        Identifier for the objects in `tbl_2`
        Default is ``Identified stars (set 2)``

    rts
        Expression characterizing the plot
        Default is ``None``

    mode
        String used to switch between different plot modes
        Default is ``None``

    name_object
        Name of the object
        Default is ``None``

    wcs_image
        WCS information
        Default is ``None``

    use_wcs_projection
        If ``True`` the starmap will be plotted with sky coordinates instead
        of pixel coordinates
        Default is ``True``.

    terminal_logger
        Logger object. If provided, the terminal output will be directed
        to this object.
        Default is ``None``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.

    indent
        Indentation for the console output lines
        Default is ``2``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'starmaps'),
    )

    if rts is not None:
        if terminal_logger is not None:
            terminal_logger.add_to_cache(
                f"Plot {filter_} band image with stars overlaid ({rts})",
                style_name='NORMAL',
                indent=indent,
            )
        else:
            terminal_output.print_to_terminal(
                f"Plot {filter_} band image with stars overlaid ({rts})",
                style_name='NORMAL',
                indent=indent,
            )

    #   Check if column with X and Y coordinates are available for table 1
    if 'x' in tbl.colnames:
        x_column = 'x'
        y_column = 'y'
    elif 'xcentroid' in tbl.colnames:
        x_column = 'xcentroid'
        y_column = 'ycentroid'
    elif 'xfit' in tbl.colnames:
        x_column = 'xfit'
        y_column = 'yfit'
    elif 'x_fit' in tbl.colnames:
        x_column = 'x_fit'
        y_column = 'y_fit'
    else:
        raise RuntimeError(
            f"{style.Bcolors.FAIL} \nNo valid X and Y column found for "
            f"table 1. {style.Bcolors.ENDC}"
        )
    #   Check if column with X and Y coordinates are available for table 2
    if tbl_2 is not None:
        if 'x' in tbl_2.colnames:
            x_column_2 = 'x'
            y_column_2 = 'y'
        elif 'xcentroid' in tbl_2.colnames:
            x_column_2 = 'xcentroid'
            y_column_2 = 'ycentroid'
        elif 'xfit' in tbl_2.colnames:
            x_column_2 = 'xfit'
            y_column_2 = 'yfit'
        else:
            raise RuntimeError(
                f"{style.Bcolors.FAIL} \nNo valid X and Y column found for "
                f"table 2. {style.Bcolors.ENDC}"
            )

    #   Set layout
    fig = plt.figure(figsize=(20, 9))

    if not use_wcs_projection:
        ax = fig.add_subplot()
    else:
        if wcs_image is not None:
            ax = plt.subplot(projection=wcs_image)
        else:
            terminal_output.print_to_terminal(
                f"Sky projection for master plot not possible, since no WCS "
                f"was provided. Use Pixel coordinates instead.",
                style_name='WARNING',
                indent=indent,
            )
            ax = fig.add_subplot()


    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title of the complete plot
    if rts is None and name_object is None:
        sub_title = f'Star map ({filter_} filter)'
    elif rts is None:
        sub_title = f'{name_object} - {filter_} filter'
    elif name_object is None:
        sub_title = f'{filter_} filter, {rts}'
    else:
        sub_title = f'{name_object} - {filter_} filter, {rts}'

    fig.suptitle(sub_title, fontsize=17)

    #   Set up normalization for the image
    norm = ImageNormalize(image, interval=ZScaleInterval(contrast=0.15, ))

    #   Display the actual image
    ax.imshow(
        image,
        cmap='PuBu',
        origin='lower',
        norm=norm,
        interpolation='nearest',
    )

    #   Plot apertures
    ax.scatter(
        tbl[x_column],
        tbl[y_column],
        s=40,
        facecolors=(0.5, 0., 0.5, 0.2),
        edgecolors=(0.5, 0., 0.5, 0.7),
        lw=0.9,
        label=label,
    )
    if tbl_2 is not None:
        ax.scatter(
            tbl_2[x_column_2],
            tbl_2[y_column_2],
            s=40,
            facecolors=(0., 0.7, 0.35, 0.2),
            edgecolors=(0., 0.7, 0.35, 0.7),
            lw=0.9,
            label=label_2,
        )

    #   Set plot limits
    ax.set_xlim(0, image.shape[1] - 1)
    ax.set_ylim(0, image.shape[0] - 1)

    # Plot labels next to the apertures
    if isinstance(tbl[x_column], u.quantity.Quantity):
        x = tbl[x_column].value
        y = tbl[y_column].value
    else:
        x = tbl[x_column]
        y = tbl[y_column]
    if mode == 'mags':
        try:
            magnitudes = tbl['mag_cali_trans']
        except KeyError:
            magnitudes = tbl['mag_cali']
        for i in range(0, len(x)):
            ax.text(
                x[i] + 11,
                y[i] + 8,
                f" {magnitudes[i]:.1f}",
                fontdict=style.font,
                color='purple',
            )
    elif mode == 'list':
        for i in range(0, len(x)):
            ax.text(
                x[i],
                y[i],
                f" {i}",
                fontdict=style.font,
                color='purple',
            )
    else:
        for i in range(0, len(x)):
            ax.text(
                x[i] + 11,
                y[i] + 8,
                f" {tbl['id'][i]}",
                fontdict=style.font,
                color='purple',
            )

    #   Define the ticks
    ax.tick_params(
        axis='both',
        which='both',
        # top=True,
        # right=True,
        direction='in',
    )
    ax.minorticks_on()

    #   Set labels
    if wcs_image is not None:
        ax.set_xlabel("Right ascension", fontsize=16)
        ax.set_ylabel("Declination", fontsize=16)
    else:
        ax.set_xlabel("[pixel]", fontsize=16)
        ax.set_ylabel("[pixel]", fontsize=16)

    #   Enable grid for WCS
    # if wcs is not None:
    ax.grid(True, color='white', linestyle='--')

    #   Plot legend
    ax.legend(
        bbox_to_anchor=(0., 1.02, 1.0, 0.102),
        loc=3,
        ncol=2,
        mode='expand',
        borderaxespad=0.,
    )

    #   Write the plot to disk
    if rts is None:
        plt.savefig(
            f'{output_dir}/starmaps/starmap_{filter_}.{file_type}',
            bbox_inches='tight',
            format=file_type,
        )
    else:
        replace_dict = {',': '', '.': '', '\\': '', '[': '', '&': '', ' ': '_',
                        ':': '', ']': '', '{': '', '}': ''}
        for key, value in replace_dict.items():
            rts = rts.replace(key, value)
        rts = rts.lower()
        plt.savefig(
            f"{output_dir}/starmaps/starmap_{filter_}_{rts}.{file_type}",
            bbox_inches='tight',
            format=file_type,
        )
    # plt.show()
    plt.close()


def plot_apertures(
        output_dir: str, image: base_utilities.Image,
        aperture: CircularAperture, annulus_aperture: CircularAnnulus,
        filename_string: str, file_type: str = 'pdf') -> None:
    """
    Plot the apertures used for extracting the stellar fluxes
           (star map plot for aperture photometry)

    Parameters
    ----------
    output_dir
        Output directory

    image
        2D Image data

    aperture
        Apertures used to extract the stellar flux

    annulus_aperture
        Apertures used to extract the background flux

    filename_string
        String characterizing the output file

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'aperture'),
    )

    #   Make plot
    plt.figure(figsize=(20, 9))

    #   Normalize the image
    norm = ImageNormalize(image, interval=ZScaleInterval())

    #   Plot the image
    plt.imshow(
        image,
        cmap='viridis',
        origin='lower',
        norm=norm,
        interpolation='nearest',
    )

    #   Plot stellar apertures
    ap_patches = aperture.plot(
        color='lightcyan',
        lw=0.2,
        label='Object aperture',
    )

    #   Plot background apertures
    ann_patches = annulus_aperture.plot(
        color='darkred',
        lw=0.2,
        label='Background annulus',
    )

    #
    handles = (ap_patches[0], ann_patches[0])

    #   Set labels
    plt.xlabel("[pixel]", fontsize=16)
    plt.ylabel("[pixel]", fontsize=16)

    #   Plot legend
    plt.legend(
        loc=(0.17, 0.05),
        facecolor='#458989',
        labelcolor='white',
        handles=handles,
        prop={'weight': 'bold', 'size': 9},
    )

    #   Save figure
    plt.savefig(
        f'{output_dir}/aperture/aperture_{filename_string}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )

    #   Set labels
    plt.xlabel("[pixel]", fontsize=16)
    plt.ylabel("[pixel]", fontsize=16)

    plt.close()


def plot_cutouts(output_dir: str, stars: EPSFStars, identifier: str,
                 terminal_logger: terminal_output.TerminalLog | None = None,
                 max_plot_stars: int = 25, name_object: str | None = None,
                 file_type: str = 'pdf', indent: int = 2) -> None:
    """
    Plot the cutouts of the stars used to estimate the ePSF

    Parameters
    ----------
    output_dir
        Output directory

    stars
        Numpy array with cutouts of the ePSF stars

    identifier
        String characterizing the plot

    terminal_logger
        Logger object. If provided, the terminal output will be directed
        to this object.
        Default is ``None``.

    max_plot_stars
        Maximum number of cutouts to plot
        Default is ``25``.

    name_object
        Name of the object
        Default is ``None``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.

    indent
        Indentation for the console output lines.
        Default is ``2``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'cutouts'),
    )

    #   Set number of cutouts
    if len(stars) > max_plot_stars:
        n_cutouts = max_plot_stars
    else:
        n_cutouts = len(stars)

    if terminal_logger is not None:
        terminal_logger.add_to_cache(
            f"Plot ePSF cutouts ({identifier})",
            indent=indent,
        )
    else:
        terminal_output.print_to_terminal(
            f"Plot ePSF cutouts ({identifier})",
            indent=indent,
        )

    #   Plot the first cutouts (default: 25)
    #   Set number of rows and columns
    n_rows = 5
    n_columns = 5

    #   Prepare plot
    fig, ax = plt.subplots(nrows=n_rows, ncols=n_columns, figsize=(20, 15),
                           squeeze=True)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                        wspace=None, hspace=0.25)

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title of the complete plot
    if name_object is None:
        sub_title = f'Cutouts of the {n_cutouts} faintest stars ({identifier})'
    else:
        sub_title = f'Cutouts of the {n_cutouts} faintest stars ({identifier}) - {name_object}'
    fig.suptitle(sub_title, fontsize=17)

    ax = ax.ravel()  # flatten the image?

    #   Loop over the cutouts (default: 25)
    for i in range(n_cutouts):
        # Remove bad pixels that would spoil the image normalization
        data_image = np.where(stars[i].data <= 0, 1E-7, stars[i].data)
        # Set up normalization for the image
        norm = simple_norm(data_image, 'log', percent=99.)
        # Plot individual cutouts
        ax[i].set_xlabel("Pixel")
        ax[i].set_ylabel("Pixel")
        ax[i].imshow(data_image, norm=norm, origin='lower', cmap='viridis')
    plt.savefig(
        f'{output_dir}/cutouts/cutouts_{identifier}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    # plt.show()
    plt.close()


def plot_epsf(
        output_dir: str, epsf: dict[str, list[ImagePSF]],
        name_object: str | None = None, id_image: str = '',
        terminal_logger: terminal_output.TerminalLog | None = None,
        file_type: str = 'pdf', indent: int = 1) -> None:
    """

    Plot the ePSF image of all filters

    Parameters
    ----------
    output_dir
        Output directory

    epsf
        PSF object, usually constructed by epsf_builder

    name_object
        Name of the object
        Default is ``None``.

    id_image
        ID of the image that should be added to the file name.
        Default is ````.

    terminal_logger
        Logger object. If provided, the terminal output will be directed
        to this object.
        Default is ``None``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.


    indent
        Indentation for the console output lines
        Default is ``1``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'epsfs'),
    )

    if terminal_logger is not None:
        terminal_logger.add_to_cache("Plot ePSF image", indent=indent)
    else:
        terminal_output.print_to_terminal("Plot ePSF image", indent=indent)

    #   Set font size
    rcParams['font.size'] = 13

    #   Set up plot
    n_plots = len(epsf)
    if n_plots == 1:
        fig = plt.figure(figsize=(6, 5))
    elif n_plots == 2:
        fig = plt.figure(figsize=(13, 5))
    else:
        fig = plt.figure(figsize=(20, 15))

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title of the complete plot
    if name_object is None:
        fig.suptitle('ePSF', fontsize=17)
    else:
        fig.suptitle(f'ePSF ({name_object})', fontsize=17)

    #   Plot individual subplots
    for i, (filter_, eps_s) in enumerate(epsf.items()):
        for eps in eps_s:
            if eps is not None:
                #   Remove bad pixels that would spoil the image normalization
                epsf_clean = np.where(eps.data <= 0, 1E-7, eps.data)
                #   Set up normalization for the image
                norm = simple_norm(epsf_clean, 'log', percent=99.)

                #   Make the subplots
                if n_plots == 1:
                    ax = fig.add_subplot(1, 1, i + 1)
                elif n_plots == 2:
                    ax = fig.add_subplot(1, 2, i + 1)
                else:
                    ax = fig.add_subplot(n_plots, n_plots, i + 1)

                #   Plot the image
                im1 = ax.imshow(epsf_clean, norm=norm, origin='lower',
                                cmap='viridis')

                #   Set title of subplot
                ax.set_title(filter_)

                #   Set labels
                ax.set_xlabel("Pixel")
                ax.set_ylabel("Pixel")

                #   Set color bar
                fig.colorbar(im1, ax=ax)

    if n_plots >= 2:
        plt.savefig(
            f'{output_dir}/epsfs/epsfs_multiple_filter{id_image}.{file_type}',
            bbox_inches='tight',
            format=file_type,
        )
    else:
        plt.savefig(
            f'{output_dir}/epsfs/epsf{id_image}.{file_type}',
            bbox_inches='tight',
            format=file_type,
        )
    # plt.show()
    plt.close()


def plot_residual(
        image_orig: dict[str, np.ndarray],
        residual_image: dict[str, np.ndarray],
        output_dir: str, name_object: str | None = None,
        terminal_logger: terminal_output.TerminalLog | None = None,
        file_type: str = 'pdf', indent: int = 1) -> None:
    """
    Plot the original and the residual ePSF image

    Parameters
    ----------
    image_orig
        Original image data

    residual_image
        Residual image data

    output_dir
        Output directory

    name_object
        Name of the object
        Default is ``None``.

    terminal_logger
        Logger object. If provided, the terminal output will be directed
        to this object.
        Default is ``None``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.

    indent
        Indentation for the console output lines
        Default is ``1``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'residual'),
    )

    if terminal_logger is not None:
        terminal_logger.add_to_cache(
            "Plot original and the residual image",
            indent=indent,
        )
    else:
        terminal_output.print_to_terminal(
            "Plot original and the residual image",
            indent=indent,
        )

    #   Set font size
    rcParams['font.size'] = 13

    #   Set up plot
    n_plots = len(image_orig)
    if n_plots == 1:
        fig = plt.figure(figsize=(10, 10))
    elif n_plots == 2:
        fig = plt.figure(figsize=(20, 10))
    else:
        fig = plt.figure(figsize=(20, 20))

    plt.subplots_adjust(
        left=None,
        bottom=None,
        right=None,
        top=None,
        wspace=None,
        hspace=0.25,
    )

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title of the complete plot
    if name_object is not None:
        fig.suptitle(f'{name_object}', fontsize=17)

    i = 1
    filter_ = None
    for filter_, image in image_orig.items():
        #   Plot original image
        #   Set up normalization for the image
        norm = ImageNormalize(image, interval=ZScaleInterval())

        if n_plots == 1:
            ax = fig.add_subplot(2, 1, i)
        elif n_plots == 2:
            ax = fig.add_subplot(2, 2, i)
        else:
            ax = fig.add_subplot(n_plots, 2, i)

        #   Plot image
        im1 = ax.imshow(
            image,
            norm=norm,
            cmap='viridis',
            aspect=1,
            interpolation='nearest',
            origin='lower',
        )

        #   Set title of subplot
        ax.set_title(f'Original Image ({filter_})')

        #   Set labels
        ax.set_xlabel("Pixel")
        ax.set_ylabel("Pixel")

        #   Set color bar
        fig.colorbar(im1, ax=ax)

        i += 1

        #   Plot residual image
        #   Set up normalization for the image
        norm = ImageNormalize(residual_image[filter_],
                              interval=ZScaleInterval())

        if n_plots == 1:
            ax = fig.add_subplot(2, 1, i)
        elif n_plots == 2:
            ax = fig.add_subplot(2, 2, i)
        else:
            ax = fig.add_subplot(n_plots, 2, i)

        #   Plot image
        im2 = ax.imshow(
            residual_image[filter_],
            norm=norm,
            cmap='viridis',
            aspect=1,
            interpolation='nearest',
            origin='lower',
        )

        #   Set title of subplot
        ax.set_title(f'Residual Image ({filter_})')

        #   Set labels
        ax.set_xlabel("Pixel")
        ax.set_ylabel("Pixel")

        #   Set color bar
        fig.colorbar(im2, ax=ax)

        i += 1

    #   Write the plot to disk
    if n_plots == 1:
        plt.savefig(
            f'{output_dir}/residual/residual_images_{filter_}.{file_type}'.replace(":", "")
            .replace(",", "").replace(" ", "_"),
            bbox_inches='tight',
            format=file_type,
        )
    else:
        plt.savefig(
            f'{output_dir}/residual/residual_images.{file_type}',
            bbox_inches='tight',
            format=file_type
        )
    # plt.show()
    plt.close()


def light_curve_jd(
        ts: TimeSeries, data_column: str, err_column: str, output_dir: str,
        error_bars: bool = True, name_object: str | None = None,
        file_name_suffix: str = '', subdirectory: str = '',
        file_type: str = 'pdf', own_scaling: bool = True,
        invert_axis: bool = True) -> None:
    """
    Plot the light curve over Julian Date

    Parameters
    ----------
    ts
        Time series

    data_column
        Filter

    err_column
        Name of the error column

    output_dir
        Output directory

    error_bars
        If True error bars will be plotted.
        Default is ``False``.

    name_object
        Name of the object
        Default is ``None``.

    file_name_suffix
        Suffix to add to the file name
        Default is ``''``

    subdirectory
        Name of the subdirectory in which to save the plots

    file_type
        Type of plot file to be created
        Default is ``pdf``.

    own_scaling
        If ``True``, the Y-axis is subject to the normal mathplotlib
        autoscaling.
        Default is ``True``.

    invert_axis
        If ``True``, the Y-axis will be inverted.
        Default is ``True``.
    """
    #   Check output directories
    if subdirectory != '':
        checks.check_output_directories(
            output_dir,
            f'{output_dir}/lightcurve{subdirectory}',
        )
    else:
        checks.check_output_directories(
            output_dir,
            os.path.join(output_dir, 'lightcurve'),
        )

    #   Make plot
    fig = plt.figure(figsize=(20, 9))

    #   Plot grid
    plt.grid(True, color='lightgray', linestyle='--')

    #   Set tick size
    plt.tick_params(axis='x', labelsize=15)
    plt.tick_params(axis='y', labelsize=15)

    #   Set title
    if name_object is None:
        fig.suptitle(f'Light curve', fontsize=30)
    else:
        fig.suptitle(f'Light curve - {name_object}', fontsize=30)

    #   Plot data with or without error bars
    if not error_bars:
        plt.plot(ts.time.jd, ts[data_column], 'k.', markersize=3)
    else:
        plt.errorbar(
            ts.time.jd,
            np.array(ts[data_column]),
            yerr=np.array(ts[err_column]),
            marker='.',
            markersize=4,
            linestyle='none',
            capsize=2,
            ecolor='dodgerblue',
            color='darkred',
        )

    #   Get median of the data
    median_data = np.median(ts[data_column].value)
    min_data = np.min(ts[data_column].value)
    max_data = np.max(ts[data_column].value)

    #   Invert y-axis
    if invert_axis & (median_data > 1.5 or median_data < 0.5):
        plt.gca().invert_yaxis()

    #   Set plot limits
    y_err = ts[err_column].value
    y_err_sigma = sigma_clipping(y_err, sigma=1.5)
    max_err = np.max(y_err_sigma)

    if median_data > 1.1 or median_data < 0.9:
        y_lim = np.max([max_err * 1.5, 0.1])
        # y_lim = np.max([max_err*2.0, 0.1])
        if own_scaling:
            plt.ylim([median_data + y_lim, median_data - y_lim])
        # plt.y_lim([max_data+y_lim, min_data-y_lim])
        y_label_text = ' [mag] (Vega)'
    else:
        y_lim = max_err * 1.2
        # plt.y_lim([median_data+y_lim,median_data-y_lim])
        if own_scaling:
            plt.ylim([min_data - y_lim, max_data + y_lim])
        # plt.ylim([0, 2])
        y_label_text = ' [flux] (normalized)'
    # plt.ylim(11.7, 11.4)

    #   Set x and y axis label
    plt.xlabel('Julian Date', fontsize=15)
    plt.ylabel(data_column + y_label_text, fontsize=15)

    #   Save plot
    plt.savefig(
        f'{output_dir}/lightcurve{subdirectory}/lightcurve_jd_{name_object}'
        f'_{data_column}{file_name_suffix}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()


def light_curve_fold(
        time_series: TimeSeries, data_column: str, err_column: str,
        output_dir: str, transit_time: str, period: float,
        binning_factor: float | None = None, error_bars: bool = True,
        name_object: str | None = None, file_name_suffix: str = '',
        subdirectory: str = '', file_type: str = 'pdf') -> None:
    """
    Plot a folded light curve

    Parameters
    ----------
    time_series
        Time series

    data_column
        Filter

    err_column
        Name of the error column

    output_dir
        Output directory

    transit_time
        Time of the transit - Format example: "2020-09-18T01:00:00"

    period
        The period in days

    binning_factor
        Light-curve binning-factor in days
        Default is ``None``.

    error_bars
        If True error bars will be plotted.
        Default is ``False``.

    name_object
        Name of the object
        Default is ``None``.

    file_name_suffix
        Suffix to add to the file name
        Default is ``''``

    subdirectory
        Name of the subdirectory in which to save the plots

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    if subdirectory != '':
        checks.check_output_directories(
            output_dir,
            f'{output_dir}/lightcurve{subdirectory}',
        )
    else:
        checks.check_output_directories(
            output_dir,
            os.path.join(output_dir, 'lightcurve'),
        )

    #   Make a time object for the  transit times
    transit_time = Time(transit_time, format='isot', scale='utc')

    #   Fold lightcurve
    ts_folded = time_series.fold(
        period=float(period) * u.day,
        epoch_time=transit_time,
    )

    #   Make plot
    fig = plt.figure(figsize=(20, 9))

    #   Plot grid
    plt.grid(True, color='lightgray', linestyle='--')

    #   Set tick size
    plt.tick_params(axis='x', labelsize=15)
    plt.tick_params(axis='y', labelsize=15)

    #   Set title
    if name_object is None:
        fig.suptitle('Folded light curve', fontsize=30)
    else:
        fig.suptitle(f'Folded light curve - {name_object}', fontsize=30)

    #   Calculate binned lightcurve => plot
    if binning_factor is not None:
        ts_binned = aggregate_downsample(
            ts_folded,
            time_bin_size=binning_factor * u.day,
        )

        #   Remove zero entries in case the binning time is smaller than the
        #   time between the data points
        mask = np.array(ts_binned[data_column]) == 0.
        mask = np.invert(mask)

        if error_bars:
            plt.errorbar(
                ts_binned.time_bin_start.jd[mask],
                np.array(ts_binned[data_column][mask]),
                yerr=np.array(ts_binned[err_column][mask]),
                # fmt='k.',
                marker='o',
                ls='none',
                elinewidth=1,
                markersize=3,
                capsize=2,
                ecolor='dodgerblue',
                color='darkred',
            )
        else:
            plt.plot(
                ts_binned.time_bin_start.jd[mask],
                ts_binned[data_column][mask],
                'k.',
                markersize=3,
            )
    else:
        if error_bars:
            plt.errorbar(
                ts_folded.time.jd,
                np.array(ts_folded[data_column]),
                yerr=np.array(ts_folded[err_column]),
                # fmt='k.',
                marker='o',
                ls='none',
                elinewidth=1,
                markersize=3,
                capsize=2,
                ecolor='dodgerblue',
                color='darkred',
            )
        else:
            plt.plot(
                ts_folded.time.jd,
                ts_folded[data_column],
                'k.',
                markersize=3,
            )

    #   Get median of the data
    median_data = np.median(ts_folded[data_column].value)
    min_data = np.min(ts_folded[data_column].value)
    max_data = np.max(ts_folded[data_column].value)

    #   Invert y-axis
    if median_data > 1.5 or median_data < 0.5:
        plt.gca().invert_yaxis()

    # plt.y_lim([0.97,1.03])

    #   Set plot limits
    y_err = time_series[err_column].value
    y_err_sigma = sigma_clipping(y_err, sigma=1.5)
    max_err = np.max(y_err_sigma)

    if median_data > 1.1 or median_data < 0.9:
        y_lim = np.max([max_err * 1.5, 0.1])
        plt.ylim([median_data + y_lim, median_data - y_lim])
        y_label_text = ' [mag] (Vega)'
    else:
        y_lim = max_err * 1.3
        # plt.y_lim([median_data - y_lim, median_data + y_lim])
        plt.ylim([min_data - y_lim, max_data + y_lim])
        y_label_text = ' [flux] (normalized)'

    #   Set x and y axis label
    plt.xlabel('Time (days)', fontsize=16)
    plt.ylabel(data_column + y_label_text, fontsize=16)

    #   Save plot
    plt.savefig(
        f'{output_dir}/lightcurve{subdirectory}/lightcurve_folded_{name_object}'
        f'_{data_column}{file_name_suffix}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()


#   TODO: Fix type hints for fit_function
def plot_transform(
        output_dir: str, filter_1: str, filter_2: str, current_filter: str,
        target_filter: str, color_literature: np.ndarray,
        fit_variable: np.ndarray, a_fit: float, b_fit: float,
        b_err_fit: float, fit_function: any, air_mass: float,
        color_literature_err: np.ndarray | None = None,
        fit_variable_err: np.ndarray | None = None,
        name_object: list[str] | str | None = None,
        image_id: int | None = None, x_data_original: np.ndarray | None = None,
        y_data_original: np.ndarray | None = None,
        file_type: str = 'pdf') -> None:
    """
    Plots illustrating magnitude transformation results

    Parameters
    ----------
    output_dir
        Output directory

    filter_1
        Filter 1

    filter_2
        Filter 2

    current_filter
        Current filter

    target_filter
        Filter for which the derived parameters will be used

    color_literature
        Colors of the calibration stars

    fit_variable
        Fit variable

    a_fit
        First parameter of the fit

    b_fit
        Second parameter of the fit
        Currently only two fit parameters are supported
        TODO: -> Needs to generalized

    b_err_fit
        Error of `b`

    fit_function
        Fit function, used for determining the fit

    air_mass
        Air mass

    color_literature_err
        Color errors of the calibration stars
        Default is ``None``.

    fit_variable_err
        Fit variable errors
        Default is ``None``.

    name_object
        Name of the object
        Default is ``None``.

    image_id
        ID of the image

    x_data_original
        Original abscissa data with out any modification, which might
        have been applied to data

    y_data_original
        Original ordinate data with out any modification, which might
        have been applied to data

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'trans_plots'),
    )

    #   Add image ID to file name, if available
    if image_id is not None:
        id_image_str = f'_{image_id}'
    else:
        id_image_str = ''

    #   Fit data
    x_lin = np.sort(color_literature)
    y_lin = fit_function(x_lin, a_fit, b_fit)

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set labels etc.
    air_mass = round(air_mass, 2)
    #   coeff  = b
    if name_object is None:
        title = f'{current_filter}{filter_1.lower()}{filter_2.lower()}' \
                f'-mag transform ({current_filter}-{current_filter.lower()}' \
                f' vs. {filter_1}-{filter_2}) (X = {air_mass}, ' \
                f'target filter: {target_filter})'
    else:
        title = f'{current_filter}{filter_1.lower()}{filter_2.lower()}' \
                f'-mag transform ({current_filter}-{current_filter.lower()}' \
                f' vs. {filter_1}-{filter_2}) - {name_object}' \
                f' (X = {air_mass})'
    y_label = f'{current_filter}-{current_filter.lower()} [mag]'
    path = f'{output_dir}/trans_plots/{target_filter}_{current_filter}' \
           f'{current_filter.lower()}_{filter_1}{filter_2}{id_image_str}.{file_type}'
    p_label = (f'slope = {b_fit:.5f}, C{current_filter.lower()}_{filter_1.lower()}'
               f'{filter_2.lower()} = {b_fit:.5f} +/- {b_err_fit:.5f}')
    x_label = f'{filter_1}-{filter_2} [mag]'

    #   Make plot
    fig = plt.figure(figsize=(15, 8))

    #   Set title
    fig.suptitle(title, fontsize=20)

    if x_data_original is not None and y_data_original is not None:
        plt.errorbar(
            x_data_original,
            y_data_original,
            marker='o',
            markersize=3,
            capsize=2,
            color='darkred',
            ecolor='wheat',
            elinewidth=1,
            linestyle='none',
        )

    #   Plot data
    plt.errorbar(
        color_literature,
        fit_variable,
        xerr=color_literature_err,
        yerr=fit_variable_err,
        marker='o',
        markersize=3,
        capsize=2,
        color='darkgreen',
        ecolor='wheat',
        elinewidth=1,
        linestyle='none',
    )

    #   Plot fit
    plt.plot(
        x_lin,
        y_lin,
        linestyle='-',
        color='maroon',
        linewidth=1.,
        label=p_label,
    )

    #   Set legend
    plt.legend(
        bbox_to_anchor=(0., 1.02, 1.0, 0.102),
        loc=3,
        ncol=4,
        mode='expand',
        borderaxespad=0.,
    )

    #   Set x and y axis label
    plt.xlabel(x_label, fontsize=16)
    plt.ylabel(y_label, fontsize=16)

    #   Add grid
    plt.grid(True, color='lightgray', linestyle='--', alpha=0.3)

    #   Get median of the data
    y_min = np.min(fit_variable)
    y_max = np.max(fit_variable)

    #   Set plot limits
    if fit_variable_err is not None:
        y_err = fit_variable_err
        y_err_sigma = sigma_clipping(y_err, sigma=1.5)
        max_err = np.max(y_err_sigma)

        y_lim = np.max([max_err * 1.5, 0.1])
        plt.ylim([y_max + y_lim, y_min - y_lim])

    #   Save plot
    plt.savefig(path, bbox_inches='tight', format=file_type)
    plt.close()


class MakeCMDs:
    """
    This class contains the necessary functionality for color magnitude plots.
    It allows:
        * to create apparent CMDs
        * to create absolute CMDs
        * to plot isochrones
        * to fit isochrone to the absolute CMD
    """

    def __init__(
            self, name_of_star_cluster: str, file_name: str, file_type: str,
            filter_2: str, filter_1: str, magnitude_color: np.ndarray,
            magnitude_filter_2: np.ndarray,
            color_err: np.ndarray | None = None,
            magnitude_filter_2_err: np.ndarray | None = None,
            output_dir: str = 'output') -> None:
        """
        Parameters
        ----------
        name_of_star_cluster
            Name of cluster

        file_name
            Base name of the file to write

        file_type
            File type

        filter_2
            First filter

        filter_1
            Second filter

        magnitude_color
            Color - 1D

        magnitude_filter_2
            Filter magnitude - 1D

        color_err
            Error for ``mag_color``
            Default is ``None``.

        magnitude_filter_2_err
            Error for ``magnitude_filter_2``
            Default is ``None``.

        output_dir
            Output directory
            Default is ``output``.
        """
        self.name_of_star_cluster = name_of_star_cluster
        self.file_name = file_name
        self.file_type = file_type
        self.filter_2 = filter_2
        self.filter_1 = filter_1
        self.color = f'{filter_1}-{filter_2}'
        self.magnitude_color = magnitude_color
        self.magnitude_filter_2 = magnitude_filter_2
        self.magnitude_color_err = color_err
        self.magnitude_filter_2_err = magnitude_filter_2_err
        self.output_dir = output_dir

        #   Additional attributes filled later
        self.magnitude_filter_2_absolute: np.ndarray | None = None
        self.magnitude_color_absolute: np.ndarray | None = None

    def set_cmd_plot_details(
            self, y_range_max: str | float, y_range_min: str | float,
            x_range_max: str | float, x_range_min: str | float,
            ax: plt.subplot) -> None:
        """
        Check the CMD plot dimensions and set defaults

        Parameters
        ----------
        y_range_max
            The maximum of the plot range in Y direction

        y_range_min
            The minimum of the plot range in Y direction

        x_range_max
            The maximum of the plot range in X direction

        x_range_min
            The minimum of the plot range in X direction

        ax
            Subplot
        """
        #   Check for absolute vs. apparent CMD
        try:
            magnitude_2 = self.magnitude_filter_2_absolute
            color = self.magnitude_color_absolute
        except AttributeError:
            magnitude_2 = self.magnitude_filter_2
            color = self.magnitude_color

        #   Set plot range -> automatic adjustment
        #   Y range
        try:
            float(y_range_max)
        except ValueError:
            ax.set_ylim([
                float(np.max(magnitude_2)) + 0.5,
                float(np.min(magnitude_2)) - 0.5
            ])
            terminal_output.print_to_terminal(
                "[Info] Use automatic plot range for Y",
                style_name='WARNING',
            )
        else:
            try:
                float(y_range_min)
            except ValueError:
                ax.set_ylim([
                    float(np.max(magnitude_2)) + 0.5,
                    float(np.min(magnitude_2)) - 0.5
                ])
                terminal_output.print_to_terminal(
                    "[Info] Use automatic plot range for Y",
                    style_name='WARNING',
                )
            else:
                ax.set_ylim([float(y_range_min), float(y_range_max)])

        #   X range
        try:
            float(x_range_max)
        except ValueError:
            ax.set_xlim([
                float(np.min(color)) - 0.5,
                float(np.max(color)) + 0.5
            ])
            terminal_output.print_to_terminal(
                "[Info] Use automatic plot range for X",
                style_name='WARNING',
            )
        else:
            try:
                float(x_range_min)
            except ValueError:
                ax.set_xlim([
                    float(np.min(color)) - 0.5,
                    float(np.max(color)) + 0.5
                ])
                terminal_output.print_to_terminal(
                    "[Info] Use automatic plot range for X",
                    style_name='WARNING',
                )
            else:
                ax.set_xlim([float(x_range_min), float(x_range_max)])

    def write_cmd(self, plot_type: str):
        """
        Write plot to disk

        Parameters
        ----------
        plot_type
            Plot type
        """
        cmd_dir = f'{self.output_dir}/cmds'
        checks.check_output_directories(cmd_dir)

        if self.name_of_star_cluster == "" or self.name_of_star_cluster == "?":
            path = (f'{cmd_dir}/{self.file_name}_{plot_type}'
                    f'_{self.filter_2}_{self.color}.{self.file_type}')
            terminal_output.print_to_terminal(
                f"Save CMD plot ({self.file_type}): {path}",
            )
            plt.savefig(
                path,
                format=self.file_type,
                bbox_inches="tight",
            )
        else:
            name_of_star_cluster = self.name_of_star_cluster.replace(
                ' ',
                '_',
            )
            path = (f'{cmd_dir}/{self.file_name}_{name_of_star_cluster}'
                    f'_{plot_type}_{self.filter_2}_{self.color}'
                    f'.{self.file_type}')
            terminal_output.print_to_terminal(
                f"Save CMD plot ({self.file_type}): {path}\n",
            )
            plt.savefig(
                path,
                format=self.file_type,
                bbox_inches="tight",
            )

    def decode_isochrone_filter_relation(
            self, isochrone_column_type: dict[str, str],
            isochrone_column: dict[str, int], current_filter: str,
            relation_list: list[tuple[int, int]], recursion_number: int
            ) -> list[tuple[int, int]]:
        """
        Decodes relationship between isochrone entries. It fills a list with
        tuples of two in integer each. The first integer gives the ID of the filter
        and the second one specifies how the magnitude is derived from the
        relationships. The second integer can be 1 or -1 and determines whether the
        isochrone magnitude of this particular relationship must be added or
        subtracted.

        Parameter
        ---------
        isochrone_column_type
            Type of the columns from the ISO file
            Keys = filter : `string`
            Values = type : `string`

        isochrone_column
            Columns to use from the ISO file.
            Keys = filter           : `string`
            Values = column numbers : `integer`

        current_filter
            Current filter

        relation_list
            List with relations. Each tuple is one relationship. In each tuple the
            first integer gives the ID of the filter and the second one determines
            how the magnitude is derived from the relationships. The second integer
            can be 1 or -1 and determines whether the isochrone magnitude of this
            particular relationship must be added or subtracted.

        recursion_number

        Returns
        -------
        relation_list
            See above
        """
        #   Exit if recursion is two high
        if recursion_number > 10:
            raise MaxRecursionError(
                f'Could not decode magnitudes from isochrone file '
                f'because maximum number of recursions reached during '
                f'color calculation'
            )

        #   Distinguish between color and 'single' magnitude entries
        if isochrone_column_type[current_filter][0] == 'single':
            relation_list.append(
                (isochrone_column[current_filter], 1)
            )
            return relation_list
        else:
            #   Set filter from color
            next_filter = isochrone_column_type[current_filter][2]

            #   Repeat until a single magnitude is found
            relation_list = self.decode_isochrone_filter_relation(
                isochrone_column_type,
                isochrone_column,
                next_filter,
                relation_list,
                recursion_number + 1,
            )

            #   Now we have to distinguish between, e.g., B-V vs. V-B
            if isochrone_column_type[current_filter][1] == 0:
                relation_list.append(
                    (isochrone_column[current_filter], 1)
                )

            else:
                relation_list.append(
                    (isochrone_column[current_filter], -1)
                )

            return relation_list

    @staticmethod
    def apply_isochrone_filter_relation(
            relation_list: list[tuple[int, int]], iso_data_line: list[str]
            ) -> float:
        """
        Uses isochrone filter relation such as color to derive individual
        magnitudes

        Parameter
        ---------
        relation_list
            List with relations. Each tuple is one relationship. In each tuple the
            first integer gives the ID of the filter and the second one determines
            how the magnitude is derived from the relationships. The second integer
            can be 1 or -1 and determines whether the isochrone magnitude of this
            particular relationship must be added or subtracted.

        iso_data_line
            Line with iso data - list of strings

        Returns
        -------
        target_magnitude
            Calculated magnitude
        """
        target_magnitude = 0.

        #   Calculate magnitude
        for relation in relation_list:
            relation_magnitude = float(iso_data_line[relation[0] - 1]) * relation[1]
            target_magnitude = target_magnitude + relation_magnitude

        return target_magnitude

    def fill_lists_with_isochrone_magnitudes(
            self, isochrone_data_line: list[str],
            isochrone_relation_filter_1: list[tuple[int, int]],
            isochrone_relation_filter_2: list[tuple[int, int]],
            isochrone_magnitude_2: list[float], isochrone_color: list[float]
            ) -> tuple[list[float], list[float]]:
        """
        Sort magnitudes and colors from isochrone files into lists and calculate
        the required color if necessary

        Parameter
        ---------
        isochrone_data_line
            Line with iso data - list of strings

        isochrone_relation_filter_1
            List with relation for filter 1. Each tuple is one relationship. In
            each tuple the first integer gives the ID of the filter and the second
            one determines how the magnitude is derived from the relationships. The
            second integer can be 1 or -1 and determines whether the isochrone
            magnitude of this particular relationship must be added or subtracted.

        isochrone_relation_filter_2
            List with relation for filter 2. Each tuple is one relationship. In
            each tuple the first integer gives the ID of the filter and the second
            one determines how the magnitude is derived from the relationships. The
            second integer can be 1 or -1 and determines whether the isochrone
            magnitude of this particular relationship must be added or subtracted.

        isochrone_magnitude_2
            List to fill with magnitudes (second filter)

        isochrone_color
            List to fill with color values

        Returns
        -------
        isochrone_magnitude_2
            Magnitude list (second filter)

        isochrone_color
            Color list
        """
        #   Calculate magnitudes and color
        magnitude_1 = self.apply_isochrone_filter_relation(
            isochrone_relation_filter_1,
            isochrone_data_line,
        )
        magnitude_2 = self.apply_isochrone_filter_relation(
            isochrone_relation_filter_2,
            isochrone_data_line,
        )
        color = magnitude_1 - magnitude_2

        isochrone_magnitude_2.append(magnitude_2)
        isochrone_color.append(color)

        return isochrone_magnitude_2, isochrone_color

    @staticmethod
    def calculate_chi_square(
            magnitude_filter_2: np.ndarray, magnitude_color: np.ndarray,
            isochrone_array: np.ndarray, nearst_neighbour_indexes: np.ndarray
            ) -> tuple[np.ndarray, np.ndarray, list[float]]:
        """
        Parameters
        ----------
        magnitude_filter_2
            Object magnitudes of filter 2

        magnitude_color
            Object colors

        isochrone_array
            Array with isochrone data

        nearst_neighbour_indexes
            Indexes of the nearest isochrone points to the reference points
            of the observed objects.

        Returns
        -------
        chi_square_magnitude_2
            Chi square based on object magnitudes

        chi_square_color
            Chi square based on object color

        chi_square_list
            See above
        """
        #   Calculate chi square
        chi_square_magnitude_2 = np.square(
            magnitude_filter_2[:, 1] - isochrone_array[:, 0][nearst_neighbour_indexes]
        ).sum()
        chi_square_color = np.square(
            magnitude_color[:, 1] - isochrone_array[:, 1][nearst_neighbour_indexes]
        ).sum()
        chi_square_total = chi_square_magnitude_2 + chi_square_color

        return chi_square_magnitude_2, chi_square_color, chi_square_total

    def plot_apparent_cmd(
            self, figure_size_x: str = '', figure_size_y: str = '',
            y_plot_range_max: str = '', y_plot_range_min: str = '',
            x_plot_range_max: str = '', x_plot_range_min: str = '') -> None:
        """
        Plot calibrated cmd with apparent magnitudes

        Parameters
        ----------
        figure_size_x
            Figure size in cm (x direction)

        figure_size_y
            Figure size in cm (y direction)

        y_plot_range_max
            The maximum of the plot range in Y direction

        y_plot_range_min
            The minimum of the plot range in Y direction

        x_plot_range_max
            The maximum of the plot range in X direction

        x_plot_range_min
            The minimum of the plot range in X direction
        """
        #   Initialize, set defaults and check plot dimensions
        initialize_plot(
            figure_size_x,
            figure_size_y,
        )

        ax0 = plt.subplot(1, 1, 1)

        self.set_cmd_plot_details(
            y_plot_range_max,
            y_plot_range_min,
            x_plot_range_max,
            x_plot_range_min,
            ax0,
        )

        #   Plot the stars
        terminal_output.print_to_terminal("Add stars", indent=1)
        ax0.errorbar(
            self.magnitude_color,
            self.magnitude_filter_2,
            yerr=self.magnitude_filter_2_err,
            xerr=self.magnitude_color_err,
            marker='o',
            ls='none',
            elinewidth=0.5,
            markersize=2,
            capsize=2,
            ecolor='#ccdbfd',
            color='darkred',
            alpha=0.4,
        )

        #   Set ticks and labels
        mk_ticks_labels(
            rf'${self.filter_2}$ [mag]',
            rf'${self.color}$ [mag]',
            ax0,
        )

        #   Write plot to disk
        self.write_cmd('apparent')
        plt.close()

    def plot_absolute_cmd(
            self, e_b_v: float, m_m: float, isochrones: str,
            isochrone_type: str, isochrone_column_type: dict[str, str],
            isochrone_column: dict[str, int], isochrone_log_age: bool,
            isochrone_keyword: str, isochrone_legend: bool,
            figure_size_x: str = '', figure_size_y: str = '',
            y_plot_range_max: str = '', y_plot_range_min: str = '',
            x_plot_range_max: str = '', x_plot_range_min: str = '',
            rv: float = 3.1, fit_isochrone: bool = False,
            magnitude_fit_range: tuple[float | None, float | None] = (None, None),
            n_bin_observation: int = 40,
            fiduciary_points_observation: bool | None = None,
            fiduciary_points_isochrones: bool = False,
            chi_square_plot_mode: str | None = None) -> None:
        """
        Plot calibrated CMD with
            * magnitudes corrected for reddening and distance
            * isochrones

        Parameters
        ----------
        e_b_v                       : `float`
            Relative extinction between B and V band

        m_m                         : `float`
            Distance modulus

        isochrones                  : `string`
            Path to the isochrone directory or the isochrone file

        isochrone_type              : `string`
            Type of 'isochrones'
            Possibilities: 'directory' or 'file'

        isochrone_column_type       : `dictionary`
            Keys = filter : `string`
            Values = type : `string`

        isochrone_column            : `dictionary`
            Keys = filter           : `string`
            Values = column numbers : `integer`

        isochrone_log_age           : `boolean`
            Logarithmic age

        isochrone_keyword           : `string`
            Keyword to identify a new isochrone

        isochrone_legend            : `boolean`
            If True plot legend for isochrones.

        rv                          : `float`, optional
            Ration between absolute and relative extinction
            Default is ``3.1``.

        figure_size_x               : `float`, optional
            Figure size in cm (x direction)
            Default is ````.

        figure_size_y               : `float`, optional
            Figure size in cm (y direction)
            Default is ````.

        y_plot_range_max            : `float`, optional
            The maximum of the plot range in Y
                                direction
            Default is ````.

        y_plot_range_min            : `float`, optional
            The minimum of the plot range in Y
                                direction
            Default is ````.

        x_plot_range_max            : `float`, optional
            The maximum of the plot range in X
                                direction
            Default is ````.

        x_plot_range_min            : `float`, optional
            The minimum of the plot range in X direction

        fit_isochrone               : `bool`, optional
            If `True`, the best fitting isochrone will be determined.
            Default is ``False``.

        magnitude_fit_range         : `tuple` of `float` or `None`
            Magnitude range to be used for the isochrone fitting and binning
            of the observations. If set to None, the minimum and maximum
            value are used.
            Default is ``(None, None)``,

        n_bin_observation           : `integer`, optional
            Number of bins into which the observation data will be combined.
            Default is ``40``.

        fiduciary_points_observation : `bool` or `None`, optional
            Determined if the binned observation will be plotted. Is set to
            `True` if fit_isochrone is `True` with the exception that
            fiduciary_points_observation is explicitly set to `False`.
            Default is ``None``.

        fiduciary_points_isochrones  : `bool`, optional
            If 'True', the isochrone points closest to the fiduciary observation
            points will be plotted.
            Default is ``False``.

        chi_square_plot_mode        : `string` or None, optional
            Mode to plot the chi square values from the isochrone fits.
            Possibilities: 1. simple   -> Combined chi square values shown on
                                          the right hand side.
                           2. detailed -> Chi square values split according
                                          to X and Y contributions. Plots are
                                          on top and on the right hand side of
                                          the CMD
            If `None` and fit_isochrone is `True` chi_square_plot_mode is set
            to `simple`.
            Default is ``None``.
        """
        #   Correct for reddening and distance
        if self.filter_1 == 'B' and self.filter_2 == 'V':
            a_filter_2 = rv * e_b_v
            relative_extinction = e_b_v
        else:
            #   Get effective filter wavelengths
            filter_1_effective_wavelength = calibration_parameters.filter_effective_wavelength[self.filter_1]
            filter_2_effective_wavelength = calibration_parameters.filter_effective_wavelength[self.filter_2]

            #   Get Fitzpatrick's extinction curve
            extinction_curve = calibration_parameters.fitzpatrick_extinction_curve(rv)

            #   Get absolute extinction in the filter
            a_filter_1 = extinction_curve(10000. / filter_1_effective_wavelength) * e_b_v
            a_filter_2 = extinction_curve(10000. / filter_2_effective_wavelength) * e_b_v

            #   Calculate relative extinction
            relative_extinction = a_filter_1 - a_filter_2

        #   TODO: Add error propagation. What is the error of rv and e_b_v?
        #   Apply extinction correction (and distance) to magnitudes and color
        magnitude_filter_2 = self.magnitude_filter_2 - a_filter_2 - m_m
        magnitude_color = self.magnitude_color - relative_extinction
        self.magnitude_filter_2_absolute = magnitude_filter_2
        self.magnitude_color_absolute = magnitude_color

        #   Plot fiduciary points if isochrone fit is performed
        if fiduciary_points_observation is None and fit_isochrone:
            fiduciary_points_observation = True
        #   Plot chi square deviation of isochrones from fiduciary points if fit is
        #   performed
        if fit_isochrone and chi_square_plot_mode is None:
            chi_square_plot_mode = 'simple'

        #   Initialize plot and check plot dimensions
        fig = initialize_plot(
            figure_size_x,
            figure_size_y,
        )

        #   Create grid for different subplots
        spec = gridspec.GridSpec(
            ncols=2,
            nrows=2,
            width_ratios=[4, 1],
            wspace=0.3,
            hspace=0.2,
            height_ratios=[4, 1],
        )

        #   Add main plot to plot grid
        ax0 = fig.add_subplot(spec[0])

        #   Set plot details
        self.set_cmd_plot_details(
            y_plot_range_max,
            y_plot_range_min,
            x_plot_range_max,
            x_plot_range_min,
            ax0,
        )

        #   Plot the stars
        terminal_output.print_to_terminal("Add stars")
        ax0.errorbar(
            magnitude_color,
            magnitude_filter_2,
            yerr=self.magnitude_filter_2_err,
            xerr=self.magnitude_color_err,
            marker='o',
            ls='none',
            elinewidth=0.5,
            markersize=2,
            capsize=2,
            ecolor='#ccdbfd',
            color='darkred',
            alpha=0.3,
        )

        #   Bin observation
        if fiduciary_points_observation or fit_isochrone:
            #   Check if fit range is defined. If not, minimum and maximum
            #   values of the data are used.
            if magnitude_fit_range[0] is None:
                min_magnitude_filter_2 = np.min(magnitude_filter_2)
            else:
                min_magnitude_filter_2 = magnitude_fit_range[0]
            if magnitude_fit_range[1] is None:
                max_magnitude_filter_2 = np.max(magnitude_filter_2)
            else:
                max_magnitude_filter_2 = magnitude_fit_range[1]

            #   Define bins
            bins = np.linspace(
                min_magnitude_filter_2,
                max_magnitude_filter_2,
                n_bin_observation,
            )

            #   Perform binning
            digitized = np.digitize(magnitude_filter_2, bins)
            #   TODO: Rewrite to make it easier to read
            magnitude_filter_2_binned = []
            magnitude_color_binned = []
            for i in range(1, len(bins)):
                if len(magnitude_filter_2[digitized == i]) != 0:
                    magnitude_filter_2_binned.append(
                        sigma_clipped_stats(magnitude_filter_2[digitized == i])
                    )
                if len(magnitude_color[digitized == i]) != 0:
                    magnitude_color_binned.append(
                        sigma_clipped_stats(magnitude_color[digitized == i])
                    )
            magnitude_filter_2_binned = np.array(magnitude_filter_2_binned)
            magnitude_color_binned = np.array(magnitude_color_binned)
            magnitude_binned_array = np.array([magnitude_filter_2_binned[:, 1], magnitude_color_binned[:, 1]]).T

            if fiduciary_points_observation:
                ax0.errorbar(
                    magnitude_color_binned[:, 1],
                    magnitude_filter_2_binned[:, 1],
                    xerr=magnitude_color_binned[:, 2],
                    yerr=magnitude_filter_2_binned[:, 2],
                    marker='o',
                    ls='none',
                    elinewidth=1.0,
                    markersize=5,
                    capsize=3,
                    ecolor='#338af7',
                    color='#F8B195',
                    alpha=0.9,
                    zorder=99.,
                )
        else:
            magnitude_binned_array = None
            magnitude_filter_2_binned = None
            magnitude_color_binned = None

        #   Plot isochrones
        #
        #   Check if isochrones are specified
        if isochrones != '' and isochrones != '?':
            #   Decode relationships between isochrone magnitudes such as color
            #   relationships
            isochrone_magnitude_relation_filter_1 = self.decode_isochrone_filter_relation(
                isochrone_column_type,
                isochrone_column,
                self.filter_1,
                [],
                0,
            )
            isochrone_magnitude_relation_filter_2 = self.decode_isochrone_filter_relation(
                isochrone_column_type,
                isochrone_column,
                self.filter_2,
                [],
                0,
            )

            #   Initialize chi square subplots
            if chi_square_plot_mode == 'detailed' and fit_isochrone:
                ax1 = fig.add_subplot(spec[1])
                ax2 = fig.add_subplot(spec[2])
            elif chi_square_plot_mode == 'simple' and fit_isochrone:
                ax2 = fig.add_subplot(spec[2])
            else:
                ax1 = None
                ax2 = None

            #   Prepare list for chi square values
            age_list = []
            chi_square_list = []
            chi_square_magnitude_2_list = []
            chi_square_color_list = []
            isochrones_list = []

            #   OPTION I: Individual isochrone files in a specific directory
            if isochrone_type == 'directory':
                #   Resolve iso path
                isochrones = Path(isochrones).expanduser()

                #   Make list of isochrone files
                file_list = os.listdir(isochrones)

                #   Number of isochrones
                n_isochrones = len(file_list)
                terminal_output.print_to_terminal(
                    f"Plot {n_isochrones} isochrone(s)",
                    style_name='OKGREEN',
                )

                #   Make color map
                color_pick = mk_colormap(n_isochrones)

                #   Prepare cycler for the line styles
                line_cycler = mk_line_cycler()

                #   Cycle through iso files
                for i in range(0, n_isochrones):
                    #   Load file
                    isochrone_data = open(isochrones / file_list[i])

                    #   Prepare variables for the isochrone data
                    isochrone_magnitude_2 = []
                    isochrone_color = []
                    age_value = ''
                    age_unit = ''

                    #   Extract B and V values & make lists
                    #   Loop over all lines in the file
                    for line in isochrone_data:
                        line_elements = line.split()

                        #   Check that the entries are not HEADER keywords
                        try:
                            float(line_elements[0])
                        except (ValueError, IndexError):
                            #   Try to find and extract age information
                            if 'Age' in line_elements or 'age' in line_elements:
                                try:
                                    age_index = line_elements.index('age')
                                except ValueError:
                                    age_index = line_elements.index('Age')

                                for string in line_elements[age_index + 1:]:
                                    #   Find age unit
                                    if string.rfind("yr") != -1:
                                        age_unit = string
                                    #   Find age value
                                    try:
                                        if isinstance(age_value, str):
                                            age_value = float(string)
                                            if age_value >= 1000. and age_unit.rfind('Myr') != -1:
                                                age_value /= 1000.
                                                age_unit = 'Gyr'
                                            if age_unit.rfind('Myr') != -1:
                                                age_unit = 'Myr'
                                            age_list.append(age_value)
                                    except (TypeError, ValueError):
                                        pass
                            continue

                        #   Fill lists
                        isochrone_magnitude_2, isochrone_color = self.fill_lists_with_isochrone_magnitudes(
                            line_elements,
                            isochrone_magnitude_relation_filter_1,
                            isochrone_magnitude_relation_filter_2,
                            isochrone_magnitude_2,
                            isochrone_color,
                        )

                    #   Close file with the iso data
                    isochrone_data.close()

                    #   Construct label
                    if not isinstance(age_value, str):
                        label = str(age_value)
                        if age_unit != '':
                            label += f' {age_unit}'
                    else:
                        label = os.path.splitext(file_list[i])[0]

                    if fit_isochrone:
                        #   Find points to compare with binned observations
                        isochrone_array = np.array(
                            [isochrone_magnitude_2, isochrone_color]
                        ).T
                        isochrones_list.append(isochrone_array)
                        isochrone_tree = KDTree(isochrone_array, leafsize=100)
                        _, nearst_neighbour_indexes = isochrone_tree.query(
                            magnitude_binned_array,
                            k=1,
                        )
                    else:
                        nearst_neighbour_indexes = None
                        isochrone_array = None

                    #   Plot iso lines
                    if fiduciary_points_isochrones:
                        ax0.plot(
                            isochrone_array[:, 1][nearst_neighbour_indexes],
                            isochrone_array[:, 0][nearst_neighbour_indexes],
                            marker='o',
                            ls='none',
                            color=color_pick.to_rgba(i),
                            alpha=0.5,
                        )
                    if fit_isochrone:
                        alpha_isochrone = 0.2
                    else:
                        alpha_isochrone = 0.5
                    ax0.plot(
                        isochrone_color,
                        isochrone_magnitude_2,
                        linestyle=next(line_cycler),
                        color=color_pick.to_rgba(i),
                        linewidth=1.2,
                        label=label,
                        alpha=alpha_isochrone,
                    )

                    if fit_isochrone:
                        #   Calculate chi square
                        chi_square_magnitude_2, chi_square_color, chi_square_total = self.calculate_chi_square(
                            magnitude_filter_2_binned,
                            magnitude_color_binned,
                            isochrone_array,
                            nearst_neighbour_indexes,
                        )
                        chi_square_magnitude_2_list.append(
                            chi_square_magnitude_2
                        )
                        chi_square_color_list.append(chi_square_color)
                        chi_square_list.append(chi_square_total)

                        #   Plot chi square values
                        if chi_square_plot_mode == 'detailed':
                            ax1.scatter(
                                chi_square_magnitude_2,
                                age_value,
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )
                            ax2.scatter(
                                age_value,
                                chi_square_color,
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )
                        elif chi_square_plot_mode == 'simple':
                            ax2.scatter(
                                age_value,
                                chi_square_color + chi_square_magnitude_2,
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )

            #   OPTION II: Isochrone file containing many individual isochrones
            if isochrone_type == 'file':
                #   Resolve iso path
                isochrones = Path(isochrones).expanduser()

                #   Load file
                isochrone_data = open(isochrones)

                #   Overall lists for the isochrones
                nearst_neighbour_indexes_list = []

                #   Number of detected isochrones
                n_isochrones = 0

                #   Loop over all lines in the file
                for line in isochrone_data:
                    line_elements = line.split()

                    #   Check for a key word to distinguish the isochrones
                    try:
                        if line[0:len(isochrone_keyword)] == isochrone_keyword:
                            #   Add data from the last isochrone to the overall
                            #   lists for the isochrones.
                            if n_isochrones:
                                #   This part is only active after an isochrone has
                                #   been detected. The variables are then assigned.
                                age_list.append(float(age))
                                isochrone_array = np.array(
                                    [isochrone_magnitude_2, isochrone_color]
                                ).T
                                isochrones_list.append(isochrone_array)

                                #   Find points to compare with binned observations
                                if fit_isochrone:
                                    isochrone_tree = KDTree(
                                        isochrone_array,
                                        leafsize=100,
                                    )
                                    _, nearst_neighbour_indexes = isochrone_tree.query(
                                        magnitude_binned_array,
                                        k=1,
                                    )
                                    nearst_neighbour_indexes_list.append(
                                        nearst_neighbour_indexes
                                    )

                            #   Save age for the case where age is given as a
                            #   keyword and not as a column
                            if isochrone_column['AGE'] == 0:
                                age = line.split('=')[1].split()[0]

                            #   Prepare/reset lists for the single isochrones
                            isochrone_magnitude_2 = []
                            isochrone_color = []

                            n_isochrones += 1
                            continue
                    except RuntimeError:
                        continue

                    #   Check that the entries are not HEADER keywords
                    try:
                        float(line_elements[0])
                    except (ValueError, IndexError):
                        continue

                    if isochrone_column['AGE'] != 0:
                        age = float(line_elements[isochrone_column['AGE'] - 1])

                    #   Fill lists
                    isochrone_magnitude_2, isochrone_color = self.fill_lists_with_isochrone_magnitudes(
                        line_elements,
                        isochrone_magnitude_relation_filter_1,
                        isochrone_magnitude_relation_filter_2,
                        isochrone_magnitude_2,
                        isochrone_color,
                    )

                #   Add last isochrone to overall lists
                #   TODO: Rearrange code so that the following block is not necessary
                age_list.append(float(age))
                isochrone_array = np.array(
                    [isochrone_magnitude_2, isochrone_color]
                ).T
                isochrones_list.append(isochrone_array)
                if fit_isochrone:
                    isochrone_tree = KDTree(isochrone_array, leafsize=100)
                    _, nearst_neighbour_indexes = isochrone_tree.query(
                        magnitude_binned_array,
                        k=1,
                    )
                    nearst_neighbour_indexes_list.append(nearst_neighbour_indexes)

                #   Close isochrone file
                isochrone_data.close()

                #   Number of isochrones
                n_isochrones = len(isochrones_list)
                terminal_output.print_to_terminal(
                    f"Plot {n_isochrones} isochrone(s)",
                    style_name='OKGREEN',
                )

                #   Make color map
                color_pick = mk_colormap(n_isochrones)

                #   Prepare cycler for the line styles
                line_cycler = mk_line_cycler()

                #   Cycle through iso lines
                age_list_new = []
                for i in range(0, n_isochrones):
                    if isochrone_log_age:
                        age_value = 10 ** age_list[i] / 10 ** 9
                        age_value = round(age_value, 3)
                    else:
                        age_value = round(age_list[i], 3)
                    age_unit = 'Gyr'
                    age_string = f'{age_value} {age_unit}'
                    age_list_new.append(age_value)

                    #   Plot iso lines
                    if fiduciary_points_isochrones:
                        ax0.plot(
                            isochrones_list[i][:, 1][nearst_neighbour_indexes_list[i]],
                            isochrones_list[i][:, 0][nearst_neighbour_indexes_list[i]],
                            marker='o',
                            ls='none',
                            color=color_pick.to_rgba(i),
                            alpha=0.5,
                        )
                    if fit_isochrone:
                        alpha_isochrone = 0.2
                    else:
                        alpha_isochrone = 0.5
                    ax0.plot(
                        isochrones_list[i][:, 1],
                        isochrones_list[i][:, 0],
                        linestyle=next(line_cycler),
                        color=color_pick.to_rgba(i),
                        linewidth=1.2,
                        label=age_string,
                        alpha=alpha_isochrone,
                    )

                    if fit_isochrone:
                        #   Calculate chi square
                        chi_square_magnitude_2, chi_square_color, chi_square_total = self.calculate_chi_square(
                            magnitude_filter_2_binned,
                            magnitude_color_binned,
                            isochrones_list[i],
                            nearst_neighbour_indexes_list[i],
                        )
                        chi_square_magnitude_2_list.append(
                            chi_square_magnitude_2
                        )
                        chi_square_color_list.append(chi_square_color)
                        chi_square_list.append(chi_square_total)

                        #   Plot chi square values
                        if chi_square_plot_mode == 'detailed':
                            ax1.plot(
                                chi_square_magnitude_2,
                                age_value,
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )
                            ax2.plot(
                                age_value,
                                chi_square_color,
                                ls='none',
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )
                        elif chi_square_plot_mode == 'simple':
                            ax2.scatter(
                                age_value,
                                chi_square_color + chi_square_magnitude_2,
                                color=color_pick.to_rgba(i),
                                marker='o',
                                alpha=0.2,
                            )
                age_list = age_list_new

            #   Plot legend
            if isochrone_legend:
                legend_ = ax0.legend(
                    bbox_to_anchor=(0., 1.02, 1.0, 0.102),
                    loc=3,
                    ncol=4,
                    mode='expand',
                    borderaxespad=0.,
                )
                for element in legend_.legend_handles:
                    element.set_alpha(0.6)

        if fit_isochrone:
            #   Evaluate chi square
            min_chi_square_id = np.argmin(chi_square_list)

            terminal_output.print_to_terminal(
                f'Best fitting isochrone: {age_list[min_chi_square_id]:.1f} '
                f'{age_unit} with chi^2 = {chi_square_list[min_chi_square_id]:.3f}',
                style_name="GOOD",
            )

            #   Plot best isochrone
            ax0.plot(
                isochrones_list[min_chi_square_id][:, 1],
                isochrones_list[min_chi_square_id][:, 0],
                linestyle='-',
                color=color_pick.to_rgba(min_chi_square_id),
                linewidth=2,
            )

            #   Finish chi square plots
            if chi_square_plot_mode == 'detailed':
                ax1.scatter(
                    chi_square_magnitude_2_list[min_chi_square_id],
                    age_list[min_chi_square_id],
                    color=color_pick.to_rgba(min_chi_square_id),
                    marker='o',
                    alpha=1.0,
                )
                ax2.scatter(
                    age_list[min_chi_square_id],
                    chi_square_color_list[min_chi_square_id],
                    color=color_pick.to_rgba(min_chi_square_id),
                    marker='o',
                    alpha=1.0,
                )
                mk_ticks_labels(
                    f'Age [{age_unit}]',
                    f'$\chi^2$ ',
                    ax1,
                )
                mk_ticks_labels(
                    f'$\chi^2$ ',
                    f'Age [{age_unit}]',
                    ax2,
                )
            elif chi_square_plot_mode == 'simple':
                ax2.scatter(
                    age_list[min_chi_square_id],
                    chi_square_magnitude_2_list[min_chi_square_id] + chi_square_color_list[min_chi_square_id],
                    color=color_pick.to_rgba(min_chi_square_id),
                    marker='o',
                    alpha=1.0,
                )
                mk_ticks_labels(
                    f'$\chi^2$ ',
                    f'Age [{age_unit}]',
                    ax2,
                )

        #   Set ticks and labels for CMD
        mk_ticks_labels(
            rf'${self.filter_2}$ [mag]',
            rf'${self.color}$ [mag]',
            ax0,
        )

        #   Write plot to disk
        self.write_cmd('absolut')
        plt.close()


def initialize_plot(size_x: str, size_y: str) -> plt.figure:
    """
    Check the plot dimensions and set defaults

    Parameters
    ----------
    size_x
        Figure size in cm (x direction)

    size_y
        Figure size in cm (y direction)

    Returns
    -------
    fig
        Figure object
    """
    #   Set figure size
    if size_x == "" or size_x == "?" or size_y == "" or size_y == "?":
        terminal_output.print_to_terminal(
            "[Info] No Plot figure size given, use default: 8cm x 8cm",
            style_name='WARNING',
        )
        fig = plt.figure(figsize=(8, 8))
    else:
        fig = plt.figure(figsize=(int(size_x), int(size_y)))

    return fig


def mk_ticks_labels(
        y_axis_label: str, x_axis_label: str, ax: plt.subplot) -> None:
    """
    Set default ticks and labels

    Parameters
    ----------
    y_axis_label
        Filter

    x_axis_label
        Color

    ax
        Subplot
    """
    #   Set ticks
    ax.tick_params(
        axis='both',
        which='both',
        top=True,
        right=True,
        direction='in',
    )
    ax.minorticks_on()
    ax.grid(True, color='lightgray', linestyle='--')

    #   Set labels
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)


class MaxRecursionError(Exception):
    pass


def mk_colormap(n_color_steps):
    """
        Make a color map e.g. for isochrones

        Parameters
        ----------
        n_color_steps    : `integer`
            Number of things to color
    """
    #   Prepare colormap
    cm1 = mcol.LinearSegmentedColormap.from_list(
        "MyCmapName",
        ['orchid',
         'blue',
         'cyan',
         'forestgreen',
         'limegreen',
         'gold',
         'orange',
         "red",
         'saddlebrown',
         ]
    )
    cnorm = mcol.Normalize(vmin=0, vmax=n_color_steps)
    cpick = cm.ScalarMappable(norm=cnorm, cmap=cm1)
    cpick.set_array([])

    return cpick


def mk_line_cycler() -> cycle:
    """
        Make a line cycler
    """
    lines: list[str] = ["-", "--", "-.", ":"]
    return cycle(lines)


def mk_color_cycler_symbols() -> cycle:
    """
        Make a color cycler
    """
    colors: list[str] = ['darkgreen', 'darkred', 'mediumblue', 'yellowgreen']
    return cycle(colors)


def mk_color_cycler_error_bars() -> cycle:
    """
        Make a color cycler
    """
    colors: list[str] = ['wheat', 'dodgerblue', 'violet', 'gold']
    return cycle(colors)


def onpick3(event):
    print('---------------------')
    print(dir(event))
    ind = event.ind
    # print('onpick3 scatter:', ind, np.take(x, ind))
    print('onpick3 scatter:', ind)
    print(event.artist)
    print(dir(event.artist))
    print(event.artist.get_label())
    print(event.artist.get_gid())
    # print(event.mouseevent)
    # print(dir(event.mouseevent))
    # print(event.mouseevent.inaxes)
    # print(dir(event.mouseevent.inaxes))
    # print(event.name)
    print('+++++++++++++++++++++')


def click_point(event):
    print('---------------------')
    print(dir(event))
    print(event.button)
    print(event.guiEvent)
    print(event.key)
    print(event.lastevent)
    print(event.name)
    print(event.step)
    print('+++++++++++++++++++++')


def d3_scatter(
        xs: list[np.ndarray], ys: list[np.ndarray], zs: list[np.ndarray],
        output_dir: str, color: list[str] | None = None, name_x: str = '',
        name_y: str = '', name_z: str = '', pm_ra: float | None = None,
        pm_dec: float | None = None, display: bool = False,
        file_type: str = 'pdf') -> None:
    """
    Make a 3D scatter plot

    Parameters
    ----------
    xs
        X values

    ys
        Y values

    zs
        Z values

    color
        Specifiers for the color

    output_dir
        Output directory

    name_x
        Label for the X axis
        Default is ````.

    name_y
        Label for the Y axis
        Default is ````.

    name_z
        Label for the Z axis
        Default is ````.

    pm_ra
        Literature proper motion in right ascension.
        If not ``None`` the value will be printed to the plot.
        Default is ``None``.

    pm_dec
        Literature proper motion in declination.
        If not ``None`` the value will be printed to the plot.
        Default is ``None``.

    display
        If ``True`` the 3D plot will be displayed in an interactive
        window. If ``False`` four views of the 3D plot will be saved to
        a file.
        Default is ``False``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Switch backend to allow direct display of the plot
    if display:
        plt.switch_backend('TkAgg')

    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'compare'),
    )

    #   Prepare plot
    fig = plt.figure(figsize=(20, 15), constrained_layout=True)

    #   Set title
    if display:
        if pm_ra is not None and pm_dec is not None:
            fig.suptitle(
                f'Proper motion vs. distance: Literature proper motion: '
                f'{pm_ra:.1f}, {pm_dec:.1f} - Choose a cluster then close the '
                f'plot',
                fontsize=17,
            )
        else:
            fig.suptitle(
                'Proper motion vs. distance: Literature proper motion: '
                '- Choose a cluster then close the plot',
                fontsize=17,
            )
    else:
        if pm_ra is not None and pm_dec is not None:
            fig.suptitle(
                f'Proper motion vs. distance: Literature proper motion: '
                f'{pm_ra:.1f}, {pm_dec:.1f} ',
                fontsize=17,
            )
        else:
            fig.suptitle(
                'Proper motion vs. distance',
                fontsize=17,
            )

    #   Switch to one subplot for direct display
    if display:
        n_subplots = 1
    else:
        n_subplots = 4

    #   Loop over all subplots
    for i in range(0, n_subplots):
        if display:
            ax = fig.add_subplot(1, 1, i + 1, projection='3d')
        else:
            ax = fig.add_subplot(2, 2, i + 1, projection='3d')

        #   Change view angle
        ax.view_init(25, 45 + i * 90)

        #   Labelling X-Axis
        ax.set_xlabel(name_x)

        #   Labelling Y-Axis
        ax.set_ylabel(name_y)

        #   Labelling Z-Axis
        ax.set_zlabel(name_z)

        #   Set default plot ranges/limits
        default_pm_range = [-20, 20]
        default_dist_range = [0, 10]

        #   Find suitable plot ranges
        xs_list = list(itertools.chain.from_iterable(xs))
        max_xs = np.max(xs_list)
        min_xs = np.min(xs_list)

        ys_list = list(itertools.chain.from_iterable(ys))
        max_ys = np.max(ys_list)
        min_ys = np.min(ys_list)

        dist_list = list(itertools.chain.from_iterable(zs))
        max_zs = np.max(dist_list)
        min_zs = np.min(dist_list)

        #   Set range: defaults or values from above
        if default_pm_range[0] < min_xs:
            x_min = min_xs
        else:
            x_min = default_pm_range[0]
        if default_pm_range[1] > min_xs:
            x_max = max_xs
        else:
            x_max = default_pm_range[1]
        if default_pm_range[0] < min_ys:
            y_min = min_ys
        else:
            y_min = default_pm_range[0]
        if default_pm_range[1] > min_ys:
            y_max = max_ys
        else:
            y_max = default_pm_range[1]
        if default_dist_range[0] < min_zs:
            z_min = min_zs
        else:
            z_min = default_dist_range[0]
        if default_dist_range[1] > min_zs:
            z_max = max_zs
        else:
            z_max = default_dist_range[1]

        ax.set_xlim([x_min, x_max])
        ax.set_ylim([y_min, y_max])
        ax.set_zlim([z_min, z_max])

        #   Plot data
        if color is None:
            for j, x in enumerate(xs):
                ax.scatter3D(
                    x,
                    ys[j],
                    zs[j],
                    # c=zs[i],
                    cmap='cividis',
                    # cmap='tab20',
                    label=f'Cluster {j}',
                    # picker=True,
                    picker=5,
                )
                ax.legend()
        else:
            for j, x in enumerate(xs):
                ax.scatter3D(
                    x,
                    ys[j],
                    zs[j],
                    c=color[j],
                    cmap='cividis',
                    # cmap='tab20',
                    label=f'Cluster {j}',
                )
                ax.legend()

    # fig.canvas.mpl_connect('pick_event', onpick3)
    # fig.canvas.mpl_connect('button_press_event',click_point)

    #   Display plot and switch backend back to default
    if display:
        plt.show()
        # plt.show(block=False)
        # time.sleep(300)
        # print('after sleep')
        plt.close()
        plt.switch_backend('Agg')
    else:
        #   Save image if it is not displayed directly
        plt.savefig(
            f'{output_dir}/compare/pm_vs_distance.{file_type}',
            bbox_inches='tight',
            format=file_type,
        )
        plt.close()


def scatter(
        x_values: list[np.ndarray], name_x: str, y_values: list[np.ndarray],
        name_y: str, rts: str, output_dir: str,
        x_errors: list[np.ndarray | None] = [None],
        y_errors: list[np.ndarray | None] = [None],
        dataset_label: list[str] | None = None, name_object: str | None = None,
        fits: list[fitting] | None = None, one_to_one: bool = False,
        file_type: str = 'pdf') -> None:
    """
    Plot magnitudes

    Parameters
    ----------
    x_values
        List of arrays with X values

    name_x
        Name of quantity 1

    y_values
        List of arrays with Y values

    name_y
        Name of quantity 2

    rts
        Expression characterizing the plot

    output_dir
        Output directory

    x_errors
        Errors for the X values
        Default is ``None``.

    y_errors
        Errors for the Y values
        Default is ``None``.

    dataset_label
        Label for the datasets
        Default is ``None``.

    name_object
        Name of the object
        Default is ``None``

    fits
        List of objects, representing fits to the data
        Default is ``None``.

    one_to_one
        If True a 1:1 line will be plotted.
        Default is ``False``.

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'scatter'),
    )

    #   Plot magnitudes
    fig = plt.figure(figsize=(8, 8))

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title
    if name_object is None:
        sub_title = f'{name_x} vs. {name_y}'
    else:
        sub_title = f'{name_x} vs. {name_y} ({name_object})'
    fig.suptitle(
        sub_title,
        fontsize=17,
    )

    #   Initialize color cyclers
    color_cycler_symbols = mk_color_cycler_symbols()
    color_cycler_error_bars = mk_color_cycler_error_bars()

    #   Prepare cycler for the line styles
    line_cycler = mk_line_cycler()

    #   Plot data
    for i, x in enumerate(x_values):
        if dataset_label is None:
            dataset_label_i = ''
        else:
            dataset_label_i = dataset_label[i]
        plt.errorbar(
            x,
            y_values[i],
            xerr=x_errors[i],
            yerr=y_errors[i],
            marker='o',
            ls='none',
            markersize=3,
            capsize=2,
            color=next(color_cycler_symbols),
            ecolor=next(color_cycler_error_bars),
            elinewidth=1,
            label=f'{dataset_label_i}'
        )

        #   Plot fit
        if fits is not None:
            if fits[i] is not None:
                x_sort = np.sort(x)
                plt.plot(
                    x_sort,
                    fits[i](x_sort),
                    color='darkorange',
                    linestyle=next(line_cycler),
                    linewidth=1,
                    label=f'Fit to dataset {dataset_label_i}',
                )

    #   Add legend
    if dataset_label is not None:
        plt.legend()

    #   Add grid
    plt.grid(True, color='lightgray', linestyle='--', alpha=0.3)

    #   Plot the 1:1 line
    if one_to_one:
        x_min = np.amin(x_values)
        x_max = np.amax(x_values)
        y_min = np.amin(y_values)
        y_max = np.amax(y_values)
        max_plot = np.max([x_max, y_max])
        min_plot = np.min([x_min, y_min])

        plt.plot(
            [min_plot, max_plot],
            [min_plot, max_plot],
            color='black',
            lw=2,
        )

    #   Set x and y axis label
    plt.ylabel(name_y)
    plt.xlabel(name_x)

    #   Save plot
    plt.savefig(
        f'{output_dir}/scatter/{rts}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()


def plot_limiting_mag_sky_apertures(
        output_dir: str, img_data: np.ndarray, mask: np.ndarray,
        image_depth: ImageDepth, file_type: str = 'pdf') -> None:
    """
    Plot the sky apertures that are used to estimate the limiting magnitude

    Parameters
    ----------
    output_dir
        Output directory

    img_data
        Image data

    mask
        Indicating the position of detected objects

    image_depth
        Object used to derive the limiting magnitude

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'limiting_mag'),
    )

    #   Plot magnitudes
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9, 3))

    #   Set title
    ax[0].set_title('Data with blank apertures')
    ax[1].set_title('Mask with blank apertures')

    #   Normalize the image data and plot
    norm = ImageNormalize(img_data, interval=ZScaleInterval(contrast=0.15, ))
    ax[0].imshow(
        img_data,
        norm=norm,
        cmap='PuBu',
        interpolation='nearest',
        origin='lower',
    )

    #   Plot mask with object positions
    ax[1].imshow(
        mask,
        interpolation='none',
        origin='lower',
    )

    #   Plot apertures used to derive limiting magnitude
    image_depth.apertures[0].plot(ax[0], color='purple', lw=0.2)
    image_depth.apertures[0].plot(ax[1], color='orange', lw=0.2)

    plt.subplots_adjust(
        left=0.05,
        right=0.98,
        bottom=0.05,
        top=0.95,
        wspace=0.2,
    )

    #   Set labels
    label_font_size = 10
    ax[0].set_xlabel("[pixel]", fontsize=label_font_size)
    ax[0].set_ylabel("[pixel]", fontsize=label_font_size)
    ax[1].set_xlabel("[pixel]", fontsize=label_font_size)
    ax[1].set_ylabel("[pixel]", fontsize=label_font_size)

    #   Save plot
    plt.savefig(
        f'{output_dir}/limiting_mag/limiting_mag_sky_regions.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()


def extinction_curves(rv: float) -> None:
    """
    Plots extinction curves
    Currently only Fitzpatrick (without most of the UV range) is supported

    Parameters
    ----------
    rv
    Ration of absolute to relative extinction: AV/E(B-V)
    """
    #   Get Fitzpatrick law
    fitzpatrick_extinction_curve = calibration_parameters.fitzpatrick_extinction_curve(rv)

    #   Get x (1/lambda) range
    x = np.arange(0, 4, 0.1)

    #   Plot dimension
    fig = plt.figure(figsize=(8, 8))

    #   Set title
    fig.suptitle(
        "Extinction curves",
        fontsize=17,
    )

    plt.plot(
        x,
        fitzpatrick_extinction_curve(x),
        color='darkorange',
        linewidth=1,
        label=r'Fitzpatrick: $R_\mathrm{V} = $' + f'{rv}',
    )

    #   Set x and y-axis label and legend
    plt.xlabel(r'1/$\lambda$ ($\mu\mathrm{m}^{-1}$)', fontsize=16)
    plt.ylabel(r'A($\lambda$)/E(B-V)', fontsize=16)
    plt.legend()

    #   Add grid
    plt.grid(True, color='lightgray', linestyle='--', alpha=0.3)

    plt.show()
    plt.close()


def filled_iso_contours(
        object_table: Table, shape_image: tuple[int, int], filter_: str,
        output_dir: str = './', fraction_bright_objects_to_use: float = 0.2,
        spacing_grid_positions: int = 20, object_property: str = 'fwhm',
        file_type: str = 'pdf') -> None:
    """
    Filled iso contour surfaces

    Parameter
    ---------
    object_table
        Table with object positions (XY) in Pixel

    shape_image
        Dimension of the input image

    filter_
        Filter name

    output_dir
        Path to the directory where the master files should be saved to
        Default is ``.``.

    fraction_bright_objects_to_use
        Fraction of bright objects to use for iso contour determination
        Default is ``0.2``

    spacing_grid_positions
        Spacing between grid positions, usually in Pixel.
        Default is ``20``

    object_property
        Property of the objects used to derive the iso contour levels
        Default is ``fwhm``

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Limit object table to the most
    n_sources = len(object_table)
    object_table.sort('flux', reverse=True)
    object_table = object_table[0:int(n_sources * fraction_bright_objects_to_use)]

    #   Define positions and apertures
    xy_object_position = np.transpose(
        (object_table['ycentroid'], object_table['xcentroid'])
    )

    #   Set up mesh and define grid positions
    x, y = np.meshgrid(
        np.arange(0, shape_image[1], spacing_grid_positions),
        np.arange(0, shape_image[0], spacing_grid_positions)
    )
    xy_grid_shape = x.shape
    xy_grid_positions = np.array([y.ravel(), x.ravel()]).T

    #   Find matches between object and grid positions and assign z values
    object_tree = KDTree(xy_object_position, leafsize=100)
    _, nearst_neighbour_indexes = object_tree.query(xy_grid_positions, k=1)

    if object_property in object_table.colnames:
        z = object_table[object_property].value[nearst_neighbour_indexes]
    else:
        terminal_output.print_to_terminal(
            f'{object_property} is not available. Try roundness instead.',
        )
        if 'roundness' in object_table.colnames:
            z = object_table['roundness'].value[nearst_neighbour_indexes]
            object_property = 'roundness'
        elif 'roundness1' in object_table.colnames:
            z = object_table['roundness1'].value[nearst_neighbour_indexes]
            object_property = 'roundness1'
        else:
            raise RuntimeError('Roundness is also not available.')
    z = z.reshape(xy_grid_shape)

    #   Setup plot
    fig, ax = plt.subplots(figsize=(20, 20))

    #   Plot contours
    cs = ax.contourf(x, y, z)
    ax.contour(
        cs,
        colors='k',
        origin='lower',
    )
    ax.set_title(object_property.upper())

    #   Add color bar
    fig.colorbar(cs)

    # Plot grid
    ax.grid(c='k', ls='-', alpha=0.3)

    #   Save plot
    plt.savefig(
        f'{output_dir}/aberration/aberration_iso_contours_{filter_}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()
    # plt.show()


def histogram_statistic(
        parameter_list_0: list[np.ndarray], name_x: str, name_y: str, rts: str,
        output_dir: str, dataset_label: list[list[str]] | None = None,
        name_object: str = None, parameter_list_1: list[np.ndarray] = None,
        file_type: str = 'pdf',
    ) -> None:
    """
    Plots histogram statistics on properties such as the zero point

    Parameters
    ----------
    parameter_list_0
        List of arrays with parameters to plot

    name_x
        Name of quantity 1

    name_y
        Name of quantity 2

    rts
        Expression characterizing the plot

    output_dir
        Output directory

    dataset_label
        Label for the datasets
        Default is ``None``.

    name_object
        Name of the object
        Default is ``None``

    parameter_list_1
        Second list of arrays with parameters to plot such as sigma
        clipped values of parameter_list_0
        Default is ``None``

    file_type
        Type of plot file to be created
        Default is ``pdf``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'calibration'),
    )

    #   Plot magnitudes
    fig = plt.figure(figsize=(8, 8))

    #   Limit the space for the object names in case several are given
    if isinstance(name_object, list):
        name_object = ', '.join(name_object)
        if len(name_object) > 20:
            name_object = name_object[0:16] + ' ...'

    #   Set title
    if name_object is None:
        sub_title = f'{name_x} histogram'
    else:
        sub_title = f'{name_x} histogram ({name_object})'
    fig.suptitle(
        sub_title,
        fontsize=17,
    )

    #   Make color map
    color_pick = mk_colormap(len(parameter_list_0))

    for i, parameter in enumerate(parameter_list_0):
        plt.hist(
            parameter,
            bins=40,
            alpha=0.25,
            color=color_pick.to_rgba(i),
            label=f'{dataset_label[0][i]}',
        )
        median_parameter = np.ma.median(parameter)
        if isinstance(median_parameter, u.quantity.Quantity):
            median_parameter = median_parameter.value
        plt.axvline(
            median_parameter,
            # color='g',
            color=color_pick.to_rgba(i),
        )

    if parameter_list_1 is not None:
        for i, parameter in enumerate(parameter_list_1):
            plt.hist(
                parameter,
                bins=10,
                alpha=0.5,
                color=color_pick.to_rgba(i),
                label=f'{dataset_label[1][i]}',
            )

            median_parameter = np.ma.median(parameter)
            if isinstance(median_parameter, u.quantity.Quantity):
                median_parameter = median_parameter.value
            plt.axvline(
                median_parameter,
                color=color_pick.to_rgba(i),
            )

    #   Add legend
    if dataset_label is not None:
        plt.legend()

    #   Set x and y axis label
    plt.ylabel(name_y)
    plt.xlabel(name_x)

    #   Save plot
    plt.savefig(
        f'{output_dir}/calibration/{rts}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()


def plot_annotated_image(
        image_data: np.ndarray, wcs_image: wcs.WCS, simbad_objects: Table,
        output_dir: Path, filter_: str, file_type: str = 'pdf',
        filter_mag: str | None = None, mag_limit: float | None = None,
    ) -> None :
    """
    Visualises the image and marks objects from the Simbad database.

    Parameters
    ----------
    image_data
        2D image data

    wcs_image
        WCS object

    simbad_objects
        Table with Simbad objects

    output_dir
        Output directory

    filter_
        Filter identifier

    file_type
        Type of plot file to be created
        Default is ``pdf``.

    filter_mag
        Name of the filter (e.g. 'V')
        Default is ``None``.

    mag_limit
        Limiting magnitude, only objects brighter as this limit will be shown
        Default is ``None``.
    """
    #   Check output directories
    checks.check_output_directories(
        output_dir,
        os.path.join(output_dir, 'starmaps'),
    )

    #   Setup figure
    fig, ax = plt.subplots(figsize=(20, 9), subplot_kw={'projection': wcs_image})

    #   Set up normalization for the image
    norm = ImageNormalize(image_data, interval=ZScaleInterval(contrast=0.1, ))

    #   Display the actual image
    ax.imshow(
        image_data,
        cmap='gray',
        origin='lower',
        norm=norm,
        interpolation='nearest',
    )

    #   Define the ticks
    ax.tick_params(
        axis='both',
        which='both',
        direction='in',
    )
    ax.minorticks_on()

    #   Set labels
    ax.set_xlabel("Right ascension", fontsize=16)
    ax.set_ylabel("Declination", fontsize=16)

    #   Enable grid for WCS
    # if wcs is not None:
    ax.grid(True, color='white', linestyle='--')

    #   Setup list for legend
    legend_elements = []

    for obj in simbad_objects:
        if 'ra' in obj.colnames:
           simbad_objects.rename_column('ra', 'RA')
        if 'dec' in obj.colnames:
            simbad_objects.rename_column('dec', 'DEC')
        if 'otype' in obj.colnames:
            simbad_objects.rename_column('otype', 'OTYPE')
        if 'main_id' in obj.colnames:
            simbad_objects.rename_column('main_id', 'MAIN_ID')

        ra, dec = obj['RA'], obj['DEC']
        obj_type = obj['OTYPE']
        name = obj['MAIN_ID']

        #   Check that the magnitude is available and meets the filter
        #   and magnitude limit conditions
        if filter_mag and mag_limit is not None:
            mag_col = f'FLUX_{filter_mag.upper()}'
            if (mag_col not in obj.colnames or obj[mag_col] is None or
                    isinstance(obj[mag_col], np.ma.core.MaskedConstant) or obj[mag_col] > mag_limit):
                continue

        #   Conversion of world coordinates to image coordinates
        coord = SkyCoord(ra=ra, dec=dec, unit=("hourangle", "deg"))
        x, y = wcs_image.world_to_pixel(coord)

        #   Check if the objects are actually within the image boundaries
        if 0 <= x < image_data.shape[1] and 0 <= y < image_data.shape[0]:
            # print(obj_type)
            #   Select icon and colour based on the object type
            plot_marker = False
            if 'Star' in obj_type:
                color, marker = 'lightblue', '*'
                plot_marker = True

                if not any(e.get_label() == 'Star' for e in legend_elements):
                    legend_elements.append(
                        plt.Line2D(
                            [0],
                            [0],
                            color=color,
                            marker=marker,
                            markerfacecolor='none',
                            markersize=8,
                            linestyle='None',
                            label='Star',
                        )
                    )


            elif obj_type in ['Galaxy', 'Seyfert1', 'Seyfert2', 'AGN_Candidate', 'QSO']:
                color = 'lightsalmon'
                #   Test if object dimension is available
                if 'DIMENSIONS' in obj.colnames and obj['DIMENSIONS'] is not None:
                    dimensions = obj['DIMENSIONS']
                    # print(dimensions)
                    try:
                        major_axis, minor_axis = [float(dim) for dim in dimensions.split('x')]
                        #   TODO: Check if rotation information is available
                        angle = 0

                        #   Convert arc minute to pixel
                        major_axis_px = (major_axis / 60.0) / wcs.wcs.cdelt[0]
                        minor_axis_px = (minor_axis / 60.0) / wcs.wcs.cdelt[1]

                        #   Draw ellipse
                        ellipse = Ellipse(
                            (x, y),
                            width=major_axis_px,
                            height=minor_axis_px,
                            angle=angle,
                            edgecolor=color,
                            facecolor='none',
                            lw=1.5,
                            alpha=0.7,
                        )
                        ax.add_patch(ellipse)
                    except ValueError:
                        pass
                else:
                    #   No dimension tag -> set default marker
                    marker = 's'
                    plot_marker = True

                if not any(e.get_label() == 'Galaxy' for e in legend_elements):
                    legend_elements.append(
                        plt.Line2D(
                            [0],
                            [0],
                            color=color,
                            marker=marker,
                            markerfacecolor='none',
                            markersize=8,
                            linestyle='None',
                            label='Galaxy',
                        )
                    )

            elif 'Nebula' in obj_type:
                color, marker = 'lightpink', 'o'
                plot_marker = True

                if not any(e.get_label() == 'Nebula' for e in legend_elements):
                    legend_elements.append(
                        plt.Line2D(
                            [0],
                            [0],
                            color=color,
                            marker=marker,
                            markerfacecolor='none',
                            markersize=8,
                            linestyle='None',
                            label='Nebula',
                        )
                    )

            else:
                color, marker = 'lightgreen', 'H'
                plot_marker = True
                name = f'{name} ({obj_type})'

                if not any(e.get_label() == 'Other' for e in legend_elements):
                    legend_elements.append(
                        plt.Line2D(
                            [0],
                            [0],
                            color=color,
                            marker=marker,
                            markerfacecolor='none',
                            markersize=8,
                            linestyle='None',
                            label='Other',
                        )
                    )

            #   Mark objects
            if plot_marker:
                ax.plot(
                    x,
                    y,
                    marker=marker,
                    markerfacecolor='none',
                    markeredgecolor=color,
                    markeredgewidth=1.2,
                    markersize=11,
                    alpha=0.8,
                )
            ax.text(
                x + 70,
                y,
                name,
                color=color,
                fontsize=8,
                alpha=0.9,
                verticalalignment='center',
                weight="bold",
            )


    #   Add legend
    ax.legend(
        bbox_to_anchor=(0., 1.02, 1.0, 0.102),
        loc=3,
        handles=legend_elements,
        ncol=5,
        fontsize=8,
        frameon=True,
        mode='expand',
        borderaxespad=0.,
    )

    #   Save plot
    plt.savefig(
        output_dir / f'starmaps/annotated_starmap_{filter_}.{file_type}',
        bbox_inches='tight',
        format=file_type,
    )
    plt.close()
    # plt.show()
