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

#flow difference hour2 - hour1 -> edges' widths
flows_widths, edge_colors, edges, flow_diff = c_d.get_flow_difference(dset, 1, 1)
g_edges = tuple(edges)

G = nx.DiGraph()
G.add_nodes_from(node_list)
G.add_edges_from(g_edges)

xy = nx.nx_agraph.graphviz_layout(G)
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
    mode='lines')

node_x = []
node_y = []

for node in G.nodes():
    x, y = xy[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y, 
    mode='markers+text',
    text=tuple(node_list),
    textposition='middle center',
    marker=dict(size=26))

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
    html.H1("Mapa różnic w działaniu sieci"),
    html.H3("Wybierz stan początkowy (godz_A) oraz stan końcowy (godz_B), \
         aby zobaczyć różnice w działaniu sieci"),
   html.P("Strzałki pokazują kierunek przepływu prądu między węzłami: \
        zielony kolor strzałki oznacza wyższy przepływ prądu w godz_B, \
            czerwony kolor strzałki oznacza niższy przepływ w godz_B, \
                kolor czarny oznacza brak zmian. \
                    Grubość strzałki odzwierciedla skalę zmiany w przepływach."), 

    html.P("Kolor węzła pokazuje czy liczba MW, które wyprodukował dany węzeł przewyższa jego zapotrzebowanie \
        (generator/receiver). \
        Kolor krawędzi odpowiada sytuacji w Godz_A, kolor wypełnienia odpowiada sytuacji w Godz_B.")], 
                    style = {'padding' : '50px' , 'backgroundColor' : 'lightcyan'}),

    html.Div([html.H3("Ustaw godziny do wizualizacji:", style={"text-align": "center", 'padding': 10}, className="row"),
              dcc.Slider(id="hour1", min=1, max=len(dset), value=1, step=1, 
                        updatemode="drag",
                        marks={i: 'Godz_A: ' if i == 0 else str(i) for i in range(0, len(dset)+1)}, className="row")],
            style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "50%", "padding": 5}),

    html.Div([dcc.Slider(id="hour2", min=1, max=len(dset), value=1, step=1, 
                        updatemode="drag",
                        marks={i: 'Godz_B: ' if i == 0 else str(i) for i in range(0, len(dset)+1)}, className="row")],
            style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "50%", "padding": 30}),

    html.Div([
        dcc.Graph(id="network-graph",
                  figure={
                      "data": [edge_trace,node_trace],
                      "layout": go.Layout(
                          height=750,
                          hovermode='closest',
                          margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
                          xaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                          yaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False})},
                    style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "100%"})
            ])

], className="container")

@app.callback(
    dash.dependencies.Output("network-graph", "figure"),
    [dash.dependencies.Input("hour1", "value"),
    dash.dependencies.Input("hour2", "value")])
def update_graph(h1,h2):
    flows_widths, edge_colors, edges, flow_diff = c_d.get_flow_difference(dset, h1, h2)
    suppliers_mask, receivers_mask, rest_mask = c_d.get_supplier_receiver_mask(dset, h1, h2, N)
    
    node_edge_colors = np.array(['darkslategrey'] * N)
    node_edge_colors[suppliers_mask[0]] = 'darkgreen'
    node_edge_colors[receivers_mask[0]] = 'darkred'

    node_colors = np.array(['whitesmoke'] * N)
    node_colors[suppliers_mask[1]] = 'lightgreen'
    node_colors[receivers_mask[1]] = 'coral'

    node_types = np.array(['receiver '] * N)
    node_types[suppliers_mask[1]] = 'generator'
    node_types[rest_mask[1]] = 'generation = demand'

    node_strings = [str(int(node)) for node in node_list]

    G = nx.DiGraph()
    G.add_nodes_from(node_list)
    G.add_edges_from(edges)
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        # to get explicit values of flow difference use flow_diff
        # textposition="top center", 
        # hovertext=tuple(flow_diff), 
        # hoverinfo='text',
        mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers+text',
        text=tuple(node_strings),
        textposition='middle center',
        hovertext=tuple(node_types),
        hoverinfo='text',
        marker=dict(
            color=node_colors,
            size=26,
            line=dict(width=4,color=tuple(node_edge_colors))
        ))

    figure = {"data": [edge_trace, node_trace],
              "layout": go.Layout(
                          showlegend=False,
                          hovermode='closest',
                          height=750,
                          margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
                          xaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                          yaxis={'showgrid': False,
                                 'zeroline': False, 'showticklabels': False},
                        annotations= [ dict(showarrow=True, arrowsize=0.8, arrowwidth=flows_widths[i], arrowhead=5, 
                        standoff=18, startstandoff=14, arrowcolor=edge_colors[i],
                        ax=xy[edge[0]][0], ay=xy[edge[0]][1], axref='x', ayref='y',
                        x=xy[edge[1]][0], y=xy[edge[1]][1], xref='x', yref='y'
                        ) for i, edge in enumerate(edges)])
                  }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)