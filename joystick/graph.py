#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  
#  JOYSTICK - Real-time plotting and logging while console controlling
#  Copyright (C) 2016  Guillaume Schworer
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
#  For any information, bug report, idea, donation, hug, beer, please contact
#    guillaume.schworer@gmail.com
#
###############################################################################

from . import core
tkinter = core.tkinter
FigureCanvasTkAgg = core.mat.backends.backend_tkagg.FigureCanvasTkAgg
np = core.np
from .frame import Frame


__all__ = ['Graph']


class Graph(Frame):
    def __init__(self, name, freq_up=1, pos=(50, 50), size=(400, 400),
                 screen_relative=False, xnpts=30, fmt="ro-",
                 bgcol='w', axrect=(0.1, 0.1, 0.9, 0.9), grid='k',
                 xylim=(0., None, 0., None), xnptsmax=50, axmargin=(1.1, 1.1),
                 **kwargs):
        """
        Initialises a graph-frame. Use :py:func:`~joystick.graph.Graph.set_xydata` and
        :py:func:`~joystick.graphGraph.get_xydata` to set and get the x- and y-data of the
        graph, or :py:func:`~joystick.graphGraph.set_xylim` and :py:func:`~joystick.graphGraph.get_xylim` to
        get and set the axes limits.

        [Optional]
          * Create a custom method :py:data:`~joystick.core.INITMETHOD` to add to the
            initialization of the frame.
          * Create a custom method :py:data:`~joystick.core.UPDATEMETHOD` to add code at
            the updating of the frame.

        Args:
          * name (str): the frame name
          * freq_up (float or None): the frequency of update of the frame,
            between 1e-3 and 1e3 Hz, or ``None`` for no update
          * pos (px or %) [optional]: left-top corner position of the
            frame, see ``screen_relative``
          * size (px or %) [optional]: width-height dimension of the
            frame, see ``screen_relative``
          * screen_relative (bool) [optional]: set to ``True`` to give
            ``pos`` and ``size`` as a % of the screen size, or ``False``
            to give then as pixels
          * xnpts (int) [optional]: the number of data points to be plotted
          * fmt (str) [optional]: the format of the line as in
            ``plt.plot(x, y, fmt)``
          * bgcol (color) [optional]: the background color of the graph
          * axrect (list of 4 floats) [optional]: the axes bounds (l,b,w,h)
            as in ``plt.figure.add_axes(rect=(l,b,w,h))``
          * grid (color or None) [optional]: the grid color, or no grid if
            ``None``
          * xylim (list of 4 floats or None) [optional]: the values of the
            axes limits (xmin, xmax, ymin, ymax), where any value can take
            ``None`` to be recalculated according to the data at each update
          * xnptsmax (int) [optional]: the maximum number of data points to
            be recorded, older data points will be deleted
          * axmargin (tuple of 2 floats) [optional]: a expand factor to
            increase the (x, y) axes limits when they are automatically
            calculated from the data (i.e. some xylim is ``None``)

        Kwargs:
          * Any non-abbreviated parameter accepted by ``figure.add_axes``
            and ``plt.plot``
          * Will be passed to the optional custom methods
        """
        kwargs['name'] = name
        kwargs['freq_up'] = freq_up
        kwargs['pos'] = pos
        kwargs['size'] = size
        kwargs['screen_relative'] = screen_relative
        kwargs['xnpts'] = xnpts
        kwargs['fmt'] = fmt
        kwargs['bgcol'] = bgcol
        kwargs['axrect'] = axrect
        kwargs['grid'] = grid
        kwargs['xylim'] = xylim
        kwargs['xnptsmax'] = xnptsmax
        kwargs['axmargin'] = axmargin
        self._minmini = 1e-2
        self._kwargs = kwargs
        # call mummy init
        super(Graph, self).__init__(**self._kwargs)
        # call ya own init
        self._init_base(**self._kwargs)

    def _init_base(self, **kwargs):
        """
        Separate function from __init__ for re-initialization purpose
        """
        self.xnptsmax = int(kwargs.pop('xnptsmax'))
        self.xylim = tuple(kwargs.pop('xylim')[:4])
        self.axmargin = tuple(map(abs, kwargs.pop('axmargin')[:2]))
        self.xnpts = int(kwargs.pop('xnpts'))
        axrect = tuple(kwargs.pop('axrect')[:4])
        self._fig = core.mat.figure.Figure()
        self.ax = self._fig.add_axes(axrect[:2] + (axrect[2]-axrect[0],
                                                   axrect[3]-axrect[1]),
                                     **core.matkwargs(kwargs))
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._window)
        self._canvas.show()
        self._canvas.get_tk_widget().pack(side=tkinter.TOP,
                                          fill=tkinter.BOTH,
                                          expand=True)
        self._canvas._tkcanvas.pack(side=tkinter.TOP,
                                    fill=tkinter.BOTH,
                                    expand=True)
        self.ax.set_axis_bgcolor(kwargs.pop('bgcol'))
        grid = kwargs.pop('grid')
        if grid not in [None, False]:
            self.ax.grid(color=grid, lw=1)
        self.ax.plot(0, 0, kwargs.pop('fmt'), **core.matkwargs(kwargs))
        core.callit(self, core.PREUPDATEMETHOD)
        core.callit(self, core.INITMETHOD, **kwargs)

    def reinit(self, **kwargs):
        """
        Re-initializes the frame, i.e. closes the current frame if
        necessary and creates a new one. Uses the parameters of
        initialization by default or anything provided through kwargs.
        See class :py:class:`~joystick.graph.Graph` for the description of input parameters.
        """
        # updates with new reinit value if specified
        self._kwargs.update(kwargs)
        # call mummy reinit
        super(Graph, self).reinit(**self._kwargs)
        # ya own reinit
        self._init_base(**self._kwargs)

    def show(self):
        """
        Updates the graph
        """
        if self.visible:
            self._canvas.draw()

    @property
    def xnptsmax(self):
        """
        The maximum number of data points to be recorded, older data
        points will be deleted. Must be > 1.
        """
        return self._xnptsmax

    @xnptsmax.setter
    def xnptsmax(self, value):
        if value < 1:
            print("{}Invalid value. Must be > 1{}" \
            .format(core.font.red, core.font.normal))
            return
        self._xnptsmax = int(value)
    
    @property
    def xnpts(self):
        """
        The number of data points to be plotted. Must be
        1 < xnpts <= ``Graph.xnptsmax``.
        """
        return self._xnpts

    @xnpts.setter
    def xnpts(self, value):
        if not 1 < value <= self.xnptsmax:
            print("{}Invalid value. Must be 1--{}{}" \
            .format(core.font.red, self.xnptsmax, core.font.normal))
            return
        self._xnpts = int(value)

    def set_xydata(self, x, y):
        """
        Sets the x and y data of the graph.
        Give x and y vectors as numpy arrays; only the last
        ``Graph.xnpts`` data-points will be displayed
        """
        if self.visible:
            self.ax.lines[0].set_xdata(x[-self.xnpts:])
            self.ax.lines[0].set_ydata(y[-self.xnpts:])

    def get_xydata(self):
        """
        Returns the x and y data of the graph
        """
        if self.visible:
            return self.ax.lines[0].get_xdata(), self.ax.lines[0].get_ydata()

    def set_xylim(self, xylim=(None, None, None, None)):
        """
        Sets the (xmin, xmax, ymin, ymax) limits of the graph.
        Set one or several values to ``None`` to auto-adjust the limits
        of the graph to its x- or y-data.
        """
        if not self.visible:
            return
        xmin, xmax, ymin, ymax = xylim
        xmin_o, xmax_o, ymin_o, ymax_o = self.get_xylim()
        xmin = xmin_o if xmin is None else float(xmin)
        xmax = xmax_o if xmax is None else float(xmax)
        ymin = ymin_o if ymin is None else float(ymin)
        ymax = ymax_o if ymax is None else float(ymax)
        if not np.allclose([xmin, xmax], [xmin_o, xmax_o]):
            self.ax.set_xlim([xmin, xmax])
        if not np.allclose([ymin, ymax], [ymin_o, ymax_o]):
            self.ax.set_ylim([ymin, ymax])

    def get_xylim(self):
        """
        Returns the (xmin, xmax, ymin, ymax) limits of the graph
        """
        if self.visible:
            return self.ax.get_xlim() + self.ax.get_ylim()

    def _pre_update(self):
        """
        Does the axes scaling
        """
        x, y = self.get_xydata()
        # None means recalculate the bound
        xmin, xmax, ymin, ymax = self.xylim
        xmin_f = x.min() if xmin is None else xmin
        xmax_f = max(x.max(), xmin_f+self._minmini) if xmax is None else xmax
        ymin_f = y.min() if ymin is None else ymin
        ymax_f = max(y.max(), ymin_f+self._minmini) if ymax is None else ymax
        if self.axmargin[0] != 1.0:
            dx = (self.axmargin[0]-1)*(xmax_f-xmin_f)*0.5
            if xmin is None:
                xmin_f -= dx
            if xmax is None:
                xmax_f += dx
        if self.axmargin[1] != 1.0:
            dy = (self.axmargin[1]-1)*(ymax_f-ymin_f)*0.5
            if ymin is None:
                ymin_f -= dy
            if ymax is None:
                ymax_f += dy
        self.set_xylim((xmin_f, xmax_f, ymin_f, ymax_f))
