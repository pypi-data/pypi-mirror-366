import os

import numpy as np
import pandas as pd


def get_samples_from_msp_df(msp_df):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py
    Function for getting sample IDs from a pandas DF containing the output data
    :param msp_df:
    :return:
    """
    # get all columns including sample names
    query_samples_dub = msp_df.columns[6:]

    # only keep 1 of maternal/paternal
    single_ind_idx = np.arange(0 ,len(query_samples_dub) ,2)
    query_samples_sing = query_samples_dub[single_ind_idx]

    # remove the suffix
    query_samples = [qs[:-2] for qs in query_samples_sing]

    return query_samples


def write_msp(msp_prefix, meta_data, pred_labels, populations, query_samples):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py

    Args:
        msp_prefix
        meta_data
        pred_labels
        populations
        query_samples

    Returns:
        None
    """
    msp_data = np.concatenate([np.array(meta_data), pred_labels.T], axis=1).astype(str)

    with open(msp_prefix +".msp", 'w') as f:
        # first line (comment)
        f.write("#Subpopulation order/codes: ")
        f.write("\t".join([str(pop ) +"= " +str(i) for i, pop in enumerate(populations)] ) +"\n")
        # second line (comment/header)
        f.write("# " +"\t".join(meta_data.columns) + "\t")
        f.write("\t".join([str(s) for s in np.concatenate([[ s +".0" , s +".1"] for s in query_samples])] ) +"\n")
        # rest of the lines (data)
        for l in range(msp_data.shape[0]):
            f.write("\t".join(msp_data[l ,:]))
            f.write("\n")


def write_fb(fb_prefix, meta_data, proba, ancestry, query_samples):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py

    Args:
        fb_prefix
        meta_data
        proba
        ancestry
        query_samples
    
    Returns:
        None
    """
    n_rows = meta_data.shape[0]

    pp = np.round(np.mean(np.array(meta_data[["spos", "epos"]] ,dtype=int) ,axis=1)).astype(int)
    gp = np.mean(np.array(meta_data[["sgpos", "egpos"]] ,dtype=float) ,axis=1).astype(float)

    fb_meta_data = pd.DataFrame()
    fb_meta_data["chromosome"] = meta_data["chm"]
    fb_meta_data["physical position"] = pp
    fb_meta_data["genetic_position"]  = gp
    fb_meta_data["genetic_marker_index"] = np.repeat(".", n_rows)

    fb_prob_header = [":::".join([q ,h ,a]) for q in query_samples for h in ["hap1", "hap2"] for a in ancestry]
    fb_prob = np.swapaxes(proba ,1 ,2).reshape(-1, n_rows).T
    fb_prob_df = pd.DataFrame(fb_prob)
    fb_prob_df.columns = fb_prob_header

    fb_df = pd.concat((fb_meta_data.reset_index(drop=True), fb_prob_df) ,axis=1)

    with open(fb_prefix +".fb", 'w') as f:
        # header
        f.write("#reference_panel_population:\t")
        f.write("\t".join(ancestry ) +"\n")
        fb_df.to_csv(f, sep="\t", index=False)

    return


def msp_to_lai(msp_file, positions, lai_file=None):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py

    Args:
        msp_file
        positions
        lai_file

    Returns:
        df
    """
    msp_df = pd.read_csv(msp_file, sep="\t", comment="#", header=None)
    data_window = np.array(msp_df.iloc[:, 6:])
    n_reps = msp_df.iloc[:, 5].to_numpy()
    assert np.sum(n_reps) == len(positions)
    data_snp = np.concatenate([np.repeat([row], repeats=n_reps[i], axis=0) for i, row in enumerate(data_window)])

    pos_lower_bound = int(msp_df.iloc[0, 1])
    pos_upper_bound = int(msp_df.iloc[-1, 2])

    extrapolating_lo = np.sum(positions < pos_lower_bound)
    extrapolating_hi = np.sum(positions > pos_upper_bound)
    if extrapolating_lo > 0:
        print("WARNING: Extrapolating ancestry inference for {} SNPs (lower bound is position {})".format
              (extrapolating_lo, pos_lower_bound))

    if extrapolating_hi > 0:
        print( "WARNING: Extrapolating ancestry inference for {} SNPs (upper bound is position {})".format
            (extrapolating_hi, pos_upper_bound) )

    with open(msp_file) as f:
        first_line = f.readline()
        second_line = f.readline()

    header = second_line[:-1].split("\t")
    samples = header[6:]
    df = pd.DataFrame(data_snp, columns=samples, index=positions)

    if lai_file is not None:
        with open(lai_file, "w") as f:
            f.write(first_line)
        df.to_csv(lai_file, sep="\t", mode='a', index_label="position")

    return df


def get_bed_data(msp_df, sample, pop_order=None):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py

    Args:
        msp_df
        sample
        pop_order

    Returns:
        bed_data
    """
    ancestry_label = lambda pop_numeric: pop_numeric if pop_order is None else pop_order[pop_numeric]

    chm, spos, sgpos = [ [val] for val in msp_df[["#chm", "spos", "sgpos"]].iloc[0] ]
    epos, egpos = [], []
    anc = msp_df[sample].iloc[0]
    ancestry_labels = [ ancestry_label(anc) ]

    for i, row_anc in enumerate(msp_df[sample].iloc[1:]):
        row = i+ 1
        if row_anc != anc:
            anc = row_anc
            epos.append(msp_df["epos"].iloc[row - 1])
            egpos.append(msp_df["egpos"].iloc[row - 1])
            chm.append(msp_df["#chm"].iloc[row])
            ancestry_labels.append(ancestry_label(row_anc))
            spos.append(msp_df["spos"].iloc[row])
            sgpos.append(msp_df["sgpos"].iloc[row])

    epos.append(msp_df["epos"].iloc[-1])
    egpos.append(msp_df["egpos"].iloc[-1])

    bed_data = {
        "chm": np.array(chm).astype(int),
        "spos": np.array(spos).astype(int),
        "epos": np.array(epos).astype(int),
        "ancestry": ancestry_labels,
        "sgpos": sgpos,
        "egpos": egpos
    }
    return bed_data


def msp_to_bed(msp_file, root, pop_order=None):
    """
    From: https://github.com/AI-sandbox/gnomix/blob/main/src/postprocess.py

    Args:
        msp_file
        root
        pop_order

    Returns:
        None
    """
    with open(msp_file) as f:
        _ = f.readline()
        second_line = f.readline()

    header = second_line.split("\t")
    msp_df = pd.read_csv(msp_file, sep="\t", comment="#", names=header)

    samples = header[6:]

    for sample in samples:
        sample_file_name = os.path.join(root, sample.replace(".", "_") + ".bed")
        sample_bed_data = get_bed_data(msp_df, sample, pop_order=pop_order)
        sample_bed_df = pd.DataFrame(sample_bed_data)
        sample_bed_df.to_csv(sample_file_name, sep="\t", index=False)
