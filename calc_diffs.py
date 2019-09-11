# -*- coding: utf-8 -*-

import h5py
import numpy as np
import networkx as nx

def get_flow_difference(dset, hour1, hour2):
    '''later make flows a list and edges not weighted '''
    flows1 = dset['hour_{}/branches'.format(hour1)]
    flows2 = dset['hour_{}/branches'.format(hour2)]
    if not flows2[:,:2].all() == flows1[:,:2].all(): raise ValueError('branches different between hours') 
    
    flow_diff = flows2[:,2] - flows1[:,2]
    edges = flows1[:,:2]
    N_edges = len(flow_diff)
    #change direction of arrow when the hour_2 flow is negative
    edges = [edges[i] if flows2[i,2]>0 else edges[i][::-1] for i in range(N_edges)]
    #set the edge weight to 1 when there is no flow difference
    flows_widths = [0.8*(abs(flow_diff[i])+0.5) if abs(flow_diff[i])>0 else 1 for i in range(N_edges)]
    
    edge_colors = np.array(['black'] * N_edges)
    edge_colors[flow_diff > 0] = 'green'
    edge_colors[flow_diff < 0] = 'red'
    return flows_widths, edge_colors, edges, flow_diff

def get_supplier_receiver_mask(dset, hour1, hour2, N):
    node_list = dset['hour_1/nodes'][:,0]
    #initialize masks with one row for each hour
    suppliers_mask = np.zeros((2,N), dtype=bool)
    receivers_mask = np.ones((2,N), dtype=bool)
    rest_mask = np.zeros((2,N), dtype=bool)

    for i, h in enumerate([hour1,hour2]):
        gns = dset['hour_{}/gens'.format(h)]
        nds = dset['hour_{}/nodes'.format(h)]
        generation = gns[:,1]
        demand = nds[:,2]
        for gen_idx, gen_node in enumerate(gns[:,0]):
            node_idx = np.where(node_list==gen_node)[0]
            if generation[gen_idx] > demand[node_idx]:
                suppliers_mask[i,node_idx]=True
                receivers_mask[i,node_idx]=False
            elif generation[gen_idx] == demand[node_idx]:
                rest_mask[i,node_idx]=True
                receivers_mask[i,node_idx]=False
        #suppliers_mask[i] = generation > demand
        #receivers_mask[i] = generation < demand
        #rest_mask[i] = ~(suppliers_mask[i]+receivers_mask[i])
    return suppliers_mask, receivers_mask, rest_mask