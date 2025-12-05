from brian2 import *
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

#parametry do symulacji pojedynczego neuronu
n = 20
inhib = 0.2
n_inhib = int(n*inhib)
n_exc = n-n_inhib

tau = 10*ms
v_th = -50*mV
v_reset = -65*mV
EL = -65*mV

#E I reversal potentials
Ee = 0*mV
Ei = 0*mV

eqs = '''
dv/dt = (EL-v+ge*(Ee-v)+gi*(Ei-v))/tau:volt #równanie napięcia błonowego
dge/dt = -ge/(5*ms):1 #rozkład przewodnictwa pobudzającego
dgi/dt=-gi/(10*ms):1 #rozkład przewodnictwa hamującego
'''
#grupy neuronów
G = NeuronGroup(n, eqs, threshold='v>v_th', reset='v=v_reset', method='euler')
#randomowe początkowe napięcia
G.v = EL + (np.random.rand(n) - 0.5)*10*mV
#synapsy
s = Synapses(G, G,
             model='w : 1',                # synaptic weight variable
             on_pre='ge_post += w',        # or gi_post for inhibitory neurons
             delay=1*ms)
s.connect(condition='i!=j', p=0.2)
#wagi
w_exc = 0.6
w_inh = -1.5
#wagi pobudzających
for i in range(n_exc):
    s.w[i,:] = w_exc
#wagi hamujących
for i in range(n_exc, n):
    s.w[i,:] = w_inh
#monitors
m = SpikeMonitor(G)
state=StateMonitor(G, 'v', record = 0) # trackowanie neuronu 0
#run
run(1*second)
#tworzenie grafu z brian2
G_nx = nx.DiGraph()
#dodanie węzłów
for i in range(n):
    if i <n_exc:
        G_nx.add_node(i, type='E')
    else:
        G_nx.add_node(i, type='I')
#dodanie linii między synapsami
#.i[:] = presyn index array, S.j[:] = postsyn index array
for pre, post in zip(s.i[:], s.j[:]):
    G_nx.add_edge(int(pre), int(post))
#wizualizacja
pos = nx.spring_layout(G_nx, seed=2)
node_colors = ['tab:blue' if n < n_exc else 'tab:red' for n in G_nx.nodes()]
plt.figure(figsize=(6,6))
nx.draw_networkx(
    G_nx,
    pos,
    node_color=node_colors,
    with_labels=True,
    node_size=400,
    arrowsize=12
)
plt.title("E/I Local Circuit Connectivity")
plt.axis("off")
plt.show()

plt.figure(figsize=(8,4))
plt.scatter(m.t/ms, m.i, s=3)
plt.xlabel("time in ms")
plt.ylabel("Neuron index")
plt.title("Raster plot of local circuit")
plt.show()

