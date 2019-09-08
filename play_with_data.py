# -*- coding: utf-8 -*-

import h5py
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

g = h5py.File('task_data.hdf5', 'r')
# print(list(f.keys()))
#dset = f['results']
# hours = list(dset.keys())
#first = dset['hour_1/nodes'][:,1] #node_type is 1,2 or 3
#print(list(first))
# nodes_id = dset['hour_1/nodes'][:,0]
# for hour in dset:
#     print(hour)
#     assert nodes_id.all()==dset['{}/nodes'.format(hour)][:,0].all()


# g = h5py.File("mytestfile2.hdf5", "w")
# hour1 = g.create_group("results/hour_1")
# hour2 = g.create_group("results/hour_2")

# nodes = hour1.create_dataset("nodes", (4,3))
# nodes[...] = [[1,1,1], [2,1,2], [3,2,2], [4,3,3]]
# gens = hour1.create_dataset("gens", (4,3))
# gens[...] = [[1,2,20],[2,2,30],[3,1,15],[4,1,17]]
# branches = hour1.create_dataset("branches", (4,3))
# branches[...] = [[1,2,4],[1,3,-1],[1,4,2],[2,4,1]]

# nodes2 = hour2.create_dataset("nodes", (4,3))
# nodes2[...] = [[1,1,1], [2,1,3], [3,1,2], [4,3,2]]
# gens = hour2.create_dataset("gens", (4,3))
# gens[...] = [[1,2,20],[2,3,30],[3,1,15],[4,1,17]]
# branches = hour2.create_dataset("branches", (4,3))
# branches[...] = [[1,2,3],[1,3,-1],[1,4,1],[2,4,3]] 

# g = h5py.File("mytestfile2.hdf5", "r")
dset = g['results'] 
#flow difference hour2 - hour1 -> edges' weights
flows1 = g['results/hour_1/branches']
flows2 = g['results/hour_2/branches']
assert(flows2[:,:2].all() == flows1[:,:2].all()) #check if branches didn't change
flow_diff = flows2[:,2] - flows1[:,2]
flows = flows1[:]
M = len(flow_diff)
#print([flow_diff[i] if abs(flow_diff[i])>0 else 1 for i in range(M)])
flows[:,2] = [flow_diff[i] if abs(flow_diff[i])>0 else 1 for i in range(M)]

edge_colors = np.array(['k'] * M)
edge_colors[flow_diff > 0] = 'g'
edge_colors[flow_diff < 0] = 'r'
#print(flow_diff)

#edges = tuple(flows)
edges = tuple(flows[:,:2])
weights = flows[:,2]

node_list = dset['hour_1/nodes'][:,0]
N = len(node_list)
suppliers_mask = np.zeros((2,N), dtype=bool)
receivers_mask = np.ones((2,N), dtype=bool)
rest_mask = np.zeros((2,N), dtype=bool)
supplier_nodes = [[],[]]
receiver_nodes = [[],[]]

for i in [0,1]:
    gns = dset['hour_{}/gens'.format(i+1)]
    nds = dset['hour_{}/nodes'.format(i+1)]
    generation = gns[:,1]
    demand = nds[:,2]
    for j,gen_node in enumerate(gns[:,0]):
        print(gen_node)
        #same_node = nds[node_list==gen_node,:]
        node_idx = np.where(node_list==gen_node)[0]
        print(node_idx)
        if generation[j] > demand[node_idx]:
            suppliers_mask[i,node_idx]=True
            receivers_mask[i,node_idx]=False
        elif generation[j] == demand[node_idx]:
            rest_mask[i,node_idx]=True
            receivers_mask[i,node_idx]=False
    print(node_list,generation,demand)
    #suppliers_mask[i] = generation > demand
    #receivers_mask[i] = generation < demand
    #rest_mask[i] = ~(suppliers_mask[i]+receivers_mask[i])
    supplier_nodes[i] = nds[suppliers_mask[i,:],0].tolist()
    receiver_nodes[i] = nds[receivers_mask[i,:],0].tolist() 

node_edge_colors = np.array(['black'] * N)
node_edge_colors[suppliers_mask[0]] = 'y'
node_edge_colors[receivers_mask[0]] = 'coral'

G = nx.DiGraph()
G.add_nodes_from(dset['hour_1/nodes'][:,0])
G.add_edges_from(edges)
#weights = [G[u][v]['weight'] for u,v in G.edges()]

#print(weights)

#M = G.number_of_edges()
#nodes = demand - generation -> zero/pobiera/generuje/zmienił w dol/zmienil w gore
#edges = flow2-flow1
position = nx.single_source_shortest_path_length(G, 5)
nx.draw_networkx_nodes(G,position, nodelist=supplier_nodes[1], \
    node_color="g", edgecolors=node_edge_colors[suppliers_mask[0]], linewidths=4)
nx.draw_networkx_nodes(G,position, nodelist=receiver_nodes[1], \
    node_color="r", edgecolors=node_edge_colors[receivers_mask[0]],linewidths=4)
nx.draw_networkx_nodes(G,position, nodelist=node_list[rest_mask[1].tolist()], \
    node_color="b",edgecolors=node_edge_colors[rest_mask[0].tolist()], linewidths=4)
#here maybe different colour for edges which are ositive and negative and width with abs (without mean)
nx.draw_networkx_edges(G,position, width=weights, edge_color=edge_colors)
nx.draw_networkx_labels(G,position)

plt.show()
