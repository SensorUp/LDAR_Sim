
# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        methods.deployment.orbit_company
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
from methods.crew import BaseCrew


def make_crews(crews, config, state, parameters, timeseries, deployment_days):
    """ Generate crews using BaseCrew class.

    Args:
        crews (list): List of crews
        config (dict): Method parameters
        state (dict): Current state of LDAR-Sim
        parameters (dict): Program parameters
        timeseries (dict): Timeseries
        deployment_days (list): days method can be deployed based on weather

    --- Required in module.company.BaseCompany ---
    """
    for i in range(config['n_crews']):
        crews.append(BaseCrew(state, parameters, config,
                              timeseries, deployment_days, id=i + 1))


class Schedule():
    def __init__(self, config, parameters, state):
        self.parameters = parameters
        self.config = config
        self.state = state

    def get_due_sites(self, site_pool):
        return site_pool

    def assign_agents(self):
        '''
        can be used to assign sites to two different satellites in the future
        for exmaple, GHG-Sat1 and GHG-Sat2 work together
        '''
        return

    def get_working_crews(self, site_pool, n_crews):
        return n_crews

    def get_crew_site_list(self, site_pool, crew_num, n_crews, crews=None):
        return site_pool
