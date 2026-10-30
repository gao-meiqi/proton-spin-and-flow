# next R3pt2pt

for itf in flows:
    # =========================================================================================
    # ---------------------------------------
    # 2pt + current

    nt = 144

    # cfg_list = np.loadtxt('/public/home/gaomq/T00_new/H48P32/test/individual_flow_configs/configs_flow%d.txt'%itf)
    cfg_list = np.loadtxt("./individual_flow_configs/conf%d_pion.txt"%itf)
    
    nconf = len(cfg_list)
    print(nconf)
    # nconf = confcut

    n = []
    for cfg in cfg_list:
        a = np.load('/public/home/gaomq/T00/2ptdata/Pi_2pt/beta6.72_mu-0.1850_ms-0.1700_L48x144/Nev200/Pi_2pt_Px0Py0Pz0.conf%d.npz'%cfg)
        n.append(a["arr_0"])

    n = np.array(n).reshape(nconf, -1, nt, nt)  # conf, moms, sink, source
    print(n.shape)

    for it in range(nt):
        n[:, :, :, it] = np.roll(n[:, :, :, it], shift=-it, axis=2)

    n_ave = n.mean(axis=0)
    C2 = np.average(n, axis=3).real  # conf, moms, sink
    C2_ave = C2.mean(axis=0)
    C2_err = C2.std(axis=0)/np.sqrt(nconf-1)

    n_sub0 = n
    n_sub1 = n - n_ave
    n_sub2 = n - C2_ave.reshape(1, -1, nt, 1)

    p = 1
    n_jak = (np.sum(n, axis=0).reshape(1, p, nt, nt) - n)/(nconf-1)
    C2_jak = (np.sum(C2, axis=0).reshape(1, p, nt) - C2)/(nconf-1) 


    data1 = np.load("/public/home/gaomq/T00/H48P32/test/individual_flow_results/Pi_data1_flow%d.npy"%itf)
    data2 = np.load("/public/home/gaomq/T00/H48P32/test/individual_flow_results/Pi_data2_flow%d.npy"%itf)

    A = (data1 - data2).real

    A_ave1 = A.mean(axis=0)
    A_ave2 = A.mean(axis=(0,1))

    A_sub1 = A - A_ave1.reshape(1, -1)
    A_sub2 = A - A_ave2
    A_sub0 = A

    print(n.shape, n_sub1.shape, n_sub2.shape)
    print("A", A.shape, "A_sub1", A_sub1.shape, "A_sub2", A_sub2.shape)

    # -----------------------------------------
    t_st = 4
    t_ed = 16
    dt = np.arange(t_st, t_ed+1)

    n_list = [n_sub0, n_sub1, n_sub2]
    A_list = [A_sub0, A_sub1, A_sub2]

    C3 = [[[] for _ in range(3)] for _ in range(3)]

    for idt in dt: # sink 
        for itau in range(t_ed + 1): # current 保持固定长度，方便后面对齐
            
            is_physical = (itau <= idt)
            
            for t0 in range(nt):
                c_idx = (t0 + itau) % nt
                for i in range(3):
                    for j in range(3):
                        if is_physical:
                            val = n_list[i][:, :, idt, t0] * A_list[j][:, c_idx].reshape(-1, 1)
                        else:
                            val = np.zeros((nconf, p), dtype=n_list[0].dtype)

                        C3[i][j].append(val)

    # ===================== jack
    C3_reshaped = np.zeros((3, 3, dt.size, t_ed+1, nt, nconf, p), dtype=np.float64)
    C3_ave      = np.zeros((3, 3, dt.size, t_ed+1, nt, p))
    C3_err      = np.zeros_like(C3_ave)
    C3_jak      = np.zeros_like(C3_reshaped)

    for i in range(3):
        for j in range(3):
            C3_reshaped[i,j] = np.array(C3[i][j]).reshape(dt.size, t_ed+1, nt, nconf, p).real
            C3_ave[i,j] = np.average(C3_reshaped[i,j], axis=3)
            C3_err[i,j] = np.std(C3_reshaped[i,j], axis=3) / np.sqrt(nconf - 1)
            sum_ax3 = np.sum(C3_reshaped[i,j], axis=3).reshape(dt.size, t_ed+1, nt, 1, p)
            C3_jak[i,j] = (sum_ax3 - C3_reshaped[i,j]) / (nconf - 1)

    print(C3_reshaped[0,0].shape)

    # ===================== n_jak
    n_jak_pick = n_jak[:, :, dt, :]
    n_jak_pick = np.transpose(n_jak_pick, (2,3,0,1))
    denominator = n_jak_pick.reshape(dt.size, 1, nt, nconf, p)

    # ===================== R_jak 
    R_jak = np.zeros_like(C3_jak)
    for i in range(3):
        for j in range(3):
            R_jak[i,j] = C3_jak[i,j] / denominator

    # ==================== err
    R_jak_avets      = np.zeros((3, 3, dt.size, t_ed+1, nconf, p))
    R_jak_avets_ave  = np.zeros((3, 3, dt.size, t_ed+1, p))
    R_jak_avets_err  = np.zeros_like(R_jak_avets_ave)

    for i in range(3):
        for j in range(3):
            R_jak_avets[i,j]     = np.average(R_jak[i,j], axis=2).real
            R_jak_avets_ave[i,j] = np.average(R_jak_avets[i,j], axis=2)
            R_jak_avets_err[i,j] = np.std(R_jak_avets[i,j], axis=2) * np.sqrt(nconf-1)

            print(R_jak_avets_ave[i,j], R_jak_avets_err[i,j],i,j, itf)
    
    itf = itf/100
    itf_str = f"{itf:.3f}".replace('.', 'p')  

    R_jak_avets = R_jak_avets.reshape(3, 3, dt.size, t_ed+1, nconf )
    print(R_jak_avets.shape)

    np.save("/public/home/gaomq/T00/H48P32/test/Pi_R_3pt_2pt_H48P32_%s"%itf_str, R_jak_avets) 