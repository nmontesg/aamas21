#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:03:17 2020

@author: Nieves Montes

@description: Compute the alignmnet given a model.
"""

import numpy as np
import multiprocessing as mp

from tax_model import Society

length = 10  # length of the paths for evaluation of alignment
paths = 500  # number of paths for evaluation of fitness


def equality_single_path(model):
  """
	Evaluate a model by its alignment with respect to equality after one path.
	"""
  for _ in range(length):
    model.step()
  agent_wealths = [agent.wealth for agent in model.agents]
  numerator = sum([sum([abs(x_i - x_j) for x_j in agent_wealths])
                  for x_i in agent_wealths])
  gini_index = numerator / (2 * model.num_agents ** 2 * np.mean(agent_wealths))
  return (1 - 2*gini_index)


def fairness_single_path(model):
  """
  Evaluate a model by its alignment with respect to fairness after one path.
  """
  for _ in range(length):
    model.step()
  evaders = [ag for ag in model.agents if ag.is_evader]
  evaders_segment = [True for ev in evaders if ev.segment == 0]
  proportion = len(evaders_segment) / model.num_evaders
  return (2*proportion - 1)


def compute_alignment(model, value):
  """
  Compute the alignment by sampling over many paths, use the alignment function
  for the input value.
  """
  model_params = {
    'num_agents': model.num_agents,
    'num_evaders': model.num_evaders,
    'collecting_rates': model.collecting_rates,
    'redistribution_rates': model.redistribution_rates,
    'invest_rate': model.invest_rate,
    'catch': model.catch,
    'fine_rate': model.fine_rate
  }
  models = [Society(**model_params) for _ in range(paths)]
  pool = mp.Pool(mp.cpu_count())
  results = pool.map(globals()[value+'_single_path'], [m for m in models])
  pool.close()
  return np.mean(results)
