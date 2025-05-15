CMS Distribution Analysis
This repository contains Python scripts for analyzing and plotting kinematic distributions of particles from CMS NanoAOD ROOT files, with a focus on WH SUEP signal events.

Contents
Lepton Histograms: Generates transverse momentum (pT), pseudorapidity (η), and azimuthal angle (φ) plots for muons, electrons, and taus.

Jet Histograms: Produces kinematic distributions for reconstructed jets.

Photon Histograms: Analyzes basic kinematic properties of photons.

Missing Transverse Energy (MET): Computes MET distributions and reconstructs the W boson transverse mass using MET and muon data.

Usage
Each script is designed to:

Read multiple NanoAOD ROOT files

Extract relevant branches using ROOT and PyROOT

Apply optional filters (e.g., pT thresholds)

Produce combined plots for each particle type

Example
To run a plotting script:

python3 lepton_histograms.py
Make sure to update the file paths inside the script to match your local ROOT file directory.

Goals
This analysis helps explore and visualize features of SUEP signals and background processes, aiming to improve selection criteria and better understand particle kinematics.

Dependencies
Python 3.x
ROOT (PyROOT)
NumPy

Author
Connor Van Cleef – based on analysis guidance from Joey Reichert (Rutgers University)
