# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
import h5py
import numpy as np
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import calc_diffs as c_d

g = h5py.File('task_data.hdf5', 'r')
dset = g['results'] 
node_list = dset['hour_1/nodes'][:,0]
N = len(node_list)
#create initial graph from hour_1



#flow difference hour2 - hour1 -> edges' widths
flows, edge_colors, edges = c_d.get_flow_difference(dset, 1, 1)
suppliers_mask, receivers_mask, rest_mask, supplier_nodes, receiver_nodes = \
    c_d.get_supplier_receiver_mask(dset, 1, 1, N)

node_edge_colors = np.array(['darkslategrey'] * N)
node_edge_colors[suppliers_mask[0]] = 'darkgreen'
node_edge_colors[receivers_mask[0]] = 'darkred'

node_colors = np.array(['whitesmoke'] * N)
node_colors[suppliers_mask[1]] = 'lightgreen'
node_colors[receivers_mask[1]] = 'coral'

node_types = np.array(['receivers'] * N)
node_types[suppliers_mask[1]] = 'suppliers'

G = nx.DiGraph()
G.add_nodes_from(node_list)
G.add_weighted_edges_from(edges)

position = graphviz_layout(G, prog='fdp')

#fig_edges = []
#for row in edges:
#    if {'data': {'source': row[0], 'target': row[1]}} not in fig_edges and row[0] != row[1]:
#        fig_edges.append({'data': {'source': row[0], 'target': row[1]}})
#print(fig_edges)
xy = nx.nx_agraph.graphviz_layout(G)
#print('A', flows[:,:2]) #xy[str(edges[0,0])])
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = xy[edge[0]]
    x1, y1 = xy[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color='#888'),
    textposition="top center",
    hoverinfo='text',
    mode='lines+text')

node_x = []
node_y = []

for node in G.nodes():
    x, y = xy[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, 
    y=node_y, 
    name = 'receivers',
    mode='markers+text',
    text=tuple(node_list),
    textposition='top right',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        colorscale='YlGnBu',
        reversescale=True,
        color=node_colors,
        size=15,
        line=dict(width=4,color=tuple(node_edge_colors))
        ))
print(flows[:,2])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
    html.H1("Network Graph")

    ], style={
        'textAlign': "center"
    }),
    html.Div([html.H3("Slide to set hours for Hour_2 - Hour_1 network visualisation:", style={"text-align": "center", 'padding': 10}, className="row"),
              dcc.Slider(id="hour1", min=1, max=len(dset), value=1, step=1, updatemode="drag",
                         marks={i: 'Hour_1: ' if i == 0 else str(i) for i in range(0, len(dset)+1)}, className="row")],
             style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "40%", "padding": 5}),
html.Div([html.Span("", style={"text-align": "center", 'padding': 10}, className="row"),             
             dcc.Slider(id="hour2", min=1, max=len(dset), value=1, step=1, updatemode="drag",
                         marks={i: 'Hour_2: ' if i == 0 else str(i) for i in range(0, len(dset)+1)}, className="row")],
             style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "40%", "padding": 30}),

    html.Div([
        dcc.Graph(id="network-graph",
                  figure={
                      "data": [edge_trace,node_trace],
                      "layout": go.Layout(
                          title='Network Graph',
                          titlefont={'size': 16},
                          showlegend=True,
                          hovermode='closest',
                          margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
                          xaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                          yaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False})

                  })
            ])

], className="container")

@app.callback(
    dash.dependencies.Output("network-graph", "figure"),
    [dash.dependencies.Input("hour1", "value"),
    dash.dependencies.Input("hour2", "value")])
def update_graph(h1,h2):
    flows, edge_colors, edges = c_d.get_flow_difference(dset, h1, h2)
    suppliers_mask, receivers_mask, rest_mask, supplier_nodes, receiver_nodes = \
    c_d.get_supplier_receiver_mask(dset, h1, h2, N)
    node_edge_colors = np.array(['darkslategrey'] * N)
    node_edge_colors[suppliers_mask[0]] = 'darkgreen'
    node_edge_colors[receivers_mask[0]] = 'darkred'

    node_colors = np.array(['whitesmoke'] * N)
    node_colors[suppliers_mask[1]] = 'lightgreen'
    node_colors[receivers_mask[1]] = 'coral'

    node_types = np.array(['receivers'] * N)
    node_types[suppliers_mask[1]] = 'suppliers'
    
    G = nx.DiGraph()
    G.add_nodes_from(node_list)
    G.add_weighted_edges_from(edges)
    node_trace = go.Scatter(
    x=node_x, y=node_y, 
    mode='markers+text',
    text=tuple(node_list),
    textposition='top right',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        colorscale='YlGnBu',
        reversescale=True,
        color=node_colors,
        size=15,
        line=dict(width=4,color=tuple(node_edge_colors))
        ))

    figure = {"data": [edge_trace, node_trace],
              "layout": go.Layout(
                          title='Network Graph',
                          titlefont={'size': 16},
                          showlegend=False,
                          hovermode='closest',
                          margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
                          xaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                          yaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                        annotations= [ dict(showarrow=True, arrowsize=0.9, arrowwidth=flows[i,2], arrowhead=5, 
                        standoff=14, startstandoff=4, arrowcolor=edge_colors[i],
                        ax=xy[edge[0]][0], ay=xy[edge[0]][1], axref='x', ayref='y',
                        x=xy[edge[1]][0], y=xy[edge[1]][1], xref='x', yref='y'
                        ) for i, edge in enumerate(flows[:,:2])])
                  }
    return figure
#server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)