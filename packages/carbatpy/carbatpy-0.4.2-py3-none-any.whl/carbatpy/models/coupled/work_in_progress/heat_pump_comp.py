# -*- coding: utf-8 -*-
"""
Heat pump with two two-tank storage, with the new component (comp.py) formulation.

Created on Thu Aug 15 12:45:29 2024

@author: atakan
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, differential_evolution, basinhopping
import carbatpy as cb

# ------- input data -----------


def heat_pump(dir_name, power=1000., **kwargs):
    new_config = kwargs.get("config", None)  # for optimizations
    verbose = kwargs.get("verbose", False)
    warnings = {}
    outputs = {}

    def add_w_o(what):
        warnings[what.name] = what.warning
        outputs[what.name] = what.output
    # ================ CALCULATIONS ==============================
    # ------ Start/initial condition ----
    # but the mass flow rate is yet unknown, plotting must be delayed
    start = cb.comp.Start("start", dir_name, m_dot=10e-3)
    config = start.config
    if new_config is not None and "working_fluid" in new_config:
        config["working_fluid"].update(new_config["working_fluid"])

    start = cb.comp.Start("start", config, m_dot=10e-3)
    # ----- compressor --------------
    # prescribed power, working_fluid mass flow rate is calculated here
    run_p_comp = {"power": power}

    compressor = cb.comp.FlowMachine("compressor", config)
    p_high = compressor.config['working_fluid']['p_high']
    compressor.calculate(start.output["state_out"],
                         {'working_fluid': [600, p_high, 5e5]},
                         run_param=run_p_comp)  # ,  m_dot=10e-3)
    # for the output only p_high is used! Now m_dot is known for the working fluid.
    m_dot_w = compressor.output["m_dot"]
    start = cb.comp.Start("start", config, m_dot=m_dot_w)
    add_w_o(start)
    add_w_o(compressor)

    # ----- coondenser --------------
    run_p_cond = {"m_dot": {"working_fluid": m_dot_w}}

    condenser = cb.comp.StaticHeatExchanger("condenser", config)
    inp1, outp1 = condenser.set_in_out(
        {'working_fluid': compressor.output['state_out']["working_fluid"]})

    condenser.calculate(in_states=inp1, run_param=run_p_cond, verbose=False)
    # condenser.hex_opti_work_out(run_p_par=run_p_cond)

    # condenser.output["state_out"]["working_fluid"]
    throttle = cb.comp.Throttle("throttle", config)
    throttle.calculate(condenser.output["state_out"]["working_fluid"],
                       compressor.output["state_in"],
                       m_dot=m_dot_w)
    add_w_o(throttle)
    add_w_o(condenser)

    evaporator = cb.comp.StaticHeatExchanger("evaporator", config)
    inp1, outp1 = evaporator.set_in_out(
        {'working_fluid': throttle.output['state_out']["working_fluid"]})
    inp2, outp2 = evaporator.set_in_out(
        start.output['state_in'], False)
    evaporator.calculate(inp1, outp2, run_param=run_p_cond, verbose=False)
    add_w_o(evaporator)

    cop = np.abs(condenser.output["q_dot"]/run_p_comp["power"])
    outputs["config"] = config
    if verbose:
        print(f"COP: {cop :.4f}")

    # =========== Calculations finished ====================
    # --------- plot preparation ------------

    fig, ax = plt.subplots(1)
    plot_info = cb.CB_DEFAULTS["Components"]["Plot"]
    plot_info.update({"ax": ax, "fig": fig, "x-shift": [0, 0]})

    pl_inf = plot_info.copy()  # for the starting point (dot)
    pl_inf.update({"label": ["start", ""],
                   "col": ["ok", "bv"],
                   "direction": 1, })
    #
    #     Plotting starts
    shift, direct = start.plot(pl_inf)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [compressor.name, ""],
                      "col": ["-r", "bv-"]})
    shift, direct = compressor.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [condenser.name, ""],
                      "col": [":r", "rv-"]})
    shift, direct = condenser.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [throttle.name, ""],
                      "col": ["-b", "bv-"]})
    shift, direct = throttle.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [evaporator.name, ""],
                      "col": [":b", "bv-"]})
    evaporator.plot(plot_info)
    return cop, outputs, warnings, fig, ax


def optimize_wf_heat_pump(dir_name, config_0, bounds_0, **kwargs):
    """
    Heat pump COP optimization, varying p_high and mixture composition

    p_low cannot be selected directly, it is determined by the storage
    temperature and the superheating temperature difference and the minimum
    approach temperature. In optimization, the low pressure (wanted) from
    the conciguration yaml file is checked. If the calculated low pressure is
    below that value, the COP is weighted with the ratio.

    Parameters
    ----------
    dir_name : str or dict
        either the path to the yaml file with all configuration parameters, or
        a dictionary with all values.
    config_0 : dict
        vales set here and deviating from dir_name.
    bounds_0 : dictTYPE
        dictionary with the p_high bounds and the upper bounds of the first
        three molefractions. The remaining value is the difference to 1. It is
        checked that the sum is 1 and all vales are positive.
    **kwargs :
        - 'optimize_global': select optimization algorith "dif_evol", "bas_hop",
        or local minimizer (Nelson Mead).

    Returns
    -------
    result : OptimizeResult
        The result of the optimization.

    """


    x0, bnds, cons = extract_optim_data(config_0, bounds_0)
    opt_global = kwargs.get('optimize_global', "dif_evol")
    tolerance = 1e-4
    max_iter = 320

    if opt_global == "dif_evol":
        result = differential_evolution(_opti_hp_func,
                                        bnds,
                                        args=(config_0, dir_name),
                                        workers=3,
                                        maxiter=max_iter,
                                        )
    elif opt_global == "bas_hop":
        result = basinhopping(_opti_hp_func,
                              x0,
                              minimizer_kwargs={'method': 'Nelder-Mead',
                                                'bounds': bnds,
                                                'args': (config_0, dir_name)},
                              )
    else:
        # Local optimization
        result = minimize(_opti_hp_func,
                          x0,
                          args=(config_0, dir_name),
                          method='Nelder-Mead',
                          # tol=tolerance,
                          bounds=bnds,
                          # constraints=cons,
                          options={
                              # 'finite_diff_rel_step': .05,
                              "maxiter": max_iter,  # can take long!
                              "disp": True})
    return result


def _opti_hp_func(x,  conf, dir_name, verbose=False, **kwargs):
    """
    Function for heat pump optimization, p_high and 4-component mixture

    Parameters
    ----------
    x : array/list, length 4
        p_high and the first three mole fractions.
    conf :  dict
        vales set here and deviating from dir_name.
    dir_name : str or dict
        either the path to the yaml file with all configuration parameters, or
        a dictionary with all values.
    verbose : TYPE, optional
        DESCRIPTION. The default is False.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    conf_act = {"working_fluid": {"p_high": x[0],
                                  'fractions': [x[1], x[2], x[3], 1-np.sum(x[1:])]}}
    if 1-np.sum(x[1:]) < 0 or any(x < 0):
        return 500

    try:
        cop, ou, wa, fi, ax = heat_pump(dir_name, config=conf_act)

        p_low_actual = ou["start"]["p_low"]
        p_low_min = ou['config']['working_fluid']["p_low"]
        p_l_ratio = p_low_actual / p_low_min
        factor = 1
        if p_l_ratio <= 1:  # punish too low pressures
            factor = p_l_ratio
        print(cop, wa, x, 1-np.sum(x[1:]), factor)

    except:
        return 509
    if any(ns.value >= 10 for ns in wa.values()):
        return 100 * cop
    return -cop * factor


def extract_optim_data(conf, bounds):
    wf_conf = conf["working_fluid"]
    wf_bounds = bounds["working_fluid"]

    x0 = [
        wf_conf["p_high"],
        *wf_conf["fractions"][:3]
    ]

    bnds = [
        tuple(wf_bounds["p_high"]),
        (0.0, wf_bounds["fractions"][0]),
        (0.0, wf_bounds["fractions"][1]),
        (0.0, wf_bounds["fractions"][2]),
    ]

    f4max = wf_bounds["fractions"][2]
    # 1. fraction_4 \>= 0: x[2] + x[3] + x[4] \<= 1
    # 2. fraction_4 <= f4max: x[2] + x[3] + x[4] \>= 1 - f4max

    cons = [
        {'type': 'ineq', 'fun': lambda x:  1 -
            (x[2] + x[3] + x[1])},        # \<=1
        {'type': 'ineq', 'fun': lambda x:  (
            x[2] + x[3] + x[1]) - (1 - f4max)},  # \>=1-f4max
    ]
    return x0, bnds, cons


if __name__ == "__main__":
    OPTI = False

    dir_name_out = cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-cycle-data.yaml"
    dir_name_out = r"C:\Users\atakan\sciebo\results\io-cycle-data-prop-pent.yaml"

    conf_m = {"working_fluid": {"p_high": 1.29e6,
                              'fractions': [.55, 0.35, .05, 0.050]}}
    conf_m = {"working_fluid": {"p_high": 1511375.0335341833,
                               'fractions': [0.75,
                                             0.25,
                                             0.0,
                                             0.0]}}
    # conf = dir_name

    cop_m, ou_m, wa_m, fi_m, ax_m = heat_pump(dir_name_out, config=conf_m, verbose=True)

    if any(ns.value != 0 for ns in wa_m.values()):
        print(f"Check Warnings, at least one deviates from 0!\n {wa_m}")
    if OPTI:
        # for optimization:
        bounds_m = {"working_fluid":
                  {"p_high": [5e5, 01.8e6],
                   'fractions': [.95, 0.5, .005, 0.5]}}  # for fractions only maximal values
        print(extract_optim_data(conf_m, bounds_m))
        opt_res = optimize_wf_heat_pump(dir_name_out, conf_m, bounds_m,
                                        optimize_global="dif_evol")
        print(opt_res, 1-np.sum(opt_res.x[1:]))

        import pandas as pd

        # Angenommen:
        # optResult.population.shape = (75, 5)
        # optResult.population_energies.shape = (75,)

        colnames = ["p_h", "propane", "butane", "pentane"]
        # Prüfe vorsichtshalber auf die richtige Länge:
        assert len(colnames) == opt_res.population.shape[1]

        df = pd.DataFrame(opt_res.population, columns=colnames)
        df["cop-weighted"] = opt_res.population_energies

        p_l = []
        c6 = []
        p_ratio = []
        cops = []
        for o_val in opt_res.population:
            conf_o = {"working_fluid": {"p_high": o_val[0],  'fractions':  [
                *o_val[1:], 1 - np.sum(o_val[1:])]}}
            cop_o, ou_o, wa_o, fi_o, ax_o = heat_pump(
                dir_name_out, config=conf_o, verbose=True)
            p_l.append(ou_o['start']['p_low'])
            c6.append(1-np.sum(o_val[1:]))
            p_ratio.append(o_val[0] / ou_o['start']['p_low'])
            cops.append(cop_o)
        df["CO2"] = c6
        df["p_low"] = p_l
        df["p_ratio"] = p_ratio
        df['cop'] = cops
        df.to_csv(
            r"C:\Users\atakan\sciebo\results\optResult_368K_255K_CO2.csv",
            index=False)
