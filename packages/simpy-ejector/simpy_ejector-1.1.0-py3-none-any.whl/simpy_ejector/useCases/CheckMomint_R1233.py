#  Copyright (c) 2023.   Adam Buruzs
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import logging
import sys
logging.basicConfig(stream = sys.stdout, level = logging.INFO)
import matplotlib.pyplot as plt
import pandas as pd
from simpy_ejector.useCases import ejectorSimulator
from simpy_ejector import refProp

logging.getLogger('matplotlib').setLevel("INFO")

# load Refprop for your fluid:
fluid = "R1233zde" # on Refprop 10 you have this, with Refprop 9 use "R1233zd"
RP = refProp.setup(fluid)

# import os, numpy as np
# from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
# RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
# RP.SETPATHdll(os.environ['RPPREFIX'])
# print(RP.RPVersion())
# r = RP.SETUPdll(1, fluid + ".FLD", "HMX.BNC", "DEF")
# print( fluid + ".FLD")

# params = { "Rin": 0.97, "Rt": 0.153, "Rout": 0.3422, "gamma_conv": 15.7, "gamma_div" : 6.0, "Dmix": 2.0,
#            "pin": 1800, "Tin" : 400, "Tsuc": 317.25, "Psuc" : 150  }

import math
# Asucin = 2 * 1.979 * 0.475 * math.pi
Asucin = 10.0
# set up geometry parameters:
params = {  "Rin": 0.97, "Rt": 0.153, "Rout": 0.3422, "gamma_conv": 15.7, "gamma_div" : 6.0, "Dmix": 2.0,
           "Pprim": 1800, "Tprim" : 400, "Tsuc": 317.25, "Psuc" : 150 , "A_suction_inlet" : Asucin ,
           "mixerLen": 11.2 , "gamma_diffusor": 2.5, "diffuserLen": 30}
## calculate Temperatures from specific enthalpy with Refprop:
# Dprim, hp = refProp.getDh_from_TP(RP, params['Tprim'], params['Pprim'] )
# params['hprim'] = hp
# Dsuc, hs = refProp.getDh_from_TP(RP, params['Tsuc'], params['Psuc'] )
# params['hsuc'] = hs



# primQ = refProp.getTD(RP, hm= params["hprim"], P=params["Pprim"] )
# params["Tprim"] = primQ['T']
# params["Tsuc"] = refProp.getTD(RP, hm= params["hsuc"], P=params["Psuc"] )['T']

# set parameters of the mixing calculations:
params["mixingParams"] = {'massExchangeFactor': 2.e-4, 'dragFactor': 0.01, 'frictionInterface': 0.0,
                        'frictionWall': 0.0015}

# create a simulator object:
esim = ejectorSimulator.ejectorSimu(params = params, fluid= fluid)
# plot the ejector geometry:
ejplot = esim.ejector.draw()
recalc = False
if recalc:
    ## calculate the primary mass flow rate:
    esim.calcPrimMassFlow()
else:
    esim.params['vin_crit'] = 0.3697265625
    esim.params['mass_flow_crit'] = 0.10295384643183664
    esim.makeEjectorGeom(params)

# esim.makeEjectorGeom(params)
## calculate the critical (= choked flow) solution in the motive nozzle:
res_crit = esim.motiveSolver()
print(f"By the motive nozzle exit:\n {res_crit.iloc[-1]}")
# solve the pre-mixing equations:
#esim.mixer.momCalcType = 1
esim.premix(res_crit) # this sets the mixer, that is needed for the mixing calculation
print(f"suction MFR [g/s] {round(esim.mixerin['massFlowSecond'],3)}")

fullres = pd.DataFrame() ## collect the premix results to this dataframe
resline = {"calctype" : 0, "Nint": 0}
resline.update(esim.mixerin)
fullres = fullres.append(resline, ignore_index=True)

print(f"premix calculation type 1:")
esim.mixer.momCalcType =1
esim.mixerin = esim.mixer.premixWrapSolve(res_crit, esim.params["Psuc"], esim.params["Tsuc"])
resline = {"calctype" :1, "Nint": 0}
resline.update(esim.mixerin)
fullres = fullres.append(resline, ignore_index=True)

Dsuc = refProp.getTD( esim.RP, hm = esim.params["hsuc"] , P=esim.params["Psuc"] )['D']
esim.mixer.momCalcType = 2

for kk in range(1,15):
##for kk in [10]:
    try:
        esim.mixer.Nint = kk
        esim.mixerin = esim.mixer.premixWrapSolve(res_crit, esim.params["Psuc"], esim.params["Tsuc"])
        print(f"---- mixer mome calc {esim.mixer.momCalcType}, N = {esim.mixer.Nint} , MFR2= {esim.mixerin['massFlowSecond']:.3f} g/m3")
        print(f"---- densities Dsuc_in {Dsuc:.3f} Dsy= {esim.mixerin['Dsy']:.3f}")
        print(f"---- pressure Psuc_in {params['Psuc']:.3f} Py= {esim.mixerin['py']:.3f}")
        print(f"---- area Aprim {esim.mixerin['Apy']:.3f} ASec= {esim.mixerin['Asy']:.3f}")
        resline = {"calctype" :2, "Nint": kk}
        resline.update(esim.mixerin)
        #resline = {"py": esim.mixerin['py'], "Dsy" : esim.mixerin['Dsy'], "MFRsuc": esim.mixerin['massFlowSecond'], "Asy": esim.mixerin['Asy'] }
        fullres = fullres.append(resline, ignore_index=True)
    except:
        print(sys.exc_info())


## test of the premix momentum integral:
[Dsi, hsi] = refProp.getDh_from_TP(esim.RP, params['Tsuc'], params['Psuc'])
params["Dsi"] = Dsi
params["hsi"] = hsi
params["hst"] = hsi
params["psi"] = params["Psuc"]
for N in range(1, 10):
    intgrl = esim.mixer.densinv_Int(147 - N/10, 7.67, 434.6702, N= N, pars = params)
    print(f"N= {N}, integral quad: {intgrl}")

##
# print(f"premix calculation type 1:")
# esim.mixer.momCalcType =1
# esim.mixerin = esim.mixer.premixWrapSolve(res_crit, esim.params["Psuc"], esim.params["Tsuc"])
# resline = {"calctype" :1, "Nint": 0}
# resline.update(esim.mixerin)
# fullres = fullres.append(resline, ignore_index=True)
# solve the mixer equations until the ejector outlet
#esim.mixersolve()

# esim.massFlowCheck()
# outletValues = esim.solMix.iloc[-1].to_dict() # .transpose()
#
# average_h = (outletValues["MFRp"] * outletValues["hp"] + outletValues["MFRs"] * outletValues["hs"])/ (outletValues["MFRp"] + outletValues["MFRs"] )
# print(f"Ejector outlet specific enthalpy {round(average_h,3)} kJ/kg, pressure {round(outletValues['p']*1e-2,3)} bar,"
#       f" vapor quality {round(outletValues['q_average'],3)}  ")
#
# esim.plotMixSolution(res_crit, esim.solMix, "simpy_ejector 1D Ejector flow solution")

