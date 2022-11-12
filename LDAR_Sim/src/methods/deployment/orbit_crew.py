
# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        methods.deployment.orbit_crew
# Purpose:     Orbit company specific deployment classes and methods (ie. Scheduling)
#
# Copyright (C) 2018-2021  Intelligent Methane Monitoring and Management System (IM3S) Group
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License as published
# by the Free Software Foundation, version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# MIT License for more details.

# You should have received a copy of the MIT License
# along with this program.  If not, see <https://opensource.org/licenses/MIT>.
#
# ------------------------------------------------------------------------------

from datetime import timedelta

import netCDF4 as nc
import numpy as np
from orbit_predictor.sources import get_predictor_from_tle_lines
from shapely import speedups
from shapely.geometry import Point
from utils.generic_functions import (geo_idx, init_orbit_poly,
                                     quick_cal_daylight)

speedups.disable()


class Schedule():
    def __init__(self, id, lat, lon, state, config, parameters, deployment_days, home_bases=None):
        self.parameters = parameters
        self.config = config
        self.state = state
        self.deployment_days = deployment_days
        self.crew_lat = lat
        self.crew_lon = lon
        self.work_hours = 24
        self.start_hour = 0
        self.end_hour = 23
        self.allowed_end_time = None

        # extract cloud cover data
        input_directory = self.parameters['input_directory']
        cloud = self.parameters['weather_file']
        Dataset = nc.Dataset(input_directory / cloud, 'r')
        self.cloudcover = Dataset.variables['tcc'][:]
        Dataset.close()
        # obtain TLE file path
        self.sat = self.config['TLE_label']
        self.tlefile = self.config['TLE_file']

        self.get_orbit_predictor()
        self.get_orbit_path()

    def start_day(self, site_pool):
        '''Start day method. Initialize time to accounty for work hours. The
           site pool that are ready for survey are passed from the company to
           the satellite to filter out sites that are not viewable, covered
           by clound, and don't have daylight.
        '''
        # Set start of work, satellite can work 24 hours per day
        self.state['t'].current_date = self.state['t'].current_date.replace(
            hour=int(1))

        # find out the site that can be seen by satellite
        viewable_sites = self.calc_viewable_sites(site_pool)
        if len(viewable_sites) == 0:
            self.worked_today = False
            daily_site_plans = []
        # check daylight and cloud_cover for each site inside the site pool
        else:
            daily_site_plans = []
            for site in viewable_sites:
                sat_dl, sat_cc = self.assess_weather(site)
                if (sat_dl and sat_cc) or not self.parameters['consider_weather']:
                    plan = self.plan_visit(site)
                    daily_site_plans.append(plan)

        return daily_site_plans

    def plan_visit(self, site):
        '''create a visit plan for satellite, the go_to_site
           are always true if site passed from start_day.
           We assume the survey time and travel time for Satellite is 0 mins
           Args:
               site: a site
           Returns:
               list: Daily itinerary:
                   {'site':(dict),
                    'go_to_site': (boolean),
                    'LDAR_mins': (int) travel to and work-onsite mins,
                    'remaining_mins':(int) minutes remaining in survey at site,
                    }
        '''
        return {
            'site': site,
            'go_to_site': True,
            'LDAR_mins': 0,
            'remaining_mins': 0,
        }

    def calc_viewable_sites(self, site_pool):
        """Generic utility function to check whether a satellite can see
           a given patch of ground. Returns True to denote the satellite
           can see the location and False otherwise.
           Args:
               site: a site

           Returns:
               valid_site: boolean
        """
        valid_site = []
        # ind = 0
        sat_date = self.sat_date
        path = self.orbit_path
        date = self.state['t'].current_date.date()
        # find daily pathes
        DP = path[sat_date == date]
        for s in site_pool:
            fac_lat = np.float16(s['lat'])
            fac_lon = np.float16(s['lon'])
            PT = Point(fac_lon, fac_lat)
            for dp in DP:
                if dp.contains(PT):
                    valid_site.append(s)
                    break
        return valid_site

    def assess_weather(self, site):
        """Check whether the site is covered by clound or have enough daylight
            Args:
             site: a site

            Returns:
                valid_site: boolean
        """

        site_lat = np.float16(site['lat'])
        site_lon = np.float16(site['lon'])

        lat_idx = geo_idx(site_lat, self.state['weather'].latitude)
        lon_idx = geo_idx(site_lon, self.state['weather'].longitude)
        ti = self.state['t'].current_timestep

        # check daylight
        date = self.state['t'].current_date
        sr, ss = quick_cal_daylight(date, site_lat, site_lon)

        if sr <= self.state['t'].current_date.hour <= ss:
            sat_daylight = True
        else:
            sat_daylight = False
        # check cloud cover

        CC = self.cloudcover[ti, lat_idx, lon_idx] * 100
        CC = round(CC)
        arr = np.zeros(100)
        arr[:CC] = 1
        np.random.shuffle(arr)

        if np.random.choice(arr, 1)[0] == 0:
            sat_cc = True
        else:
            sat_cc = False

        return (sat_daylight, sat_cc)

    def get_orbit_predictor(self):
        """ Get the orbit predictor of satellite based on
            TLE file and satellite name specified in the input parameter.
        """
        # build a satellite orbit object
        input_directory = self.parameters['input_directory']
        TLEs = []
        with open(input_directory / self.tlefile) as f:
            for line in f:
                TLEs.append(line.rstrip())
        i = 0
        for x in TLEs:
            if x == self.sat:
                break
            i += 1
        TLE_LINES = (TLEs[i+1], TLEs[i+2])
        self.predictor = get_predictor_from_tle_lines(TLE_LINES)
        return

    def get_orbit_path(self):
        '''Get the orbit path polygon for a time interval based on
           orbit predictor of a satellite.
        '''
        # initiate the orbit path
        T1 = self.state['t'].start_date
        T2 = self.state['t'].end_date
        # calculate the orbit path polygon for satellite
        self.sat_datetime, self.orbit_path = init_orbit_poly(
            self.predictor, T1, T2, 15)
        self.sat_date = [d.date() for d in self.sat_datetime]

        self.sat_date = np.array(self.sat_date)
        self.orbit_path = np.array(self.orbit_path)

        return

    def update_schedule(self, work_mins):
        '''Update the time
        '''
        self.state['t'].current_date += timedelta(minutes=int(work_mins))

    def end_day(self, site_pool, itinerary):
        return
