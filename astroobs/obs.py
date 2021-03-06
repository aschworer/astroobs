# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Guillaume SCHWORER
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import _core

_obsDataFile = './obsData.txt'
_many_color = ['#40AC1E','#4E9FCC','#9A4ECC','#CC7B4E','#4E2ECC','#CC9EBD','#8EDCCD','#DC1ED2','#F21616','#2816F2','#3BF216','#F2E016']

class ObservatoryList(object):
    """
    Manages the database of observatories.

    Args:
      * dataFile (str): path+file to the observatories database. If left to ``None``, the standard package database will be used

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      * Exception: if a mandatory input parameter is missing when loading all observatories

    Use :func:`add`, :func:`rem`, :func:`mod` to add, remove or modify an observatory to the database.
    
    >>> import astroobs.obs as obs
    >>> ol = obs.ObservatoryList()
    >>> ol
    List of 34 observatories
    >>> ol.obsids
    ['mwo',
     'kpno',
     'ctio',
     'lasilla',
     ...
     'vlt',
     'mgo',
     'ohp']
    >>> ol['ohp']
    {'elevation': 650.0,
     'lat': 0.7667376848115423,
     'long': 0.09971647793060935,
     'moonAvoidRadius': 0.0,
     'name': 'Observatoire de Haute Provence',
     'pressure': 1010.0,
     'temp': 15.0,
     'timezone': 'Europe/Paris'}
    """
    def __init__(self, dataFile=None, **kwargs):
        if dataFile is not None:
            self.dataFile = dataFile
        else:
            try:
                this_dir, this_filename = _core.os.path.split(__file__)
                self.dataFile = _core.os.path.join(this_dir, _obsDataFile[_obsDataFile.find('/')+1:])
            except:
                self.dataFile = _obsDataFile
        self._raiseError = bool(kwargs.get('raiseError', False))
        self._load(**kwargs)

    def _load(self, **kwargs):
        """
        Loads the list of observatories from the database using dataFile property
        """
        self.heads = [item.strip() for item in open(self.dataFile).readlines() if item.strip()[:7]=='#heads#'][0][7:]
        self.lines = [item.strip() for item in open(self.dataFile).readlines() if (item.strip()[:1]!='#' and item.strip()!="")]
        self._wholefile = [item.strip() for item in open(self.dataFile).readlines()]
        self.obsids = [item.strip().split(';')[0].lower() for item in open(self.dataFile).readlines() if (item.strip()[:1]!='#' and item.strip()!="")]
        allsplitobs = [item.split(';') for item in self.lines]
        self.obsdic = {}
        for item in allsplitobs:
            try:
                self.obsdic.update({item[0]:{'name':str(item[1]),'long':_core.E.degrees(item[2]),'lat':_core.E.degrees(item[3]),'elevation':float(item[4]),'temp':float(item[5]),'pressure':float(item[6]),'timezone':str(item[7]),'moonAvoidRadius':float(item[8])}})
            except:
                if bool(kwargs.get('raiseError', self._raiseError)) is True:
                    raise Exception, "Missing parameter for '%s' (obsid '%s')" % (item[1], item[0])
                else:
                    print "\033[31mMissing parameter for '%s' (obsid '%s')\033[39m" % (item[1], item[0])

    def _info(self):
        return "List of %s observatories" % (len(self.obsids))
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    def __getitem__(self, key):
        return self.obsdic[key]

    def add(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0, **kwargs):
        """
        Adds an observatory to the current observatories database.

        Args:
          * obsid (str): id of the observatory to add. Must be unique, without spaces or ;
          * name (str): name of the observatory
          * long (str - '+/-ddd:mm:ss.s'): longitude of the observatory. West is negative, East is positive
          * lat (str - '+/-dd:mm:ss.s'): latitude of the observatory. North is Positive, South is negative
          * elevation (float - m): elevation of the observatory
          * timezone (str): timezone of the observatory, as in pytz library. See note below
          * temp (float - degrees Celcius) [optional]: temperature at the observatory
          * pressure (float - hPa) [optional]: pressure at the observatory
          * moonAvoidRadius (float - degrees) [optional]: minimum distance at which a target must sit from the moon to be observed

        Kwargs:
          See class constructor

        Raises:
          * NameError: if the observatory ID already exists
          * Exception: if a mandatory input parameter is missing when reloading all observatories

        .. note::
          To view all available timezones, run:
          >>> import pytz
          >>> for tz in pytz.all_timezones:
          >>>     print tz
        """
        if str(obsid).lower() in self.obsids or str(obsid).strip().find(' ')!=-1 or str(obsid).strip().find(';')!=-1:
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise NameError, "The observatory ID provided already exists."
            else:    
                print "\033[31mThe observatory ID provided already exists.\033[39m"
                return
        else:
            f = open(self.dataFile, 'a')
            newobs = '\n%s;%s;%s;%s;%4.1f;%2.1f;%4.1f;%s;%3.1f' % (str(obsid).lower().strip(), str(name).replace(";",""), str(long).replace(";",""), str(lat).replace(";",""), float(elevation), float(temp), float(pressure), str(timezone).replace(";",""), float(moonAvoidRadius))
            f.write(newobs)
            f.close()
            self._load(**kwargs)

    def rem(self, obsid, **kwargs):
        """
        Removes an observatory from the current observatories database.

        Args:
          * obsid (str): id of the observatory to remove

        Kwargs:
          See class constructor

        Raises:
          * NameError: if the observatory ID does not exist
          * Exception: if a mandatory input parameter is missing when reloading all observatories
        """
        if str(obsid).lower() not in self.obsids:
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise NameError, "The observatory ID provided was not found."
            else:
                print "\033[31mThe observatory ID provided was not found.\033[39m"
                return
        else:
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load(**kwargs)

    def mod(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0, **kwargs):
        """
        Modifies an observatory in the current observatories database.

        Args:
          * obsid (str): id of the observatory to modify. All other parameters redefine the observatory

        Kwargs:
          See class constructor

        Raises:
          * NameError: if the observatory ID does not exist
          * Exception: if a mandatory input parameter is missing when reloading all observatories

        .. note::
          Refer to :func:`add` for details on input parameters
        """
        if str(obsid).lower() not in self.obsids:
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise NameError, "The observatory ID was not found."
            else:
                print "\033[31mThe observatory ID was not found.\033[39m"
                return
        else:
            newobs = '\n%s;%s;%s;%s;%4.1f;%2.1f;%4.1f;%s;%3.1f' % (str(obsid).lower().strip(), str(name).replace(";",""), str(long).replace(";",""), str(lat).replace(";",""), float(elevation), float(temp), float(pressure), str(timezone).replace(";",""), float(moonAvoidRadius))
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            newlines += newobs
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load(**kwargs)

    def nameList(self):
        """
        Provides a list of tuples (obs id, observatory name) in the alphabetical order of the column 'observatory name'.
        """
        obsorder = []
        names = _core.np.asarray([item.split(';')[1] for item in self.lines])
        ids = _core.np.asarray([item.split(';')[0] for item in self.lines])
        namesorted = _core.np.argsort(names)
        return zip(ids[namesorted], names[namesorted])


class Observatory(_core.E.Observer, object):
    """
    Defines an observatory from which the ephemeris of the twilights or a night-sky target are processed. The *night-time* is base on the given date. It ends at the next sunrise and starts at the sunset preceeding this next sunrise.

    Args:
      * obs (str): id of the observatory to pick from the observatories database OR the name of the custom observatory (in that case, ``long``, ``lat``, ``elevation``, ``timezone`` must also be given, ``temp``, ``pressure``, ``moonAvoidRadius`` are optional)
      * local_date (see below): the date of observation in local time
      * ut_date (see below): the date of observation in UT time
      * horizon_obs (float - degrees): minimum altitude at which a target can be observed, default is 30 degrees altitude
      * epoch (str): the 'YYYY' year in which all ra-dec coordinates are converted

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``
      * fig: TBD

    Raises:
      * NameError: if a mandatory input parameter is missing
      * KeyError: if the observatory ID does not exist
      * KeyError: if the twilight keyword is unknown
      * Exception: if the observatory object has no date

    .. note::
      * For details on ``local_date`` and ``ut_date``, refer to :func:`Observatory.upd_date`
      * For details on other input parameters, refer to :func:`ObservatoryList.add`
      * The :class:`Observatory` automatically creates and manages a :class:`Moon` target under ``moon`` attribute
      * If ``obs`` is the id of an observatory to pick in the database, the user can still provide ``temp``, ``pressure``, ``moonAvoidRadius`` attributes which will override the database default values
      * ``horizon`` attribute is in radian

    Main attributes:
      * ``localnight``: gives the local midnight time in local time (YYYY, MM, DD, 23, 59, 59)
      * ``date``: gives the local midnight time in UT time
      * ``dates``: is a vector of Dublin Julian Dates. Refer to :func:`process_obs`
      * ``lst``: the local sidereal time corresponding to each ``dates`` element
      * ``localTimeOffest``: gives the shift in days between UT and local time: local=UT+localTimeOffest
      * ``moon``: points to the :class:`Moon` target processed for the given observatory and date
    Twilight attributes:
      * For the next three attributes, ``XXX`` shall be replaced by {'' (blank), 'civil', 'nautical', 'astro'} for, respectively, horizon, -6, -12, and -18 degrees altitude
      * ``sunriseXXX``: gives the sunrise time for different twilights, in Dublin Julian Dates. e.g.: ``observatory.sunrise``
      * ``sunsetXXX``: gives the sunset time for different twilights, in Dublin Julian Dates. e.g.: ``observatory.sunsetcivil``
      * ``len_nightXXX``: gives the night duration for different twilights (between corresponding sunset and sunrise), in hours. e.g.: ``observatory.len_nightnautical``

    .. warning::
      * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

    >>> import astroobs.obs as obs
    >>> o = obs.Observatory('ohp', local_date=(2015,3,31,23,59,59))
    >>> o
    <ephem.Observer date='2015/3/31 21:59:59' epoch='2000/1/1 12:00:00'
    lon=5:42:48.0 lat=43:55:51.0 elevation=650.0m horizon=-0:49:04.8
    temp=15.0C pressure=1010.0mBar>
    >>> o.moon
    Moon - phase: 89.2%
    >>> print o.sunset, '...', o.sunrise, '...', o.len_night
    2015/3/31 18:08:40 ... 2015/4/1 05:13:09 ... 11.0746939826
    >>> import ephem as E
    >>> print E.Date(o.sunsetastro+o.localTimeOffest), '...', E.Date(
            o.sunriseastro+o.localTimeOffest), '...', o.len_nightastro
    2015/3/31 21:43:28 ... 2015/4/1 05:38:26 ... 7.91603336949
    """
    def __init__(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, local_date=None, ut_date=None, horizon_obs=None, dataFile=None, epoch='2000', **kwargs):
        super(Observatory, self).__init__() # first init
        self._raiseError = bool(kwargs.get('raiseError', False))
        if long is None and lat is None and elevation is None and timezone is None: # gave directly an obsid, supposely
            obslist = ObservatoryList(dataFile=dataFile, **kwargs)
            if str(obs).lower() in obslist.obsids: # if correct id
                for k, v in obslist.obsdic[str(obs).lower()].items(): # copy the site info to self
                    setattr(self, k, v)
                self.id = str(obs).lower()
            else: # if not correct id
                if bool(kwargs.get('raiseError', self._raiseError)) is True:
                    raise KeyError, "Could not find observatory id %s in database" % (str(obs).lower())
                else:
                    print "\033[31mCould not find observatory id %s in database.\033[39m" % (str(obs).lower())
                    return
        elif long is not None and lat is not None and elevation is not None and timezone is not None: # gave the details of a valid observatory
            self.name = str(obs)
            self.timezone = str(timezone)
            self.elevation = float(elevation)
            # checks the type of long and lat
            if isinstance(long, (float, int)):
                self.long = _core.np.deg2rad(long)
            else:
                self.long = _core.E.degrees(long)
            if isinstance(lat, (float, int)):
                self.lat = _core.np.deg2rad(lat)
            else:
                self.lat = _core.E.degrees(lat)
        else: # a parameter is missing
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise Exception, "One or more input parameter missing. All 'long', 'lat', 'elevation', and 'timezone' are mandatory."
            else:
                print "\033[31mOne or more input parameter missing. All 'long', 'lat', 'elevation', and 'timezone' are mandatory.\033[39m"
                return
        # overwrite observatory value
        if temp is not None: self.temp = float(temp)
        if pressure is not None: self.pressure = float(pressure)
        if moonAvoidRadius is not None: self.moonAvoidRadius = float(moonAvoidRadius)
        # checks if values exist and sets default if not
        if not hasattr(self, 'temp'): self.temp = 15.0
        if not hasattr(self, 'pressure'): self.pressure = 1010.0
        if not hasattr(self, 'moonAvoidRadius'): self.moonAvoidRadius = 0.
        epoch = str(int(epoch)) # set epoch
        if epoch == '2000':
            self.epoch = _core.E.J2000
        elif epoch == '1950':
            self.epoch = _core.E.B1950
        else:
            self.epoch = epoch
        self.horizon = -_core.np.sqrt(2*self.elevation/_core.E.earth_radius)
        if horizon_obs is None:
            self.horizon_obs = 30. # default value
        else:
            self.horizon_obs = float(horizon_obs)
        # initialise the date
        self.upd_date(local_date=local_date, ut_date=ut_date, force=True, **kwargs)


    def _calc_sunRiseSet(self, mode='', **kwargs):
        """
        Processes sunrise, sunset in UTC and night duration in hour and adds info to the object as attributes
        mode can be: '' (horizon), 'astro' (-18 degrees), 'nautical' (-12 degrees),'civil' (-6 degrees)

        assumption: self.date is local midnight of the observation date and is expressed in UT
        """
        horizs = {'':self.horizon, 'astro':-0.314159, 'nautical':-0.2094395, 'civil':-0.104719} # 18, 12 and 6 degrees
        if mode.lower() not in horizs.keys():
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise KeyError, "Unknown twilight '%s'" % mode # checks for mode
            else:
                print "\033[31mUnknown twilight '%s'\033[39m" % mode
                return
        s1, s2 = self.horizon, self.date # save initial obs values
        self.horizon = horizs[mode.lower()] # set horizon from mode
        # init in case of error
        setattr(self, "sunrise"+mode.lower(), None)
        setattr(self, "sunset"+mode.lower(), None)
        setattr(self, "len_night"+mode.lower(), 0.)
        try: # try block to catch NeverUp or AlwaysUp errors from pyephem in case of polar region
            v = self.next_rising(_core.E.Sun())
            setattr(self, "sunrise"+mode.lower(), v) # adds property sunrise of mode
            self.date = v
            setattr(self, "sunset"+mode.lower(), self.previous_setting(_core.E.Sun())) # adds property sunset of mode
            setattr(self, "len_night"+mode.lower(), (getattr(self, "sunrise"+mode.lower()) - getattr(self, "sunset"+mode.lower()))*24)
        except _core.E.AlwaysUpError:
            self.alwaysDark = False
        except _core.E.NeverUpError:
            self.alwaysDark = True
        self.horizon, self.date = s1, s2 # restore initial obs values


    def upd_date(self, ut_date=None, local_date=None, force=False, **kwargs):
        """
        Updates the date of the observatory, and re-process the observatory parameters if the date is different.

        Args:
          * ut_date (see below): the date of observation in UT time
          * local_date (see below): the date of observation in local time
          * force (bool): if ``False``, the observatory is re-processed only if the date changed

        Kwargs:
          See class constructor

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        Returns:
          ``True`` if the date was changed, otherwise ``False``

        .. note::
          * ``local_date`` and ``ut_date`` can be date-tuples ``(yyyy, mm, dd, [hh, mm, ss])``, timestamps, datetime structures or ephem.Date instances.
          * If both are given, ``ut_date`` has higher priority
          * If neither of those are given, the date is automatically set to *tonight* or *now* (whether the sun has already set or not)
        """
        stored_date = getattr(self, 'localnight', _core.datetime(2000, 1, 1))
        s1 = self.date # saves initiprocess_obsal date value
        # set the local_date to this night's sunset time in local time so we can get the local day/month/year
        if local_date is None and ut_date is None: # default set to tonight midnight if date not provided
            self.date = _core.E.now() # takes the now for temporary calculation
            try: # are we in a polar region ?
                self.date = _core.E.Date(self.next_rising(_core.E.Sun()))
                local_date = _core.convertTime(self.previous_setting(_core.E.Sun()), self.timezone, 'utc', format='dt')
            except (_core.E.AlwaysUpError, _core.E.NeverUpError): # yes sire
                if _core.convertTime(_core.E.now(), self.timezone, 'utc', format='dt').hour<12: # yest
                    local_date = _core.E.Date(_core.convertTime(_core.E.now(), self.timezone, 'utc', format='ed')-1).datetime()
                else: # today
                    local_date = _core.convertTime(_core.E.now(), self.timezone, 'utc', format='dt')
        elif ut_date is not None: # if given ut date
            local_date = _core.convertTime(ut_date, self.timezone, 'utc', format='dt')
        else: # if given local date
            local_date = _core.cleanTime(local_date, format='dt')
        # check if the date has changed
        if stored_date.year==local_date.year and stored_date.month==local_date.month and stored_date.day==local_date.day and force is False: # didn't change
            self.date = s1 # set initial value back
            return False
        else: # the date has changed
            self.localTimeOffest = _core.convertTime(_core.E.now(), self.timezone, 'utc', format='ed')-_core.E.now()
            self.localnight = local_date.replace(hour=23, minute=59, second=59) # midnight in local time
            self.date = _core.convertTime(self.localnight, 'utc', self.timezone, format='ed') # midnight in UT time
            self.process_obs(**kwargs)
            return True


    def process_obs(self, pts=200, margin=15, fullhour=False, **kwargs):
        """
        Processes all twilights as well as moon rise, set and position through night for the given observatory and date.
        Creates the vector ``observatory.dates`` which is the vector containing all timestamps at which the moon and the targets will be processed.

        Args:
          * pts (int) [optional]: the size of the ``dates`` vector, whose elements are linearly spaced in time
          * margin (float - minutes) [optional]: the margin between the first element of the vector ``dates`` and the sunset, and between the sunrise and its last element
          * fullhour (bool) [optional]: if ``True``, then the vector ``dates`` will start and finish on the first full hour preceeding sunset and following sunrise

        Kwargs:
          See class constructor

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        .. note::
          In case the observatory is in polar regions where the sun does not alway set and rise everyday, the first and last elements of the ``dates`` vector are set to local midday right before and after the local midnight of the observation date. e.g.: 24h night centered on the local midnight.
        """
        def set_data_range(sunset, sunrise, numdates, margin=15, fullhour=False):
            """Returns a numpy array of numdates dates linearly spaced in time, from margin minutes before sunset to margin minutes after sunrise if fullhour is False, and from the previous full hour before sunset to next full hour after sunrise if fullhour is True."""
            if fullhour:
                ss = _core.E.Date(int(sunset*24)/24.)
                sr = _core.E.Date(int(sunrise*24+1)/24.)
            else:
                ss = _core.E.Date(float(sunset) - margin*_core.E.minute)
                sr = _core.E.Date(float(sunrise) + margin*_core.E.minute)
            return _core.np.linspace(ss, sr, int(numdates))
        if not hasattr(self, "date"):
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise Exception, "No date specified, 'date' attribute must exist as ephem.date" # checks if date exists
            else:
                print "\033[31mNo date specified, 'date' attribute must exist as ephem.date.\033[39m"
                return
        self.date = _core.cleanTime(self.date, format='ed')
        for mode in ['','astro','nautical','civil']: # gets sunrise and sunsets for all modes
            self._calc_sunRiseSet(mode=mode, **kwargs)
        if self.sunset is not None and self.sunrise is not None:
            self.dates = set_data_range(sunset=self.sunset, sunrise=self.sunrise, numdates=pts, margin=margin, fullhour=fullhour) # gets linearly spaced dates along the night
        else: # no sunrise or sunset, observatory in polar regions
            startnight = _core.convertTime(self.localnight.replace(hour=12, minute=0, second=0), 'utc', self.timezone, format='ed')
            endnight = _core.convertTime(_core.E.Date(_core.E.Date(self.localnight)+1).datetime().replace(hour=11, minute=59, second=59), 'utc', self.timezone, format='ed')
            self.dates = set_data_range(sunset=startnight, sunrise=endnight, numdates=pts, margin=0, fullhour=False) # gets linearly spaced dates along the night
        # computes the lst
        s1 = self.date
        self.lst = []
        for d in self.dates:
            self.date = d
            self.lst.append(self.sidereal_time())
        self.lst = _core.np.asarray(self.lst)
        self.date = s1
        # computes the Moon
        self.moon = Moon(obs=self)


    @property
    def nowArg(self):
        """
        Returns the index of *now* in the ``observatory.dates`` vector, or None if *now* is out of its bounds (meaning the observation is not taking place now)

        >>> import astroobs.obs as obs
        >>> import ephem as E
        >>> o = obs.Observatory('ohp')
        >>> plt.plot(o.dates, o.moon.alt, 'k-')
        >>> now = o.nowArg
        >>> if now is not None:
        >>>     plt.plot(o.dates[now], o.moon.alt[now], 'ro')
        >>> else:
        >>>     plt.plot([E.now(), E.now()], [o.moon.alt.min(),o.moon.alt.max()], 'r--')
        """
        now = _core.E.now()
        deltadates = (self.dates[1]-self.dates[0])/2.
        if now<self.dates[0]-deltadates or now>self.dates[-1]+deltadates: return None
        return (_core.np.abs(self.dates-_core.E.now())).argmin()
    @nowArg.setter
    def nowArg(self, value):
        raise AttributeError, "Read-only"


    def plot(self, **kwargs):
        """
        Plots the observatory diagram

        Kwargs:
          * See class constructor
          * dt (float - hour): the spacing of tick-label of x-axis, default is 1 hour
          * t0 (float - DJD): the date of the first tick-label of x-axis, default is sunsetastro
          * xlim ([xmin, xmax]): bounds for x-axis, default is full night span
          * ylim ([ymin, ymax]): bounds for y-axis, default is [horizon_obs-10, 90]
          * xlabel (str): label for x-axis, default 'Time (UT)'
          * ylabel (str): label for y-axis, default 'Elevation (°)'
          * title (str): title of the diagram, default is observatory name or coordinates
          * ymin_margin (float): margin between xmin of graph and horizon_obs. Low priority vs ylim, default is 10
          * retfignum (bool): if ``True``, the figure number will be returned, default is ``False``
          * fignum (int): figure number on which to plot, default is ``False``
          * retaxnum (bool): if ``True``, the ax index as in ``figure.axes[n]`` will be returned, default is ``False``
          * axnum (int): axes index on which to plot, default is ``None`` (create new ax)
          * retfig (bool): if ``True``, the figure number will be returned, default is ``False``
          * fig (figure): figure on which to plot, default is ``None`` (use fignum)
          * retaxnum (bool): if ``True``, the ax index as in ``figure.axes[n]`` will be returned, default is ``False``
          * ax (axes): ax on which to plot, default is ``None``
          * now (bool): if ``True`` and within range, a vertical line as indication of "now" will be shown, default is True
          * retnow (bool): returns the line object (``nowline`` key) corresponding to the 'now-line', default is ``False``
          * legend (bool): whether to add a legend or not, default is ``True``
          * loc: location of the legend, default is 8 (top right), refer to plt.legend
          * ncol: number of columns in the legend, default is 3, refer to plt.legend
          * columnspacing: spacing between columns in the legend, refer to plt.legend
          * lfs: legend font size, default is 11
          * textlbl (bool): if ``True``, a text label with target name or coordinates will be added near transit, default is ``False``

        Raises:
          N/A
        """
        self._plot()

    def _plot(self, **kwargs):
        if kwargs.get('fignum', None) is None and kwargs.get('fig', None) is None and kwargs.get('axnum', None) is None and kwargs.get('ax', None) is None: # no fig and no ax given, need to create
            thefig = _core.plt.figure()
        elif kwargs.get('fignum', None) is not None:
            thefig = _core.plt.figure(kwargs['fignum'])
        elif kwargs.get('fig', None) is None and kwargs.get('ax', None) is not None:
            thefig = _core.plt.figure(kwargs['ax'].figure.number)
        else:
            thefig = kwargs['fig']
        if kwargs.get('axnum', None) is None and kwargs.get('ax', None) is None:
            theax = thefig.add_axes([0.1,0.1,0.8,0.8])
        elif kwargs.get('axnum', None) is not None:
            theax = thefig.axes[kwargs['ax']]
        else:
            theax = kwargs['ax']
        retkwargs = {}
        if kwargs.get('retfignum', False) is True: retkwargs.update({'fignum':thefig.number})
        if kwargs.get('retaxnum', False) is True: retkwargs.update({'axnum':thefig.axes.index(theax)})
        if kwargs.get('retfig', False) is True: retkwargs.update({'fig':thefig})
        if kwargs.get('retax', False) is True: retkwargs.update({'ax':theax})
        if kwargs.get('simpleplt', False) is not False:
            if retkwargs!={}:
                return retkwargs
            else:
                return
        # set min and max on y axis to most min and most max of any plot-able parameter, or ylim
        minmin, maxmax = theax.set_ylim(kwargs.get('ylim', [-180, 360]))
        # if polar night
        if (self.sunrise is None or self.sunset is None) and getattr(self, 'alwaysDark', False) is True:
            bgcolor = 'w'
        else:
            bgcolor = '#04031C'
        theax.add_patch(_core.Rectangle((self.dates[0], minmin), self.dates[-1]-self.dates[0], maxmax, facecolor=bgcolor, edgecolor=bgcolor))
        if self.sunset is not None and self.sunrise is not None:
            theax.add_patch(_core.Rectangle((self.sunset, minmin), self.sunrise-self.sunset, maxmax, facecolor='#1814A3', edgecolor='#1814A3'))
        if self.sunsetcivil is not None and self.sunrisecivil is not None:
            theax.add_patch(_core.Rectangle((self.sunsetcivil, minmin), self.sunrisecivil-self.sunsetcivil, maxmax, facecolor='#6F6BE8', edgecolor='#6F6BE8'))
        if self.sunsetnautical is not None and self.sunrisenautical is not None:
            theax.add_patch(_core.Rectangle((self.sunsetnautical, minmin), self.sunrisenautical-self.sunsetnautical, maxmax, facecolor='#C1BFF2', edgecolor='#C1BFF2'))
        if self.sunsetastro is not None and self.sunriseastro is not None:
            theax.add_patch(_core.Rectangle((self.sunsetastro, minmin), self.sunriseastro-self.sunsetastro, maxmax, facecolor='w', edgecolor='w'))
        theax.set_xlim(kwargs.get('xlim', [self.dates[0], self.dates[-1]]))
        if kwargs.has_key('ylim'):
            theax.set_ylim(kwargs['ylim'])
        else:
            theax.set_ylim([self.horizon_obs-float(kwargs.get('ymin_margin', 10)), 90])
            theax.add_patch(_core.Rectangle((self.dates[0], minmin), self.dates[-1]-self.dates[0], self.horizon_obs-minmin, facecolor='k', edgecolor='None', alpha=0.3))
        dt = float(kwargs.get('dt', 1))
        t0 = min(max(float(kwargs.get('t0', self.sunsetastro)), self.sunset), self.sunrise)
        datetick = _core.np.r_[_core.np.arange(t0, self.dates[0], -dt/24.)[::-1], _core.np.arange(t0, self.dates[-1], dt/24.)[1:]]
        datetickstr = [str(_core.E.Date(item)).split()[1][:-3] for item in datetick]
        _core.plt.xticks(datetick, datetickstr, rotation='horizontal', size='10')
        theax.grid(True)
        theax.set_xlabel(kwargs.get('xlabel', 'Time (UT)'))
        theax.set_ylabel(kwargs.get('ylabel', 'Elevation (°)'))
        theax.set_title(kwargs.get('title', getattr(self, 'name', str(self.lat)+' '+str(self.lon))+' - '+str(self.localnight).split()[0]))
        if kwargs.get('now') is True and obs.nowArg is not None:
            thenowline = theax.plot([_core.E.now(), _core.E.now()], theax.get_ylim(), 'r-')
        else:
            thenowline = ''
        if kwargs.get('retnow', False) is True: retkwargs.update({'nowline':thenowline})
        if retkwargs!={}: return retkwargs


class Target(object):
    """
    Initialises a target object from its right ascension and declination. Optionaly, processes the target for the observatory and date given (refer to :func:`Target.process`).

    Args:
      * ra (str 'hh:mm:ss.s' or float - degrees): the right ascension of the target
      * dec (str '+/-dd:mm:ss.s' or float - degrees): the declination of the target
      * name (str): the name of the target, for display
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the target
      * input_epoch (str): the 'YYYY' year of epoch in which the ra-dec coordinates are given. These coordinates will corrected with precession if the epoch of observatory is different

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A
    """
    def __init__(self, ra, dec, name, input_epoch='2000', obs=None, **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        if isinstance(ra, (float, int)):
            self._ra = _core.Angle(ra, 'deg')
        else:
            self._ra = _core.Angle(str(ra)+'h')
        self._dec = _core.Angle(str(dec)+'d')
        self.name = str(name)
        self.input_epoch = str(int(input_epoch))
        if obs is not None: self.process(obs=obs, **kwargs)

    def __getitem__(self, key):
        return getattr(self, str(key).lower(), None)

    def _info(self):
        return "Target: '%s', %ih%im%2.1fs %s%i°%i'%2.1f\"%s" % (self.name, self._ra.hms[0], self._ra.hms[1], self._ra.hms[2], (self._dec.dms[0]>0)*'+', self._dec.dms[0], _core.np.abs(self._dec.dms[1]), _core.np.abs(self._dec.dms[2]), hasattr(self, "_ticked")*(', '+getattr(self, "_ticked", False)*'O'+(not getattr(self, "_ticked", False))*'-'))
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    @property
    def ra(self):
        """
        The right ascension of the target, displayed as tuple (hh, mm, ss)
        """
        ra = self._ra.hms
        return [int(ra[0]), int(ra[1]), ra[2]]
    @ra.setter
    def ra(self, value):
        raise AttributeError, "Read-only"

    @property
    def dec(self):
        """
        The declination of the target, displayed as tuple (+/-dd, mm, ss)
        """
        dec = self._dec.dms
        return [int(dec[0]), int(dec[1]), dec[2]]
    @dec.setter
    def dec(self, value):
        raise AttributeError, "Read-only"

    @property
    def raStr(self):
        """
        A pretty printable version of the right ascension of the target
        """
        hms = self._ra.hms
        return "%ih%im%2.1fs" % (hms[0], hms[1], hms[2])
    @raStr.setter
    def raStr(self, value):
        raise AttributeError, "Read-only"
    @property
    def decStr(self):
        """
        A pretty printable version of the declination of the target
        """
        dms = self._dec.dms
        return "%s%i°%i'%2.1f\"" % ((dms[0]>0)*'+', dms[0], dms[1], dms[2])
    @decStr.setter
    def decStr(self, value):
        raise AttributeError, "Read-only"

    def _set_RiseSetTransit(self, target, obs, **kwargs):
        """
        Adds to self the attributes set_time, set_az, rise_time, rise_az, transit_az, transit_alt, transit_time of a target given an observatory.
        Set to rise/set attributes to None in case the target does not rise/set
        """
        s1 = obs.date # save initial obs values
        obs.date = obs.dates[0]
        self.rise_time = None
        self.rise_az = None
        self.set_time = None
        self.set_az = None
        try: # try block to catch NeverUp or AlwaysUp errors from pyephem in case of polar region
            self.set_time = obs.next_setting(target)
            obs.date = self.set_time
            target.compute(obs)
            self.set_az = _core.np.rad2deg(target.az)
            self.rise_time = obs.previous_rising(target)
            obs.date = self.rise_time
            target.compute(obs)
            self.rise_az = _core.np.rad2deg(target.az)
        except _core.E.AlwaysUpError:
            self.alwaysUp = True
        except _core.E.NeverUpError:
            self.alwaysUp = False
        if self.rise_time is not None:
            obs.date = self.rise_time
        else:
            obs.date = obs.dates[0]
        self.transit_time = obs.next_transit(target)
        obs.date = self.transit_time
        target.compute(obs)
        self.transit_az = _core.np.rad2deg(target.az)
        self.transit_alt = _core.np.rad2deg(target.alt)
        obs.date = s1 # restore initial obs values

    def process(self, obs, **kwargs):
        """
        Processes the target for the given observatory and date.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the target

        Kwargs:
          See class constructor

        Raises:
          N/A

        Creates vector attributes:
          * ``airmass``: the airmass of the target
          * ``ha``: the hour angle of the target (degrees)
          * ``alt``: the altitude of the target (degrees - horizon is 0)
          * ``az``: the azimuth of the target (degrees)
          * ``moondist``: the angular distance between the moon and the target (degrees)

        .. note::
          * All previous attributes are vectors related to the time vector of the observatory used for processing, stored under ``dates`` attribute

        Other attributes:
          * ``rise_time``, ``rise_az``: the time (ephem.Date) and the azimuth (degree) of the rise of the target
          * ``set_time``, ``set_az``: the time (ephem.Date) and the azimuth (degree) of the setting of the target
          * ``transit_time``, ``transit_az``: the time (ephem.Date) and the azimuth (degree) of the transit of the target
        
        .. warning::
          * it can occur that the target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``, i.e. ``set_time``, ``set_az``, ``rise_time``, ``rise_az``. In that case, an additional parameter is added to the Target object: ``Target.alwaysUp`` which is ``True`` if the target never sets and ``False`` if it never rises above the horizon.
        """
        save_date = obs.date # saves the date
        obs.date = obs.dates[0]
        self.airmass = []
        self.ha = []
        self.alt = []
        self.az = []
        self.moondist = []
        targetdb = "star,f|V|G2,%s,%s%s,0.0,%s" % (':'.join(map(str, self.ra)), '-'*(self.dec[0]<0), ':'.join(map(str, map(abs, self.dec))), int(self.input_epoch))
        target = _core.E.readdb(targetdb)
        self._set_RiseSetTransit(target=target, obs=obs, **kwargs)
        for t in range(len(obs.dates)):
            obs.date = obs.dates[t] # forces the obs date for target calculation
            target.compute(obs)
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            self.ha.append(obs.lst[t] - target.a_ra)
            self.moondist.append(_core.E.separation([self.az[t], self.alt[t]], [_core.np.deg2rad(obs.moon.az[t]), _core.np.deg2rad(obs.moon.alt[t])]))
        # set radec to obs epoch
        self._ra = _core.np.rad2deg(_core.Angle(target.a_ra, unit='rad'))
        self._dec = _core.np.rad2deg(_core.Angle(target.a_dec, unit='rad'))
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self.airmass = _core.np.asarray(self.airmass)
        self.moondist = _core.np.rad2deg(self.moondist)

    def _whenobs(self, obs, fromDate="now", toDate="now+30day", plot=True, ret=False, dday=1, **kwargs):
        """
        Does the calculations for whenobs method
        """
        if fromDate=="now":
            fromDate = _core.E.now()
        else:
            fromDate = _core.cleanTime(fromDate, format='ed')
        if toDate=="now+30day":
            toDate = _core.E.Date(fromDate+30)
        else:
            toDate = _core.cleanTime(toDate, format='ed')
        old_date = obs.date
        dday = max(1, int(dday))
        dates = _core.np.arange(fromDate, toDate, dday)
        retval = []
        for date in dates:
            obs.upd_date(ut_date=_core.E.Date(date), **kwargs)
            # checks for polar night/day
            if obs.sunset is None or obs.sunrise is None: # if polar
                if obs.alwaysDark is True:
                    gooddates = _core.np.ones(len(obs.dates), dtype=bool)
                else:
                    retval.append((0., 0., obs.dates.size*dt, 0., 0., 0., 0.))
                    continue
            else:
                gooddates = ((obs.dates>obs.sunset) & (obs.dates<obs.sunrise))
            dt = (obs.dates[1]-obs.dates[0])*24
            self.process(obs=obs, **kwargs)
            badalt = (self.alt[gooddates]<obs.horizon_obs)
            if obs.sunsetastro is None or obs.sunriseastro is None: # no astro set or rise of target
                badsunsetting = _core.np.ones(gooddates.sum(), dtype=bool)
                badsunrising = _core.np.ones(gooddates.sum(), dtype=bool)
            else:
                badsunsetting = (obs.dates[gooddates]<obs.sunsetastro)
                badsunrising = (obs.dates[gooddates]>obs.sunriseastro)
            badmoon = (self.moondist[gooddates]<obs.moonAvoidRadius)
            # get statistics for target
            sunsettinggoodmoon = ((badsunsetting) & (_core.np.logical_not(badmoon)) & (_core.np.logical_not(badalt)))
            sunsettingbadmoon = ((badsunsetting) & (badmoon) & (_core.np.logical_not(badalt)))
            sunrisinggoodmoon = ((badsunrising) & (_core.np.logical_not(badmoon)) & (_core.np.logical_not(badalt)))
            sunrisingbadmoon = ((badsunrising) & (badmoon) & (_core.np.logical_not(badalt)))
            obsgoodmoon = ((_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)) & (_core.np.logical_not(badalt)) & (_core.np.logical_not(badmoon)))
            obsbadmoon = ((_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)) & (_core.np.logical_not(badalt)) & (badmoon))
            darkbadalt = ((badalt) & (_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)))
            twighlightbadalt = ((badalt) & ((badsunrising) | (badsunsetting)))
            retval.append((obsgoodmoon.sum()*dt, obsbadmoon.sum()*dt, sunsettinggoodmoon.sum()*dt, sunsettingbadmoon.sum()*dt, sunrisinggoodmoon.sum()*dt, sunrisingbadmoon.sum()*dt, darkbadalt.sum()*dt, twighlightbadalt.sum()*dt))
        # set the date back
        obs.upd_date(ut_date=old_date, **kwargs)
        self.process(obs=obs, **kwargs)
        # prepare outputing
        retkeys = ['obs','moon','dusk','duskmoon','dawn','dawnmoon','darklow','twighlightlow']
        retval = _core.np.asarray(retval, dtype=[(key, 'f8') for key in retkeys])
        return dates, retval, retkeys

    def whenobs(self, obs, fromDate="now", toDate="now+30day", plot=True, ret=False, dday=1, **kwargs):
        """
        Processes the target for the given observatory and dat.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the target
          * fromDate (see below): the start date of the range
          * toDate (see below): the end date of the range
          * plot: whether it plots the diagram
          * ret: whether it returns the values
          * dday: the 

        Kwargs:
          See class constructor
          * legend (bool): whether to add a legend or not, default is ``True``
          * loc: location of the legend, default is 8 (top right), refer to plt.legend
          * ncol: number of columns in the legend, default is 3, refer to plt.legend
          * columnspacing: spacing between columns in the legend, refer to plt.legend
          * lfs: legend font size, default is 11

        Raises:
          N/A

        .. note::
          * ``local_date`` and ``ut_date`` can be date-tuples ``(yyyy, mm, dd, [hh, mm, ss])``, timestamps, datetime structures or ephem.Date instances.
        """
        defaultlegend = True
        dates, retval, retkeys = self._whenobs(obs=obs, fromDate=fromDate, toDate=toDate, plot=plot, ret=ret, dday=dday, **kwargs)
        if plot is True:
            def daymon(t):
                months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                t = str(_core.E.Date(t)).split()[0].split('/')[1:][::-1]
                return t[0]+' '+months[int(t[1])]
            thefig = _core.plt.figure()
            theax = thefig.add_axes([0.09,0.15,0.85,0.8])
            bottombar = _core.np.zeros(dates.size)
            color = {'obs':'#02539C', 'moon':'#02539C', 'twighlightlow':'#AB6E50', 'darklow':'#6E2D0D', 'dusk':'#FACF50', 'duskmoon':'#FACF50', 'dawnmoon':'#A1E6E2', 'dawn':'#A1E6E2'}
            legend = {'obs':'Optimal','twighlightlow':'Low+Dusk/Dawn', 'darklow':'Low+Dark', 'dusk':'Up+Dusk','dawn':'Up+Dawn'}
            hatch = {'duskmoon':'//', 'moon':'//', 'dawnmoon':'//'}
            datestr = [daymon(item) for item in dates]
            for key in retkeys:
                if legend.get(key, '')!='' and kwargs.get('legend', defaultlegend) is True:
                    theax.bar(dates, retval[key], bottom=bottombar, width=0.8+(dday-1)*0.9, color=color[key], hatch=hatch.get(key, ''), edgecolor='k', linewidth=0.0, label=legend.get(key, ''))
                else:
                    theax.bar(dates, retval[key], bottom=bottombar, width=0.8+(dday-1)*0.9, color=color[key], hatch=hatch.get(key, ''), edgecolor='k', linewidth=0.0)
                bottombar += retval[key]
            _core.plt.xticks(dates[0::2]+0.5, datestr[0::2], rotation='vertical')
            theax.bar(dates, _core.np.zeros(dates.size), bottom=0, color='w', hatch='//', edgecolor='k', label='Moon')
            theax.set_xlim([dates[0]-1, dates[-1]+2])
            theax.set_ylabel('Duration (hour)')
            theax.set_title(getattr(self, 'name', self.raStr+' '+self.decStr)+' @ '+getattr(obs, 'name', str(obs.lat)+' '+str(obs.lon)))
            if kwargs.get('legend', defaultlegend) is True:
                theax.legend(loc=kwargs.get('loc', 8), frameon=True, ncol=kwargs.get('ncol', 3), columnspacing=kwargs.get('columnspacing', 0.2))
                theax.get_legend().texts[0].set_fontsize(kwargs.get('lfs', 11))
        if ret is not False: return dates, retval

    def plot(self, obs, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the target at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the target

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * simpleplt (bool): if ``True``, the observatory plot will not be plotted, default is ``False``
          * color (str or #XXXXXX): the color of the target curve, default is 'k'
          * lw (float): the linewidth, default is 1
        
        Raises:
          N/A
        """
        self._plot(obs=obs, y=y, **kwargs)

    def _plot(self, obs, y='alt', **kwargs):
        defaultlegend = False
        kwargs['title'] = kwargs.get('title', getattr(self, 'name', self.raStr+' '+self.decStr)+' @ '+getattr(obs, 'name', str(obs.lat)+' '+str(obs.lon)) +' - '+str(obs.localnight).split()[0])
        kwargs['ylabel'] = kwargs.get('ylabel', 'Elevation (°) vs time (UT)')
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        retkwargs = obs._plot(**kwargs)
        if kwargs.get('legend', defaultlegend) is True:
            retkwargs['ax'].plot(obs.dates, getattr(self, y), kwargs.get('color', 'k'), lw=kwargs.get('lw', 1), label=getattr(self, 'name', self.raStr+' '+self.decStr))
        else:
            retkwargs['ax'].plot(obs.dates, getattr(self, y), kwargs.get('color', 'k'), lw=kwargs.get('lw', 1))
        if kwargs.get('legend', defaultlegend) is True:
            retkwargs['ax'].legend(loc=kwargs.get('loc', 8), frameon=True, ncol=kwargs.get('ncol', 3), columnspacing=kwargs.get('columnspacing', 0.2))
            retkwargs['ax'].get_legend().texts[0].set_fontsize(kwargs.get('lfs', 11))
        if kwargs.get('textlbl', False) is True:
            retkwargs['ax'].text(obs.dates[:-30][self.alt[:-30].argmax()], self.alt[:-30].max(), getattr(self, 'name', self.raStr+' '+self.decStr))
        if saveretax is False: retkwargs.pop('ax')
        if retkwargs!={}: return retkwargs
        


class Moon(Target):
    """
    Initialises the Moon. Optionaly, processes the Moon for the observatory and date given (refer to :func:`Moon.process`).

    Args:
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the Moon

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A
    """
    def __init__(self, obs=None, input_epoch='2000', **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        self.name = 'Moon'
        self.input_epoch = str(int(input_epoch))
        if obs is not None: self.process(obs=obs, **kwargs)

    def _info(self):
        return "Moon - phase: %2.1f%%" % (self.phase.mean())
    @property
    def ra(self):
        """
        The right ascension of the Moon, displayed as tuple of np.array (hh, mm, ss)
        """
        return self._ra.hms
    @ra.setter
    def ra(self, value):
        raise AttributeError, "Read-only"

    @property
    def dec(self):
        """
        The declination of the Moon, displayed as tuple of np.array (+/-dd, mm, ss)
        """
        return self._dec.dms
    @dec.setter
    def dec(self, value):
        raise AttributeError, "Read-only"

    @property
    def raStr(self):
        """
        A pretty printable version of the mean of the right ascension of the moon
        """
        hms = self._ra.hms
        return "%ih%im%2.1fs" % (hms[0].mean(), hms[1].mean(), hms[2].mean())
    @raStr.setter
    def raStr(self, value):
        raise AttributeError, "Read-only"
    @property
    def decStr(self):
        """
        A pretty printable version of the mean of the declination of the moon
        """
        dms = self._dec.dms
        return "%s%i°%i'%2.1f\"" % ((dms[0].mean()>0)*'+', dms[0].mean(), dms[1].mean(), dms[2].mean())
    @decStr.setter
    def decStr(self, value):
        raise AttributeError, "Read-only"

    def plot(self, obs, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the moon at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the moon

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * simpleplt (bool): if ``True``, the observatory plot will not be plotted, default is ``False``
          * color (str or #XXXXXX): the color of the moon curve, default is '#777777'
          * lw (float): the linewidth, default is 1
        
        Raises:
          N/A
        """
        kwargs['color'] = kwargs.get('color', '#777777')
        self._plot(obs=obs, y=y, **kwargs)

    def process(self, obs, **kwargs):
        """
        Processes the moon for the given observatory and date.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the moon

        Kwargs:
          See class constructor

        Raises:
          N/A

        Creates vector attributes:
          * ``airmass``: the airmass of the moon
          * ``ha``: the hour angle of the moon (degrees)
          * ``alt``: the altitude of the moon (degrees - horizon is 0)
          * ``az``: the azimuth of the moon (degrees)
          * ``ra``: the right ascension of the moon, see :func:`Moon.ra`
          * ``dec``: the declination of the moon, see :func:`Moon.dec`

        .. note::
          * All previous attributes are vectors related to the time vector of the observatory used for processing: ``obs.dates``

        Other attributes:
          * ``rise_time``, ``rise_az``: the time (ephem.Date) and the azimuth (degree) of the rise of the moon
          * ``set_time``, ``set_az``: the time (ephem.Date) and the azimuth (degree) of the setting of the moon
          * ``transit_time``, ``transit_az``: the time (ephem.Date) and the azimuth (degree) of the transit of the moon
        
        .. warning::
          * it can occur that the moon does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``, i.e. ``set_time``, ``set_az``, ``rise_time``, ``rise_az``. In that case, an additional parameter is added to the Moon object: ``Moon.alwaysUp`` which is ``True`` if the Moon never sets and ``False`` if it never rises above the horizon.
        """
        save_date = obs.date # saves the date
        obs.date = _core.E.Date(obs.dates[0])
        self.ha = []
        self.airmass = []
        self.phase = []
        self.alt = []
        self.az = []
        self._ra = []
        self._dec = []
        target = _core.E.Moon()
        self._set_RiseSetTransit(target=target, obs=obs, **kwargs)
        for t in range(len(obs.dates)):
            obs.date = obs.dates[t] # forces obs date for target calculations
            target.compute(obs) # target calculation
            self.phase.append(target.phase)
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            self._ra.append(target.a_ra)
            self._dec.append(target.a_dec)
            self.ha.append(obs.lst[t] - target.a_ra)
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self._ra = _core.np.rad2deg(_core.Angle(self._ra, 'rad'))
        self._dec = _core.np.rad2deg(_core.Angle(self._dec, 'rad'))
        self.airmass = _core.np.asarray(self.airmass)
        self.phase = _core.np.asarray(self.phase)



class TargetSIMBAD(Target):
    """
    Initialises a target object from an online SIMBAD database name-search. Optionaly, processes the target for the observatory and date given (refer to :func:`TargetSIMBAD.process`).

    Args:
      * name (str): the name of the target as if performing an online SIMBAD search
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the target
    
    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A

    Creates attributes:
      * ``flux``: a dictionary of the magnitudes of the target. Keys are part or all of ['U','B','V','R','I','J','H','K']
      * ``link``: the link to paste into a web-browser to display the SIMBAD page of the target
      * ``linkbib``: the link to paste into a web-browser to display the references on the SIMBAD page of the target
      * ``hd``: if applicable, the HD number of the target
      * ``hr``: if applicable, the HR number of the target
      * ``hip``: if applicable, the HIP number of the target
    """
    def __init__(self, name, obs=None, input_epoch='2000', **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        self.name = str(name)
        self.input_epoch = str(int(input_epoch))
        customSimbad = _core.Simbad()
        customSimbad.add_votable_fields('fluxdata(U)', 'fluxdata(B)', 'fluxdata(V)', 'fluxdata(R)', 'fluxdata(I)', 'fluxdata(J)', 'fluxdata(H)', 'fluxdata(K)', 'plx', 'sptype')
        try:
            result = customSimbad.query_object(str(self.name))
        except:
            print "\033[31mThe given object was not found in SIMBAD.\033[39m"
            return
        if result is None:
            if bool(kwargs.get('raiseError', self._raiseError)) is True:
                raise NameError, "The given object was not found in SIMBAD"
            else:
                print "\033[31mThe given object was not found in SIMBAD.\033[39m"
                return
        self._ra = _core.Angle(str(result['RA'][0])+'h')
        self._dec = _core.Angle(str(result['DEC'][0])+'d')

        # copies the fluxes
        self.flux = {}
        if not hasattr(result['FLUX_U'][0], 'mask'): self.flux.update({'U':float(result['FLUX_U'][0])})
        if not hasattr(result['FLUX_B'][0], 'mask'): self.flux.update({'B':float(result['FLUX_B'][0])})
        if not hasattr(result['FLUX_V'][0], 'mask'): self.flux.update({'V':float(result['FLUX_V'][0])})
        if not hasattr(result['FLUX_R'][0], 'mask'): self.flux.update({'R':float(result['FLUX_R'][0])})
        if not hasattr(result['FLUX_I'][0], 'mask'): self.flux.update({'I':float(result['FLUX_I'][0])})
        if not hasattr(result['FLUX_J'][0], 'mask'): self.flux.update({'J':float(result['FLUX_J'][0])})
        if not hasattr(result['FLUX_H'][0], 'mask'): self.flux.update({'H':float(result['FLUX_H'][0])})
        if not hasattr(result['FLUX_K'][0], 'mask'): self.flux.update({'K':float(result['FLUX_K'][0])})
        self.sptype = str(result['SP_TYPE'][0])
        if not hasattr(result['PLX_VALUE'][0],'mask'):
            self.plx = float(result['PLX_VALUE'][0])
            self.dist = 1000/self.plx

        # searches for HD, HR, and HIP numbers
        for i in _core.Simbad.query_objectids(self.name)['ID']:
            i = i.upper()
            if i[:3]=='HD ':
                self.hd = int(_core.make_num(_core.re.sub('^(HD)','',i).strip()))
            if i[:3]=='HR ':
                self.hr = int(_core.make_num(_core.re.sub('^(HR)','',i).strip()))
            if i[:4]=='HIP ':
                self.hip = int(_core.make_num(_core.re.sub('^(HIP)','',i).strip()))

        self.link = "http://simbad.u-strasbg.fr/simbad/sim-id?Ident=" + self.name.replace("+","%2B").replace("#","%23").replace(" ","+")
        self.linkbib = self.link + "&submit=display&bibdisplay=refsum&bibyear1=1950&bibyear2=%24currentYear#lab_bib"
        if obs is not None: self.process(obs=obs, **kwargs)


class Observation(Observatory):
    """
    Assembles together an :class:`Observatory` (including itself the :class:`Moon` target), and a list of :class:`Target`.

    For use and docs refer to:
      * :func:`add_target` to add a target to the list
      * :func:`rem_target` to remove one
      * :func:`change_obs` to change the observatory
      * :func:`change_date` to change the date of observation

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``
      * fig: TBD

    Raises:
      See :class:`Observatory`

    .. warning::
      * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

    >>> import astroobs.obs as obs
    >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
    >>> o
    Observation at Observatoire de Haute Provence on 2015/6/21-22. 0 targets.
        Moon phase: 89.2%
    >>> o.moon
    Moon - phase: 89.2%
    >>> print o.sunset, '...', o.sunrise, '...', o.len_night
    2015/3/31 18:08:40 ... 2015/4/1 05:13:09 ... 11.0746939826
    >>> import ephem as E
    >>> print E.Date(o.sunsetastro+o.localTimeOffest), '...', E.Date(
            o.sunriseastro+o.localTimeOffest), '...', o.len_nightastro
    2015/3/31 21:43:28 ... 2015/4/1 05:38:26 ... 7.91603336949
    >>> o.add_target('vega')
    >>> o.add_target('mystar', dec=19.1824, ra=213.9153)
    >>> o.targets
    [Target: 'vega', 18h36m56.3s +38°35'8.1", O,
     Target: 'mystar', 14h15m39.7s +19°16'43.8", O]
    >>> print "%s mags: 'K': %2.2f, 'R': %2.2f"%(o.targets[0].name,
            o.targets[0].flux['K'], o.targets[0].flux['R'])
    vega mags: 'K': 0.13, 'R': 0.07
    """
    def _info(self):
        nextday = _core.E.Date(_core.E.Date(self.localnight)+1).datetime()
        nextdaystr = [str(nextday.day)]
        if nextday.month!=self.localnight.month: nextdaystr = [str(nextday.month)] + nextdaystr
        if nextday.year!=self.localnight.year: nextdaystr = [str(nextday.year)] + nextdaystr
        return "Observation at %s on %i/%i/%i-%s. %i targets. Moon phase: %2.1f%%" % (self.name, self.localnight.year, self.localnight.month, self.localnight.day, "/".join(nextdaystr), len(self.targets), self.moon.phase.mean())
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    @property
    def targets(self):
        """
        Shows the list of targets recorded into the Observation
        """
        if not hasattr(self, '_targets'): self._targets = []
        return self._targets
    @targets.setter
    def targets(self, value):
        if not isinstance(value, (list, tuple)): # single element
            if not isinstance(value, Target):
                if bool(kwargs.get('raiseError', self._raiseError)) is True:
                    raise AttributeError, "Can't add non-Target object to target list"
                else:
                    print "\033[31mCan't add non-Target object to target list\033[39m"
                    return
            self._targets = [value] # adds the moon and the element
            self._targets._ticked = True
        else:
            for item in value:
                if bool(kwargs.get('raiseError', self._raiseError)) is True:
                    raise AttributeError, "Can't add non-Target object to target list"
                else:
                    print "\033[31mCan't add non-Target object to target list\033[39m"
                    return
            self._targets = value
            for item in self._targets:
                item._ticked = True
                item.process(obs=self, **kwargs)

    @property
    def ticked(self):
        """
        Shows whether the target was select for observation
        """
        if not hasattr(self, '_targets'): return []
        return [item._ticked for item in self._targets]
    @ticked.setter
    def ticked(self, value):
        raise AttributeError, "Read-only"

    def tick(self, tgt, forceTo=None, **kwargs):
        """
        Changes the ticked property of a target (whether it is selected for observation)

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list
          * forceTo (bool) [optional]: if ``True``, selects the target for observation, if ``False``, unselects it, if ``None``, the value of the selection is inverted
        
        Kwargs:
          See class constructor

        Raises:
          N/A

        .. note::
          * Automatically reprocesses the target for the given observatory and date if it is selected for observation

        >>> import astroobs.obs as obs
        >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
        >>> o.add_target('arcturus')
        >>> o.targets
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", O]
        >>> o.tick(4)
        >>> o.targets
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", -]
        """
        if not hasattr(self, '_targets') or not isinstance(tgt, int): return None
        if forceTo is not None:
            self._targets[tgt]._ticked = bool(forceTo)
        else:
            self._targets[tgt]._ticked = not bool(self._targets[tgt]._ticked)
        if self._targets[tgt]._ticked is True: self._targets[tgt].process(self, **kwargs)
    

    def add_target(self, tgt, ra=None, dec=None, name="", **kwargs):
        """
        Adds a target to the observation list
        
        Args:
          * tgt (see below): the index of the target in the ``Observation.targets`` list
          * ra ('hh:mm:ss.s' or decimal degree) [optional]: the right ascension of the target to add to the observation list. See below
          * dec ('+/-dd:mm:ss.s' or decimal degree) [optional]: the declination of the target to add to the observation list. See below
          * name (string) [optional]: the name of the target to add to the observation list. See below
        
        ``tgt`` arg can be:
          * a :class:`Target` instance: all other parameters are ignored
          * a target name (string): if ``ra`` and ``dec`` are not ``None``, the target is added with the provided coordinates; if ``None``, a SIMBAD search is performed on ``tgt``. ``name`` is ignored
          * a ra-dec string ('hh:mm:ss.s +/-dd:mm:ss.s'): in that case, ``ra`` and ``dec`` will be ignored and ``name`` will be the name of the target

        Kwargs:
          See class constructor

        Raises:
          * ValueError: if ra-dec formating was not understood

        .. note::
          * Automatically processes the target for the given observatory and date

        >>> import astroobs.obs as obs
        >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
        >>> arc = obs.TargetSIMBAD('arcturus')
        >>> o.add_target(arc)
        >>> o.add_target('arcturus')
        >>> o.add_target('arcturus', dec=19.1824, ra=213.9153)
        >>> o.add_target('14:15:39.67 +10:10:56.67', name='arcturus')
        >>> o.targets 
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +10°40'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O]
        """
        if not hasattr(self, '_targets'): self._targets = []
        if isinstance(tgt, Target):
            self._targets += [tgt]
        elif ra is not None and dec is not None:
            self._targets += [Target(ra=ra, dec=dec, name=tgt, **kwargs)]
        elif isinstance(tgt, (int, float, str)): # if we have a ra-dec string
            try:
                ra, dec = _core.radecFromStr(str(tgt))
                self._targets += [Target(ra=ra, dec=dec, name=name, **kwargs)]
            except:
                self._targets += [TargetSIMBAD(name=tgt)]
        self._targets[-1]._ticked = True
        self._targets[-1].process(obs=self, **kwargs)

    def rem_target(self, tgt, **kwargs):
        """
        Removes a target from the observation list

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list

        Kwargs:
          See class constructor

        Raises:
          N/A
        """
        if not hasattr(self, '_targets'): return None
        if isinstance(tgt, int): self._targets.pop(tgt)

    def change_obs(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, horizon_obs=None, dataFile=None, recalcAll=False, **kwargs):
        """
        Changes the observatory and optionaly re-processes all target for the new observatory and same date

        Args:
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process

        Kwargs:
          See class constructor

        .. note::
          * Refer to :func:`ObservatoryList.add` for details on other input parameters
        """
        targets = self._targets
        Observation.__init__(self, obs=obs, long=long, lat=lat, elevation=elevation, timezone=timezone, temp=temp, pressure=pressure, moonAvoidRadius=moonAvoidRadius, local_date=self.localnight, horizon_obs=horizon_obs, dataFile=dataFile, **kwargs)
        self._targets = targets
        if recalcAll is not None: self._process(recalcAll=recalcAll, **kwargs)


    def _process(self, recalcAll=False, **kwargs):
        """
        Processes all target for the given observatory and date
        Args:
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process
        """
        for item in self.targets:
            if item._ticked or recalcAll: item.process(self, **kwargs)
        

    def change_date(self, ut_date=None, local_date=None, recalcAll=False, **kwargs):
        """
        Changes the date of the observation and optionaly re-processes targets for the same observatory and new date

        Args:
          * ut_date: Refer to :func:`Observatory.upd_date`
          * local_date: Refer to :func:`Observatory.upd_date`
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process

        Kwargs:
          See class constructor

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        """
        self.upd_date(ut_date=ut_date, local_date=local_date, **kwargs)
        if recalcAll is not None: self._process(recalcAll=recalcAll, **kwargs)

    def plot(self, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the target at the given observatory and date

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * moon (bool): if ``True``, adds the moon to the graph, default is ``True``
          * autocolor (bool): if ``True``, sets curves-colors automatically, default is ``True``

        Raises:
          N/A
        """
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        retkwargs = self._plot(**kwargs)
        kwargs['ax'] = retkwargs['ax']
        kwargs['simpleplt'] = True
        colindex = 0
        for item in self.targets:
            if item._ticked is True and item.name.lower()!="moon":
                if kwargs.get('autocolor', True): kwargs['color'] = _many_color[colindex%len(_many_color)]
                item.plot(self, y=y, **kwargs)
                colindex += 1
        if kwargs.has_key('color'): kwargs.pop('color')
        if kwargs.get('moon', True) is True: self.moon.plot(self, y=y, **kwargs)
        if saveretax is False: retkwargs.pop('ax')
        if retkwargs!={}: return retkwargs
