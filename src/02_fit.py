# next EE
import numpy as np
import xarray as xr
import gvar as gv
import lsqfit
import os
from matplotlib import pyplot as plt
import lsqfit

def const_fcn(x, p):
    return {k: p['M'] + 0*x[k] for k in x}

dt = np.arange(4, 17) 

CXg_all_flows = []

for itf in flows:
    # print(itf)
    
    itf_str = f"{itf/100:.3f}".replace('.', 'p')
    file_path = f"/public/home/gaomq/T00/H48P32/test/Pi_R_3pt_2pt_H48P32_{itf_str}.npy"

    config_path = f"/public/home/gaomq/T00/H48P32/test/individual_flow_configs/conf{itf}_pion.txt"
    # print(config_path)

    if not os.path.exists(config_path):
        print(f"Skip Flow {itf}: Config file not found.")
        continue
    
    cfg_list = np.loadtxt(config_path)
    nconf = len(cfg_list)
    # print(nconf)
    
    try:
        raw_data = np.load(file_path)
        
    except FileNotFoundError:
        print(f"Skip Flow {itf}: Data file not found.")
        continue

    R_xr = xr.DataArray(
        raw_data[2, 2].real, 
        coords={'tsink_idx': np.arange(len(dt)), 
                'tau': np.arange(17), 
                'jackknife': np.arange(nconf)},
        dims=['tsink_idx', 'tau', 'jackknife']
    )

    R_ave = R_xr.mean('jackknife')
    R_2 = R_xr.rename({'tsink_idx': 'tsink_idx2', 'tau': 'tau2'})
    R_cov = xr.cov(R_xr, R_2, dim='jackknife', ddof=0) * (nconf - 1)

    plateau_data = {}
    x_dict = {}

    best_fit = None
    final_n_skip = 4
    
    for trial_skip in [4, 5, 6, 7, 8, 9]:
        temp_plateau_data = {}
        temp_x_dict = {}
        
        valid_idx = [i for i, t in enumerate(dt) if t > 2 * trial_skip]
        
        for idx in valid_idx:
            t_sep = dt[idx]
            t_range_arr = np.arange(trial_skip, t_sep - trial_skip + 1)
            
            if len(t_range_arr) > 0:
                val = R_ave.isel(tsink_idx=idx, tau=t_range_arr).values
                cov = R_cov.isel(tsink_idx=idx, tau=t_range_arr, 
                                 tsink_idx2=idx, tau2=t_range_arr).values
                tag = f't{t_sep}'
                temp_plateau_data[tag] = gv.gvar(val, cov)
                temp_x_dict[tag] = np.zeros(len(t_range_arr))

        total_pts = sum(len(v) for v in temp_plateau_data.values())
        if total_pts <= 1: 
            continue 

        fit = lsqfit.nonlinear_fit(data=(temp_x_dict, temp_plateau_data), fcn=const_fcn, p0={'M': 0.1})
        best_fit = fit
        final_n_skip = trial_skip
        
        if fit.chi2 / fit.dof < 1.2:
            break
            
    if best_fit is not None and best_fit.chi2 / best_fit.dof < 5.0:

        CXg_all_flows.append(best_fit.p['M'])
        # print(itf, final_n_skip, best_fit.p['M'], best_fit.chi2/best_fit.dof)
        print(f"Flow {itf} | n_skip: {final_n_skip} | M: {best_fit.p['M']} | chi2/dof: {best_fit.chi2/best_fit.dof:.2f}",nconf)

        # # -------------------------------------------------------------

        plt.figure()
        for idx, t in enumerate(dt[:13]):
            tau_arr = np.arange(17)
            val = R_ave.isel(tsink_idx=idx).values
            cov = R_cov.isel(tsink_idx=idx, tau=tau_arr, tsink_idx2=idx, tau2=tau_arr).values
            err = np.sqrt(np.diag(cov)) 
            
            x = tau_arr - t/2
            mask = val != 0
            x, val, err = x[mask], val[mask], err[mask]
            plt.errorbar(x, val, yerr=err, capsize=3, ls='none',label=r'$t_{\rm sink}=%d$'%t)

        M = best_fit.p['M'].mean
        Me = best_fit.p['M'].sdev
        x_min, x_max = plt.gca().get_xlim()
        plt.fill_between([x_min, x_max], M-Me, M+Me, color='r', alpha=0.2)
        plt.legend(bbox_to_anchor=(1, 1))
        plt.xlabel(r'$\tau$')
        plt.ylabel('$3pt/2pt$')
        # plt.close()
        
        # # ----------------------------------------------------------------

    else:
        print(f"Flow {itf:3d} | Fit failed: \chi2 {best_fit.chi2/best_fit.dof:.2f})")
        CXg_all_flows.append(np.nan)

CXg_final = np.array(CXg_all_flows)
# np.save("/public/home/gaomq/T00/H48P32/test/EE_H48P32.npy", CXg_final/2)