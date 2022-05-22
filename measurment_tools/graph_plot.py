configured = [{'conn':  1, 'latency':  0.173 , 'tps':  5783.689994, 'init_conn_time':  2.495 },
{'conn':  10, 'latency':  0.699 , 'tps':  14297.969688, 'init_conn_time':  6.524 },
{'conn':  20, 'latency':  1.399 , 'tps':  14292.860716, 'init_conn_time':  10.591 },
{'conn':  30, 'latency':  1.982 , 'tps':  15133.171913, 'init_conn_time':  16.477 },
{'conn':  40, 'latency':  3.087 , 'tps':  12957.563978, 'init_conn_time':  20.456 },
{'conn':  50, 'latency':  3.896 , 'tps':  12833.346167, 'init_conn_time':  23.310 },
{'conn':  60, 'latency':  4.360 , 'tps':  13761.152267, 'init_conn_time':  27.334 },
{'conn':  70, 'latency':  5.599 , 'tps':  12501.785969, 'init_conn_time':  44.402 },
{'conn':  80, 'latency':  5.777 , 'tps':  13846.819559, 'init_conn_time':  44.140 },
{'conn':  90, 'latency':  6.266 , 'tps':  14363.230131, 'init_conn_time':  47.105 },
{'conn':  100, 'latency':  7.061 , 'tps':  14163.302882, 'init_conn_time':  53.840 },
{'conn':  110, 'latency':  7.809 , 'tps':  14085.769531, 'init_conn_time':  59.610 },
{'conn':  120, 'latency':  8.438 , 'tps':  14222.053665, 'init_conn_time':  57.471 },
{'conn':  150, 'latency':  10.476 , 'tps':  14317.758793, 'init_conn_time':  84.946 },
{'conn':  200, 'latency':  14.353 , 'tps':  13934.757466, 'init_conn_time':  110.583 },
#{'conn':  500, 'latency':  40.940 , 'tps':  12212.875302, 'init_conn_time':  245.642 },
#{'conn':  700, 'latency':  51.424 , 'tps':  13612.321095, 'init_conn_time':  351.849 },
#{'conn':  1000, 'latency':  158.379 , 'tps':  6313.956432, 'init_conn_time':  488.324 }
]

default = [{'conn':  1, 'latency':  0.224 , 'tps':  4458.314757, 'init_conn_time':  2.318 },
{'conn':  10, 'latency':  0.942 , 'tps':  10621.348911, 'init_conn_time':  8.136 },
{'conn':  20, 'latency':  1.739 , 'tps':  11497.556769, 'init_conn_time':  14.824 },
{'conn':  30, 'latency':  2.513 , 'tps':  11939.348112, 'init_conn_time':  17.622 },
{'conn':  40, 'latency':  3.337 , 'tps':  11985.377839, 'init_conn_time':  23.986 },
{'conn':  50, 'latency':  3.718 , 'tps':  13449.175566, 'init_conn_time':  25.445 },
{'conn':  60, 'latency':  4.583 , 'tps':  13092.718267, 'init_conn_time':  27.266 },
{'conn':  70, 'latency':  5.183 , 'tps':  13505.691684, 'init_conn_time':  36.312 },
{'conn':  80, 'latency':  5.971 , 'tps':  13398.315162, 'init_conn_time':  47.702 },
{'conn':  90, 'latency':  6.651 , 'tps':  13531.799729, 'init_conn_time':  48.288 },
{'conn':  100, 'latency':  8.860 , 'tps':  11286.426943, 'init_conn_time':  61.284 },
{'conn':  110, 'latency':  9.675 , 'tps':  11369.509044, 'init_conn_time':  84.475 },
{'conn':  120, 'latency':  8.855 , 'tps':  13551.818767, 'init_conn_time':  63.976 },
{'conn':  150, 'latency':  11.081 , 'tps':  13536.440097, 'init_conn_time':  77.027 },
{'conn':  200, 'latency':  14.934 , 'tps':  13392.259274, 'init_conn_time':  113.667 },
#{'conn':  500, 'latency':  41.423 , 'tps':  12070.588803, 'init_conn_time':  355.406 },
#{'conn':  700, 'latency':  56.567 , 'tps':  12374.640472, 'init_conn_time':  410.918 },
#{'conn':  1000, 'latency':  177.330 , 'tps':  5639.194204, 'init_conn_time':  584.393 }
]
import matplotlib.pyplot as plt

x = [x['conn'] for x in default]
y = [x['latency'] for x in default]

q = [x['conn'] for x in configured]
w = [x['latency'] for x in configured]

fig, ax = plt.subplots()

default_f, = ax.plot(x, y, label='default')
configured_f, = ax.plot(q, w, label='configured')
ax.legend(handles=[default_f, configured_f])
plt.ylabel('latency, ms')
plt.xlabel('connections count')
plt.show()