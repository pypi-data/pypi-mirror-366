#!/usr/bin/env python
#---------------------------------------------------------------------------
# Copyright 2021 Takafumi Ogawa
# Licensed under the Apache License, Version2.0.
#---------------------------------------------------------------------------
# Auxiliary tool of pydecs library for converting the file from JANAF database
#---------------------------------------------------------------------------
import os
import sys
import argparse

kjmol2eV =1.036427e-2 # eV/(kJ/mol)

def convGasEneFromJANAF():
    parser = argparse.ArgumentParser(
        description="Converting JANAF-tabel to inpydecs_<gas>_delG.csv",
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Input file (text-type JANAF table)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output filename",
        type=str,
        default=None,
    )
    print("  Starting: pydecs-convGasEne-JANAF")
    args = parser.parse_args()
    filename_in = args.input_file
    print(f"  Input-file: {filename_in}")
    if not os.path.exists(filename_in):
        print("  Error: input-file not found: {filename_in}")
        sys.exit()

    temp_list = []
    ene_list = []
    fin1 = open(filename_in).readlines()
    t1 = fin1[0].split()[-1].strip()
    label1 = t1[:t1.find("(")]
    for t1 in fin1:
        if not "." in t1:
            continue
        t2=t1.split()
        temper=float(t2[0])
        ene=-temper*float(t2[2])/1000.0+float(t2[4])
        if temper<1e-6:
            ene0=ene 
            ene=0.0
        else:
            ene=ene-ene0
        temp_list.append(temper)
        ene2 = kjmol2eV*ene
        ene_list.append(ene2)

    if args.output:
        fnout1 =args.output
    else:
        fnout1 = f"inpydecs_{label1}_delG.csv"
    print(f"  Output-file: {fnout1}")
    fout1 = open(fnout1,"w")
    fout1.write("#"+fin1[0].strip()+"\n")
    fout1.write("#Temperature [K], Free_Energy [eV]\n")
    for t1,e1 in zip(temp_list,ene_list):
        fout1.write(f"{t1},{e1}\n")

def getGasEneFromJANAF():
    import re
    import shutil
    parser = argparse.ArgumentParser(
        description="Setup inpydecs_<gas>_delG.csv",
    )
    parser.add_argument(
        "gas_species",
        nargs="+",
        type=str,
        help="Gas species such as CO2, H2O, N2"
    )
    args = parser.parse_args()
    print("  Starting: pydecs-getGasEne-JANAF")

    sys.tracebacklimit = 0
    try:
        import janaf
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "\n  This tool requires janaf tool\n"
            "      -> pip install janaf\n"
        ) from e
    
    species_list = args.gas_species
    for sp1 in species_list:
        sp2 = re.escape(sp1)+"$"
        print(f"  Setting up for {sp2}")
        res1 = janaf.search(formula=sp2)
        print(f"    Found JANAF table: {res1}")
        
        fn1 = str(res1.fname)
        fn2 = fn1[fn1.rfind("/")+1:]
        print(f"  Copy from: {fn1}")
        print(f"       to: {fn2}")
        shutil.copy(fn1,fn2)
        sys.argv = ["pydecs-convGasEne-JANAF",fn2]
        convGasEneFromJANAF()
        print("  "+"-"*40)

if __name__=="__main__":
    convGasEneFromJANAF()

