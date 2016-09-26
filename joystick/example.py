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


import joystick as jk
import numpy as np
import time

class test(jk.Joystick):
    _infinite_loop = jk.deco_infinite_loop()

    def _init(self, *args, **kwargs):
        """
        Function called at initialization, don't bother why for now
        """
        self._t0 = time.time()
        self.xdata = np.array([self._t0])
        self.ydata = np.array([0.0])
        self.mygraph = jk.Graph(daddy=self, name="test", size=(500, 500), pos=(50, 50), fmt="go-", xnpts=15, freq_up=7, bgcol="y")
        self.mytext = jk.Text(daddy=self, name="Y-overflow", size=(500, 250), pos=(600, 50), freq_up=1)

    @_infinite_loop(wait_time=0.2)
    def _generate_fake_data(self):
        """
        Function called at simulation start, getting data and pushing it to the graph every 0.2 seconds
        """
        self.xdata = jk.core.add_datapoint(self.xdata, time.time())
        self.ydata = jk.core.add_datapoint(self.ydata, np.random.random()*1.05)
        if self.ydata[-1] > 1:
            self.mytext.add_text('Some data bumped into the ceiling: {:.3f}'.format(self.ydata[-1]))
        t = np.round(self.xdata-self._t0, 1)
        self.mygraph.set_xydata(t, self.ydata)
