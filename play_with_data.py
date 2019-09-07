# -*- coding: utf-8 -*-

import h5py
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

#f = h5py.File('task_data.hdf5', 'r')
# print(list(f.keys()))
#dset = f['results']
# hours = list(dset.keys())
#first = dset['hour_1/nodes'][:,1] #node_type is 1,2 or 3
#print(list(first))
# nodes_id = dset['hour_1/nodes'][:,0]
# for hour in dset:
#     print(hour)
#     assert nodes_id.all()==dset['{}/nodes'.format(hour)][:,0].all()


g = h5py.File("mytestfile.hdf5", "r")
#day1 = g.create_group("results/day_1")
#day2 = g.create_group("results/day_2")
#nodes = day1.create_dataset("nodes", (4,3))
#nodes[...] = [[1,1,1], [2,1,2], [3,2,2], [4,3,3]]
#gens = day1.create_dataset("gens", (4,3))
#gens[...] = [[1,2,20],[2,2,30],[3,1,15],[4,1,17]]
#branches = day1.create_dataset("branches", (4,3))
#branches[...] = [[1,2,4],[1,3,-1],[1,4,2],[2,4,1]]
#print(g['results/nodes'][:])
#nodes2 = day2.create_dataset("nodes", (4,3))
#nodes2[...] = [[1,1,1], [2,1,3], [3,1,2], [4,3,2]]
#gens = day2.create_dataset("gens", (4,3))
#gens[...] = [[1,2,20],[2,3,30],[3,1,15],[4,1,17]]
#branches = day2.create_dataset("branches", (4,3))
#branches[...] = [[1,2,3],[1,3,-1],[1,4,1],[2,4,2]]


dset = g['results'] 
#flow difference day2 - day1 -> edges' weights
flows1 = g['results/day_1/branches']
flows2 = g['results/day_2/branches']
assert(flows2[:,:2].all() == flows1[:,:2].all()) #check if branches didn't change
flow_diff = flows2[:,2] - flows1[:,2]
flows = flows1[:]
flows[:,2] = flow_diff + np.mean(flows1[:,2])

edges = tuple(flows)
weights = flows[:,2]

node_list = dset['day_1/nodes'][:,0]
N = len(node_list)
givers_list_mask = np.empty((2,N), dtype=bool)
takers_list_mask = np.empty((2,N), dtype=bool)
rest_mask = np.empty((2,N), dtype=bool)
supplier_nodes = [[],[]]
receiver_nodes = [[],[]]

for i in [1,2]:
    generation = dset['day_{}/gens'.format(i)][:,1]
    demand = dset['day_{}/nodes'.format(i)][:,2]
    givers_list_mask[i-1] = generation > demand
    takers_list_mask[i-1] = generation < demand
    rest_mask[i-1] = ~(givers_list_mask[i-1]+takers_list_mask[i-1])
    supplier_nodes[i-1] = dset['day_{}/nodes'.format(i)][givers_list_mask[i-1,:],0].tolist()
    receiver_nodes[i-1] = dset['day_{}/nodes'.format(i)][takers_list_mask[i-1,:],0].tolist() 

edge_colors = np.array(['black']*N)
edge_colors[givers_list_mask[0]] = 'y'
edge_colors[takers_list_mask[0]] = 'red'

#print(givers_list_mask1, takers_list_mask1,rest_mask1)
#print(edge_colors[givers_list_mask1])
#print(receiver_nodes1)
#nodeList_same = [nd for i,nd in enumerate(dset['day_1/nodes'][:,0]) \
#    if dset['day_1/nodes'][i,2]== dset['day_2/nodes'][i,2]]
#nodeList_less = list(dset['day_1/nodes'][:,0])
#for j in nodeListA:
#    nodeListB.remove(j)  
#print(nodeListB)
G = nx.DiGraph()
G.add_nodes_from(dset['day_1/nodes'][:,0])
G.add_weighted_edges_from(edges)
#weights = [G[u][v]['weight'] for u,v in G.edges()]

#print(weights)

#M = G.number_of_edges()
#nodes = demand - generation -> zero/pobiera/generuje/zmienił w dol/zmienil w gore
#edges = flow2-flow1
position = nx.circular_layout(G)
nx.draw_networkx_nodes(G,position, nodelist=supplier_nodes[1], \
    node_color="g", edgecolors=edge_colors[givers_list_mask[0]], linewidths=4)
nx.draw_networkx_nodes(G,position, nodelist=receiver_nodes[1], \
    node_color="r", edgecolors=edge_colors[takers_list_mask[0]],linewidths=4)
nx.draw_networkx_nodes(G,position, nodelist=node_list[rest_mask[1].tolist()], \
    node_color="b",edgecolors=edge_colors[rest_mask[0].tolist()], linewidths=4)
#here maybe different colour for edges which are ositive and negative and width with abs (without mean)
nx.draw_networkx_edges(G,position, width=weights)
nx.draw_networkx_labels(G,position)
plt.show()
