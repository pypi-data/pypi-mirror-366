# File for dimensioning of an ejector with R1233zd cooling fluid.

# R1233zde		A
# 	Mprim [kg/s]	0.57
# 	Msec [kg/s]	0.265
# 	Pprim [bar]	20.07
# 	Psec	2.763
# 	Tprim
# 	Tsec
# 	hprim [kJ/kg]	365.5
# 	hsec [kJ/kg]	437.1
# 	q_out	0.6838


# ! python -m site
### installing package in jupyter notebook
# import sys # replace the path below with the location of your .whl file :
#!{sys.executable} -m pip install C:\Users\BuruzsA\PycharmProjects\flows1d\dist\flows1d-1.0.0b4-py3-none-any.whl
## if you want to uninstall for test/updates


import logging
import sys
logging.basicConfig(stream = sys.stdout, level = logging.INFO)


#sys.path.append("C:/Users/BuruzsA/PycharmProjects/")
#sys.path.append("C:/Users/BuruzsA/PycharmProjects/flows1d") ## this is not needed, if the package is installed in jupyter
from simpy_ejector import nozzleFactory, NozzleParams, nozzleSolver, EjectorGeom, refProp, EjectorMixer
from simpy_ejector.useCases import ejectorSimulator

import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import time
import importlib
import math
import logging

logging.basicConfig(stream=sys.stdout, level= logging.INFO)

# get_ipython().run_line_magic('matplotlib', 'notebook')
#
# from IPython.display import Image
# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:100% !important; }</style>"))
# display(HTML("<style>div.output_scroll { height: 44em; }</style>"))
from time import time
t0 = time()


pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 140)
np.core.arrayprint._line_width = 180
np.set_printoptions(linewidth= 180)

# get_ipython().run_cell_magic('html', '', '<style type = "text/css">\n/* Any CSS style can go in here. */\nbody {\n font-family: sans-serif;\n font-size: 19px;}\n.dataframe th {\n    font-size: 18px;\n}\n.dataframe td {\n    font-size: 20px;\n}\n.CodeMirror{\nfont-size:20px;}\n\n</style>')

# params = { "Rin": 1.0, "Rt": 0.22, "Rout": 0.345, "gamma_conv": 15.0, "" "Dmix": 1.4,
#            "pin": 2140, "Tin" : 409, "Tsuc": 336.25, "Psuc" : 430  }
# Rout = 18 * math.tan( 6.0 * math.pi/180) + 1.53


fluid = "R1233zde"  ## Manuel : "R1233zde" from Refprop 10.0 !
RP = refProp.setup(fluid)
params = { "Rin": 0.97, "Rt": 0.1534, "Rout": 0.3428, "gamma_conv": 15.7, "gamma_div" : 6, "Dmix": 2,
           "Pprim": 1800, "hprim" : 368.0, "hsuc": 436.628, "Psuc" : 150 , "A_suction_inlet" : 5.9,
           "mixerLen": 11.2 , "gamma_diffusor": 2.5, "diffuserLen": 25.194}
primQ = refProp.getTD(RP, hm= params["hprim"], P=params["Pprim"] )
params["Tprim"] = primQ['T']
params["Tsuc"] = refProp.getTD(RP, hm= params["hsuc"], P=params["Psuc"] )['T']

[Din, hin] = refProp.getDh_from_TP(RP, params['Tprim'], params['Pprim'])


#params["Rin"] = 1.1  # cm
#params["Rt"]  = 0.29 # smaller throat -> smaller critical primary mass flow rate
# params["Rout"] = 0.87 # 0.468  cm radius
# params["Dmix"] = 2.67
# params["A_suction_inlet"] = 16
# params["gamma_conv"] = 15.0 # degree
# params["gamma_div"] = 7.0
params["mixingParams"] = {'massExchangeFactor': 2.e-4, 'dragFactor': 0.01, 'frictionInterface': 0.0,
                        'frictionWall': 0.0015}
#ejector = makeEjectorGeom(params)
esim = ejectorSimulator.ejectorSimu(params, fluid = "R1233zde")
recalc = True
if recalc :
    esim.calcPrimMassFlow()
else:
    esim.params['vin_crit']= 0.371484375
    esim.params['mass_flow_crit'] = 0.10340564176831657
    esim.makeEjectorGeom(params)
ejplot = esim.ejector.draw()
print(esim.params)

esim.makeEjectorGeom(params)
res_crit = esim.motiveSolver()
print(f"By the motive nozzle exit:\n {res_crit.iloc[-1]}")
esim.premix(res_crit) # this sets the mixer, that is needed for the mixing calculation
print(f"suction MFR [g/s] {round(esim.mixerin['massFlowSecond'],3)}")

# esim.mixer.mixingParams = {'massExchangeFactor': 0.e-4, 'dragFactor': 0.01, 'frictionInterface': 0.001,
#                     'frictionWall': 0.00}
# params["gamma_diffusor"] = 2.0
# params["diffuserLen"] = 30
esim.makeEjectorGeom(params)
esim.premix(res_crit)
esim.mixersolve()
diffusor_out = esim.solMix.iloc[-1]
out_prim = refProp.getTD(esim.RP, hm= diffusor_out["hp"], P=diffusor_out["p"] )
out_sec =  refProp.getTD(esim.RP, hm= diffusor_out["hs"], P=diffusor_out["p"] )
print(diffusor_out)
## we would need to reach this quality at the end: 1/q = 1 + entrainment_ratio
q_need = 1.0/ (1.0 + esim.mixerin["massFlowSecond"]/ esim.mixerin["massFlowPrim"]  )
print(f"needed vapor quality = {round(q_need, 3)}. calculated {round(esim.outlet_quality,3)}")

esim.mixer.plotSolution(res_crit, esim.solMix, "no shock in mixer",  ejplot)

## maybe something wrong with the mixing formula? Too high primary mass flow rate at the end!
esim.massFlowCheck()
esim.plotMixSolution(res_crit, esim.solMix, "simpy_ejector 1D Ejector flow solution")
print( f"MFR prim {esim.mixerin['massFlowPrim']} sec {esim.mixerin['massFlowSecond']} "
       f"sum {round(esim.mixerin['massFlowPrim'] + esim.mixerin['massFlowSecond'],3)} g/sec ")
print(f"  {(esim.solMix['MFRp'] + esim.solMix['MFRs']).head(3)}")
print(f" mixer prim sec MFR in kg/s {[round(esim.solMix[k].iloc[1],3) for k in ['MFRp', 'MFRs']] } ")
print(f"secondary density {round(esim.mixerin['Dsy'],3)}")
mixerin_sec =  refProp.getTD(esim.RP, hm= esim.mixerin["hsy"], P=esim.mixerin["py"] )
print(f"this should be equal with {mixerin_sec}")
print(esim.mixerin['massFlowSecond'],esim.mixerin['massFlowPrim'])
print(esim.mixerin['massFlowSecond']/esim.mixerin['massFlowPrim'])
print(esim.solMix['p'][199]/params['Psuc'])
