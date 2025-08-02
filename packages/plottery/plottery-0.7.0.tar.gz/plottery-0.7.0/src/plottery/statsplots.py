from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import count
from matplotlib import cm, pyplot as plt
import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter
import six
import sys

if sys.version_info[0] == 2:
    range = xrange


def contour_levels(x, y=[], bins=10, levels=(0.68, 0.95)):
    """
    Get the contour levels corresponding to a set of percentiles (given
    as fraction of 1) for a 2d histogram. Used commonly to plot
    posterior distributions from MCMC samples.

    Parameters
    ----------
        x : array of floats
            if y is given then x must be a 1d array. If y is not given then
            x should be a 2d array
        y : array of floats (optional)
            1d array with the same number of elements as x
        bins : argument of np.histogram2d
        levels : list of floats between 0 and 1
            the fractional percentiles of the data that should be above the
            returned values

    Returns
    -------
        level_values : list of floats, same length as *levels*
            The values of the histogram above which the fractional percentiles
            of the data given by *levels* are

    """
    if len(y) > 0:
        if len(x) != len(y):
            msg = "Invalid input for arrays; must be either 1 2d array"
            msg += " or 2 1d arrays"
            raise ValueError(msg)
    else:
        if len(np.array(x).shape) != 2:
            msg = "Invalid input for arrays; must be either 1 2d array"
            msg += " or 2 1d arrays"
            raise ValueError(msg)

    def findlevel(lo, hist, level):
        return 1.0 * hist[hist >= lo].sum() / hist.sum() - level

    if len(x) == len(y):
        hist, xedges, yedges = np.histogram2d(x, y, bins=bins)
        hist = np.transpose(hist)
        extent = (xedges[0], xedges[-1], yedges[0], yedges[-1])
    elif len(y) == 0:
        hist = np.array(x)
    level_values = [
        optimize.bisect(findlevel, hist.min(), hist.max(), args=(hist, l))
        for l in levels
    ]
    return level_values


def corner(
    X,
    config=None,
    names="",
    labels=None,
    bins=20,
    bins1d=20,
    clevels=(0.68, 0.95),
    contour_reference="samples",
    blind=False,
    truths=None,
    truths_in_1d=False,
    truth_color="r",
    smooth=False,
    lnlike=None,
    likesmooth=1,
    color_likelihood="r",
    colors="k",
    cmap=None,
    ls1d="-",
    ls2d="solid",
    style1d="curve",
    medians1d=True,
    percentiles1d=True,
    background=None,
    bweight=None,
    bcolor="r",
    vmin=0,
    vmax=1,
    alpha=0.5,
    limits=None,
    show_likelihood_1d=True,
    ticks=None,
    show_contour=True,
    top_labels=False,
    pad=1,
    h_pad=0.1,
    w_pad=0.02,
    output="",
    verbose=False,
    names_kwargs={},
    contour_kwargs={},
):
    """
    Do a corner plot (e.g., with the posterior parameters of an MCMC chain).
    Note that there may still be some issues with the tick labels.

    Parameters
    ----------
      X         : array-like
                  all posterior parameters. Can also be the outputs of
                  more than one chain, given as an array of arrays of models.
                  For instance, the example has three chains with two
                  parameters. In this case, X = [[A1,B1], [A2,B2], [A3,B3]].

    Optional parameters
    -------------------
      names     : list of strings
                  Names for each of the chains. Will be used to show a legend
                  in the (empty) upper corner
      labels    : list of strings
                  names of the parameters
      bins      : int or array of ints
                  Number of bins for the contours in the off-diagonal panels.
                  Should be one value per chain, one value per parameter,
                  or have shape (nchains,nparams)
      bins1d    : int or array of ints
                  Number of bins for the histograms or curves in the diagonal
                  panels. Should be one value per chain, one value per
                  parameter, or have shape (nchains,nparams)
      clevels   : list of floats between 0 and 1
                  percentiles at which to show contours
      contour_reference : ('samples', 'chi2')
                  whether to draw contour on fractions of samples or
                  on likelihood levels. In the former case, *clevels*
                  must be floats between 0 and 1; in the latter, the
                  levels of the chi2. ONLY 'samples' IMPLEMENTED SO FAR
      blind     : bool
                  if ``True``, all tick labels will be hidden
      truths    : one of {list of floats, 'medians', None}
                  reference values for each parameter, to be shown in
                  each panel
      smooth    : float
                  the width of the gaussian with which to smooth the
                  contours in the off-diagonal panels. If no value is given,
                  the contours are not smoothed.
      lnlike    : array of floats
                  the likelihood surface, to be shown as a histogram in the
                  diagonals or to be used to define the 2d contours. If
                  contour_reference=='chi2' then provide the chi2 here
                  instead of the likelihood
      show_likelihood_1d : bool
                  whether to show the likelihood in the diagonal panels
      likesmooth : int
                  the number of maxima to average over to show the
                  likelihood surface
      colors    : any argument taken by the *colors* argument of
                  plt.contour(), or a tuple of them if more than one
                  model is to be plotted
      ls1d      : ('solid', 'dashed', 'dashdot', 'dotted')
                  linestyle for the diagonal plots, if style1d=='curve'.
                  Can specify more than one value as a list if more than one
                  model is being plotted.
      ls2d      : ('solid', 'dashed', 'dashdot', 'dotted')
                  linestyle for the contours. Can specify more than one value
                  as a list if more than one model is being plotted.
      style1d   : ('bar', 'step', 'stepfilled', 'curve', 'smooth')
                  if 'curve' or 'smooth', plot the 1d posterior as a
                  curve; else this parameter is passed to the 'histtype'
                  argument in pyplot.hist()
      medians1d : bool
                  whether to show the medians in the diagonal panels as
                  vertical lines
      percentiles1d : bool
                  whether to show selected percentiles (see *clevels*) in the
                  diagonal panels as vertical lines
      background : (None, 'points', 'density', 'logdensity', 'filled')
                  If not None, then either points, a smoothed 2d histogram,
                  or filled contours are plotted beneath contours.
      bweight   : array-like, same length as e.g., A1
                  values to color-code background points
      bcolor    : color property, consistent with *background*
                  color of the points or filled contours, or colormap of the
                  2d density background.
      vmin, vmax : colormap limits. NOT YET IMPLEMENTED
      alpha     : float between 0 and 1
                  transparency of the points if shown
      limits    : list of length-2 lists
                  a list of plot limits for each of the parameters.
      ticks     : list of lists
                  a list of tick positions for each parameter, to be printed
                  both in the x and y axes as appropriate.
      top_labels : bool
                  whether to show axis and tick labels at the top of each
                  diagonal plot
      pad       : float
                  blank space outside axes (passed to tight_layout)
      output    : string
                  filename to save the plot.
      verbose   : boolean
                  whether to print the marginalized values per variable
      names_kwargs : dictionary
                  keyword arguments controlling the location and style
                  of the legend containing model names; passed to
                  plt.legend(). The default settings are:
                      * 'loc': 'upper right'
                      * 'frameon': False
                      * 'bbox_to_anchor': (0.95,0.95)
                      * 'bbox_transform': plt.gcf().transFigure
      contour_kwargs : keyword arguments to be passed to ``plt.contourf``
                  (if background=="filled") or ``plt.contour``


    Returns
    -------
      fig, axes_diagonal, axes_off : pylab figure and axes (diagonal and
                  off-diagonal) instances

    """
    # not yet implemented
    # options = _load_corner_config(config)
    nchains = len(X) if _depth(X) > 2 else 1
    if nchains > 1:
        ndim = len(X[0])
        nsamples = len(X[0][0])
        if background == "points":
            background = None
    else:
        ndim = len(X)
        nsamples = len(X[0])
        X = (X,)
    if nsamples == 0:
        msg = "plottools.corner: received empty array."
        msg += " It is possible that you set the burn-in to be longer"
        msg += " than the chain itself!"
        raise ValueError(msg)
    # check ticks
    if ticks is not None:
        if len(ticks) != ndim:
            print(
                "WARNING: number of tick lists does not match" " number of parameters"
            )
            ticks = None
    # check limits
    if limits is not None:
        if len(limits) != ndim:
            print(
                "WARNING: number of limit lists does not match" " number of parameters"
            )
            limits = None
    # check likelihood
    if lnlike is not None and show_likelihood_1d:
        if _depth(lnlike) == 1:
            lnlike = np.squeeze(lnlike)[None]
        else:
            assert len(lnlike) == nchains
    # what to show in the off-diagonals
    assert contour_reference in (None, "likelihood", "samples")

    # check clevels - they should be fractions between 0 and 1 for
    # contour_reference == 'samples'.
    # if contour_reference != 'samples':
    # msg = 'ERROR: only "samples" option implemented for'
    # msg += ' contour_reference. Setting contour_reference="samples"'
    # print(msg)
    # contour_reference = 'samples'
    if contour_reference == "samples":
        if 1 < max(clevels) <= 100:
            clevels = [cl / 100.0 for cl in clevels]
        elif max(clevels) > 100:
            msg = "ERROR: contour levels must be between 0 and 1 or between"
            msg += " 0 and 100"
            print(msg)
            exit()
    # check truths
    if truths is not None:
        if len(truths) != ndim:
            msg = "WARNING: number of truth values does not match number"
            msg += " of parameters"
            print(msg)
            truths = None
    try:
        if len(smooth) != len(X[0]):
            print(
                "WARNING: number of smoothing widths must be equal to"
                " number of parameters"
            )
            smooth = [0 for i in X[0]]
    except TypeError:
        if smooth not in (False, None):
            smooth = [smooth for i in X[0]]
    bins, bins1d = _binning(bins, bins1d, nchains, ndim, limits)
    if len(X) == 1:
        if isinstance(colors, six.string_types):
            color1d = colors
        else:
            color1d = "k"
    else:
        if len(colors) == len(X):
            color1d = colors
        # supports up to 10 names (plot would be way overcrowded!)
        else:
            color1d = ["C{0}".format(i) for i in range(10)]
    if isinstance(ls1d, six.string_types):
        ls1d = [ls1d for i in X]
    if isinstance(ls2d, six.string_types):
        ls2d = [ls2d for i in X]
    # to move the model legend around
    names_kwargs_defaults = {
        "loc": "center",
        "frameon": False,
        "bbox_to_anchor": (0.95, 0.95),
        "bbox_transform": plt.gcf().transFigure,
    }
    for key in names_kwargs_defaults:
        if key not in names_kwargs:
            names_kwargs[key] = names_kwargs_defaults[key]
    # all set!
    axvls = ("--", ":", "-.")
    fig, axes = plt.subplots(
        ndim, ndim, figsize=(2 * ndim + 1, 2 * ndim + 1)
    )  # , sharex=True, sharey=True)

    # diagonals
    plot_ranges = []
    axes_diagonal = []
    # to generate model legend
    model_lines = []
    # for backward compatibility
    histtype = style1d.replace("hist", "step")
    for i in range(ndim):
        ax = axes[i][i]
        axes_diagonal.append(ax)
        peak = 0
        edges = []
        for m, Xm in enumerate(X):
            if limits is None:
                Xm_i = Xm[i]
            else:
                mask = (Xm[i] >= limits[i][0]) & (Xm[i] <= limits[i][1])
                Xm_i = Xm[i][mask]
            xlim = (Xm_i.min(), Xm_i.max())
            edges.append([])
            if style1d in ("curve", "smooth"):
                ho, e = np.histogram(Xm_i, bins=bins1d[m][i])
                xo = 0.5 * (e[1:] + e[:-1])
                kind = "slinear" if style1d == "curve" else "cubic"
                fx = interp1d(xo, xlim[0] + (xlim[1] - xlim[0]) * ho, kind=kind)
                xn = np.linspace(xo.min(), xo.max(), 500)
                n = fx(xn)
                (line,) = ax.plot(xn, n, ls=ls1d[m], color=color1d[m])
                if i == 0:
                    model_lines.append(line)
            else:
                n, e, patches = ax.hist(
                    Xm_i,
                    bins=bins1d[m][i],
                    histtype=histtype,
                    color=color1d[m],
                    density=True,
                )  # weights=np.ones(Xm_i.size)/Xm_i.sum())
            edges[-1].append(e)
            if n.max() > peak:
                peak = n.max()
            area = n.sum()
            if medians1d:
                ax.axvline(np.median(Xm_i), ls="-", color=color1d[m])
            if verbose:
                if len(names) == len(X):
                    print(f"names[{m}] = {names[m]}")
                if labels is not None:
                    print(f"  {labels[i]}", end=" ")
                    if truths is None:
                        print("")
                    else:
                        print(f"(truth: {truths[i]})")
                    print(f"    p50.0  {np.median(Xm_i):.3f}")
            for p, ls in zip(clevels, axvls):
                v = [
                    np.percentile(Xm_i, 100 * (1 - p) / 2.0),
                    np.percentile(Xm_i, 100 * (1 + p) / 2.0),
                ]
                if percentiles1d:
                    ax.axvline(v[0], ls=ls, color=color1d[m])
                    ax.axvline(v[1], ls=ls, color=color1d[m])
                if verbose:
                    print(f"    p{100*p:.1f} {v[0]:.3f}  {v[1]:.3f}")
        if lnlike is not None:
            for m, Xm, Lm, e in zip(count(), X, lnlike, edges):
                binning = np.digitize(Xm_i, e[m])
                xo = 0.5 * (e[m][1:] + e[m][:-1])
                # there can be nan's because some bins have no data
                valid = np.array(
                    [(len(Lm[binning == ii]) > 0) for ii in range(1, len(e[m]))]
                )
                Lmbinned = [
                    np.median(np.sort(Lm[binning == ii + 1])[-likesmooth:])
                    for ii, L in enumerate(valid)
                    if L
                ]
                # normalized to the histogram area
                Lmbinned = np.exp(Lmbinned)
                Lmbinned -= Lmbinned.min()
                Lmbinned /= Lmbinned.max() / peak
                ax.plot(
                    xo[valid], Lmbinned, "-", color=color_likelihood, lw=1, zorder=-10
                )
        if truths_in_1d and truths is not None:
            ax.axvline(truths[i], ls="-", color=truth_color, zorder=10)
        if i == ndim - 1 and labels is not None:
            if len(labels) >= ndim:
                ax.set_xlabel(labels[i])
        ax.set_yticks([])
        if blind:
            ax.set(xticks=[], yticks=[])
        else:
            # to avoid overcrowding tick labels
            if ticks is None:
                tickloc = plt.MaxNLocator(3)
                ax.xaxis.set_major_locator(tickloc)
            else:
                ax.set_xticks(ticks[i])
            plt.xticks(rotation=45)
            ax.set_ylim(0, 1.1 * peak)
            if i != ndim - 1:
                ax.set_xticklabels([])
        if top_labels:
            topax = ax.twiny()
            topax.set_xlim(*ax.get_xlim())
            topax.xaxis.set_major_locator(tickloc)
            topax.set_xlabel(labels[i])
        plot_ranges.append(ax.get_xlim())

    # lower off-diagonals
    axes_off = []
    # vertical axes
    for i in range(1, ndim):
        # empty axes at the top-right
        axes[0][i].axis("off")
        for j in range(i + 1, ndim):
            axes[i][j].axis("off")
        # horizontal axes
        for j in range(i):
            ax = axes[i][j]
            axes_off.append(ax)
            extent = np.append(plot_ranges[j], plot_ranges[i])
            for m, Xm in enumerate(X):
                if limits is not None:
                    mask_ij = (
                        (Xm[j] >= limits[j][0])
                        & (Xm[j] <= limits[j][1])
                        & (Xm[i] >= limits[i][0])
                        & (Xm[i] <= limits[i][1])
                    )
                    Xm_i = Xm[i][mask_ij]
                    Xm_j = Xm[j][mask_ij]
                else:
                    Xm_i = Xm[i]
                    Xm_j = Xm[j]
                if contour_reference == "likelihood":
                    ax.contour(
                        Xm_j,
                        Xm_i,
                        lnlike,
                        levels=clevels,
                        linewidths=1,
                        **contour_kwargs,
                    )
                elif contour_reference == "samples":
                    h = np.histogram2d(Xm_j, Xm_i, bins=bins[m][i])
                    h, xe, ye = np.histogram2d(Xm_j, Xm_i, bins=bins[m][i])
                    h = h.T
                    extent = (xe[0], xe[-1], ye[0], ye[-1])
                    if smooth not in (False, None):
                        h = gaussian_filter(h, (smooth[i], smooth[j]))
                    levels = contour_levels(Xm_j, Xm_i, bins=bins[m][i], levels=clevels)
                if background is None:
                    pass
                elif background == "points":
                    if not (cmap is None or bweight is None):
                        ax.scatter(
                            Xm_j,
                            Xm_i,
                            c=bweight,
                            marker=".",
                            s=4,
                            lw=0,
                            cmap=cmap,
                            zorder=-10,
                        )
                    else:
                        ax.plot(Xm_j, Xm_i, ",", color=bcolor, alpha=alpha, zorder=-10)
                elif background.endswith("density"):
                    h2d, xe, ye = np.histogram2d(Xm_i, Xm_j, bins=bins[m][i])
                    if background == "logdensity":
                        h2d = np.log10(h2d)
                    else:
                        h2d[h2d == 0] = np.nan
                    ax.imshow(
                        h2d, origin="lower", cmap=bcolor, extent=extent, aspect="auto"
                    )
                elif background == "filled":
                    lvs = contour_levels(Xm_j, Xm_i, bins=bins[m][i], levels=clevels)
                    lvs = np.append(lvs[::-1], h.max())
                    # what's this supposed to test?
                    try:
                        if not isinstance(bcolor[0], str) and hasattr(
                            bcolor[0], "__iter__"
                        ):
                            bcolor = [bc for bc in bcolor]
                    except TypeError:
                        pass
                    if cmap is not None:
                        cmap = plt.get_cmap(cmap)
                        c = np.linspace(vmin, vmax, lvs.size)
                        colors = cmap((c[:-1] + c[1:]) / 2)
                    else:
                        colors = bcolor[::-1]
                    ax.contourf(
                        h,
                        lvs,
                        extent=extent,
                        linestyles=ls2d[m],
                        colors=colors,
                        **contour_kwargs,
                    )
                if show_contour:  # and background != "filled":
                    ax.contour(
                        h,
                        levels[::-1],
                        colors=color1d[m],
                        linestyles=ls2d[m],
                        extent=extent,
                        zorder=10,
                        **contour_kwargs,
                    )
                if truths is not None:
                    ax.plot(
                        truths[j],
                        truths[i],
                        "+",
                        color=truth_color,
                        mew=4,
                        ms=12,
                        zorder=10,
                    )
            if labels is not None:
                if len(labels) == ndim:
                    if j == 0:
                        ax.set_ylabel(labels[i])
                    if i == ndim - 1:
                        ax.set_xlabel(labels[j])
            if blind:
                ax.set(xticks=[], yticks=[])
            else:
                if j > 0:
                    ax.set_yticklabels([])
                if i < ndim - 1:
                    ax.set_xticklabels([])
                # ax.set_xlim(*plot_ranges[j])
                # ax.set_ylim(*plot_ranges[i])
                if ticks is not None:
                    ax.set_xticks(ticks[j])
                    ax.set_yticks(ticks[i])
                else:
                    # to avoid overcrowding tick labels
                    ax.xaxis.set_major_locator(plt.MaxNLocator(3))
                    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
                for tick in ax.get_xticklabels():
                    tick.set_rotation(45)

    if limits is None:
        limits = [ax.get_xlim() for ax in axes[-1][:-1]] + [axes[-1][0].get_ylim()]
        for i, row in enumerate(axes):
            for j, ax in enumerate(row):
                ax.set_xlim(limits[j])
                if i != j:
                    ax.set_ylim(limits[i])

    if (len(X) == 1 and isinstance(names, six.string_types)) or (
        hasattr(names, "__iter__") and len(names) == len(X)
    ):
        fig.legend(model_lines, names, **names_kwargs)
    fig.tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad)
    if output:
        plt.savefig(output, format=output[-3:])
        plt.close()
    return fig, axes_diagonal, axes_off


def _binning(bins, bins1d, nchains, ndim, limits):
    # check the binning scheme.
    meta_bins = [bins, bins1d]
    for i, bname in enumerate(("bins", "bins1d")):
        bi = np.array(meta_bins[i])
        bidepth = _depth(bi)
        # will be the same message in all cases below
        msg = (
            f"{bname} must correspond either to the number"
            " of chains or number of parameters, or have shape"
            " (nchains,nparams)"
        )
        if bidepth > 2:
            raise ValueError(f"iterable too deep: {msg}")
        # this means binning will be the same for all chains
        ones = np.ones((nchains, ndim), dtype=int)
        # is it a scalar?
        if bidepth == 0:
            if isinstance(meta_bins[i], str):
                meta_bins[i] = nchains * [[meta_bins[i] for j in range(ndim)]]
            else:
                meta_bins[i] = bi.T * ones
        # or a 1d list?
        elif bidepth == 1:
            bi = np.array(bi)
            if len(bi) == ndim:
                meta_bins[i] = ones * bi
            elif len(bi) == nchains:
                meta_bins[i] = ones * bi[:, None]
            else:
                raise ValueError(msg)
        elif (
            bidepth == 2 and nchains > 1 and np.array(bi).shape != ones.shape
        ) or bidepth > 2:
            raise ValueError(msg)
    # adjusted to the required shape (and type)
    bins, bins1d = meta_bins
    return bins, bins1d


def _depth(L):
    """the depth of an array or list

    Useful to assess the proper format of arguments. Returns zero if
    scalar.
    """
    return len(np.array(L).shape)
