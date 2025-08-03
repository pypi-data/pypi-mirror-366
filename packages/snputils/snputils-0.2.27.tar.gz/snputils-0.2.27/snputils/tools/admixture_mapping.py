import argparse
import logging
from typing import List
import numpy as np
from scipy import stats
import pandas as pd

from snputils.phenotype.io.read import UKBPhenReader
from snputils.ancestry.io.local.read import MSPReader

log = logging.getLogger(__name__)


def parse_admixmap_args(argv):
    parser = argparse.ArgumentParser(prog='admixture_mapping', description='Admixture Mapping.')

    parser.add_argument('--plot', required=False, default=False, type=bool, help='Plot Admixture Mapping Results {True, *False*}')
    requiredARGV = parser.add_argument_group('required arguments')
    requiredARGV.add_argument('--pheID', required=True, type=str, help='Phenotype ID.')
    requiredARGV.add_argument('--phe_path', required=True, type=str, help='Path of the .phe file (include file).') 
    requiredARGV.add_argument('--msp_path', required=True, type=str, help='Path of the .msp file (include file).') 
    requiredARGV.add_argument('--results_path', required=True, type=str, help='Path used to save resulting data in compressed .tsv file.')
    
    return parser.parse_args(argv)


def admixmap(argv: List):
    args = parse_admixmap_args(argv)
    
    gbe_id = args.pheID

    phe_path = (args.phe_path)
    phe_reader = UKBPhenReader(phe_path)
    pheObj = phe_reader.read()

    cases_IDs = pheObj.cases_IDs
    controls_IDs = pheObj.controls_IDs

    cases_haplotypes = pheObj.cases_haplotypes
    controls_haplotypes = pheObj.controls_haplotypes

    msp_reader = MSPReader(args.msp_path)
    mspObj = msp_reader.read()

    hla_windows = []
    # Remove HLA (in chr 6, between positions x and y for spos and epos)
    if 6 in mspObj.chromosomes:
        print("Removing HLA windows...")
        for indx in np.where(mspObj.chromosomes==6)[0]:
            if ( (25477797 <= mspObj.physical_pos[indx][0] <= 36448354)
                or (25477797 <= mspObj.physical_pos[indx][1] <= 36448354) ):
                print("From chm", mspObj.chromosomes[indx], "Window", indx, "has been removed.")
                hla_windows.append(indx)
        mspObj.filter_windows(indexes=hla_windows, include=False, inplace=True)
    else:
        print("No HLA windows to remove.")
        
    print("Creating case and control mspObjects...")
    cases_indx = []
    controls_indx = []
    # The loop is optimized so that it is only necessary to visit half of the elements
    # This optimization however is susceptible to the current Phenotype Reader: [haplotype.0] + [haplotype.1]
    for ind in range(len(mspObj.haplotypes))[::2]:
        if mspObj.haplotypes[ind] in pheObj.cases_haplotypes:
            cases_indx.append(ind)
            cases_indx.append(ind+1)
        else:
            controls_indx.append(ind)
            controls_indx.append(ind+1)
        
    cases_mspObj = mspObj.copy
    controls_mspObj = mspObj.copy
    cases_mspObj.filter_samples(indexes=controls_indx, include=False)
    controls_mspObj.filter_samples(indexes=cases_indx, include=False)

    # Sanity Check
    if (len(cases_mspObj.lai) == 0):
        raise ValueError("No case data available!")
    if (len(controls_mspObj.lai) == 0):
        raise ValueError("No control data available!")
    del mspObj

    print("Calculating baseline average ancestry frequencies in cases and controls...")
    ancFrac = []
    # It can be assume that the same ancestries are present in cases and controls (hence it could also be controls_mspObj.n_ancestries)
    for ancestry in range(cases_mspObj.n_ancestries):
        ancFrac.append(
            float((cases_mspObj.lai == ancestry).sum()) / (cases_mspObj.lai.size) - float((controls_mspObj.lai == ancestry).sum()) / (controls_mspObj.lai.size)
        )

    data = []
    print("Calculating test statistics across windows...")
    for window in range(len(cases_mspObj.chromosomes)):
        # This could also be retrieved from controls_mspObj
        chm, spos, epos = (
            cases_mspObj.chromosomes[window],
            cases_mspObj.physical_pos[window][0],
            cases_mspObj.physical_pos[window][1],
        )

        case_ancestriesxwindow = cases_mspObj.lai[window]
        control_ancestriesxwindow = controls_mspObj.lai[window]
        for ancestry_string, ancestry in cases_mspObj.ancestry_map.items():
            case_p = float((case_ancestriesxwindow == ancestry).sum()) / len(case_ancestriesxwindow)
            control_p = float((control_ancestriesxwindow == ancestry).sum()) / len(control_ancestriesxwindow)
            A = case_p - control_p
            B = ancFrac[ancestry]
            C = case_p * (1 - case_p) / len(case_ancestriesxwindow)
            D = control_p * (1 - control_p) / len(control_ancestriesxwindow)
            z = (A - B) / np.sqrt(C + D)
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
            data.append([chm, spos, epos, ancestry_string, A, B, C, D, z, p_value])

    admixmap_results_path = args.results_path
    print("Writing dataframe to file found in", admixmap_results_path)
    results = pd.DataFrame(
        data, columns=["#chm", "spos", "epos", "ancestry", "A", "B", "C", "D", "z", "p_value"]
    )
    results.to_csv(admixmap_results_path + gbe_id + "_admixmap.tsv.gz", sep="\t", index=False)
