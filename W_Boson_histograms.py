import os
import math
import ROOT

# Directory containing ROOT files
root_files_directory = "/home/ctv19/root_macros/SuepDistribution1/"

triggers_of_interest = [
    "HLT_Mu50",
    "HLT_IsoMu24",
    "HLT_Ele35_WPTight_Gsf",
]

# Noise filters
noise_filters = [
    "Flag_goodVertices",
    "Flag_globalSuperTightHalo2016Filter",
    "Flag_HBHENoiseFilter",
    "Flag_HBHENoiseIsoFilter",
    "Flag_EcalDeadCellTriggerPrimitiveFilter",
    "Flag_BadPFMuonFilter",
    "Flag_BadPFMuonDzFilter",
    "Flag_eeBadScFilter",
]

lepton_data = {
    "Muon": {"pt": [], "eta": [], "phi": [], "charge": []},
    "Electron": {"pt": [], "eta": [], "phi": [], "charge": []},
}
met_pt_values = []
met_phi_values = []
w_mass_values = []
w_pt_values = []
w_phi_values = []

def passes_trigger(tree):
    return any(hasattr(tree, trig) and getattr(tree, trig) for trig in triggers_of_interest)

def passes_met_filters(tree):
    for filt in noise_filters:
        if hasattr(tree, filt) and not getattr(tree, filt):
            return False
    return True

def calculate_w_kinematics(lep_pt, lep_phi, met_pt, met_phi):
    delta_phi = lep_phi - met_phi
    mt = math.sqrt(2 * lep_pt * met_pt * (1 - math.cos(delta_phi)))
    px_lep = lep_pt * math.cos(lep_phi)
    py_lep = lep_pt * math.sin(lep_phi)
    px_met = met_pt * math.cos(met_phi)
    py_met = met_pt * math.sin(met_phi)

    px_w = px_lep + px_met
    py_w = py_lep + py_met

    pt_w = math.sqrt(px_w**2 + py_w**2)
    phi_w = math.atan2(py_w, px_w)

    return mt, pt_w, phi_w

def draw_latex_label(x, y, text):
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.DrawLatex(x, y, text)

def plot_histogram(data, title, x_label_tex, filename, bins=50, x_range=None):
    if not data:
        return
    hist = ROOT.TH1F(title, title, bins, *(x_range if x_range else (min(data), max(data))))
    for val in data:
        hist.Fill(val)

    c = ROOT.TCanvas()
    hist.Draw()

    hist.GetXaxis().SetTitle("")
    hist.GetYaxis().SetTitle("")

    draw_latex_label(0.5, 0.02, x_label_tex)
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.04)
    latex.SetTextAngle(90)
    latex.DrawLatex(0.06, 0.5, "Counts")

    c.Print(os.path.join(root_files_directory, filename))

for filename in os.listdir(root_files_directory):
    if not filename.endswith(".root"):
        continue

    file_path = os.path.join(root_files_directory, filename)
    root_file = ROOT.TFile.Open(file_path)
    if not root_file or root_file.IsZombie():
        print(f"Skipping corrupted file: {filename}")
        continue

    tree = root_file.Get("Events")
    if not tree:
        print(f"No 'Events' tree found in {filename}")
        continue

    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        
        if not (passes_trigger(tree) and passes_met_filters(tree)):
            continue

        if hasattr(tree, "PuppiMET_pt") and hasattr(tree, "PuppiMET_phi"):
            met_pt = tree.PuppiMET_pt
            met_phi = tree.PuppiMET_phi
        else:
            continue

        if met_pt < 40: 
            continue

        met_pt_values.append(met_pt)
        met_phi_values.append(met_phi)

        found_lepton = False

        # -------- MUON SELECTION (tightened) --------
        if hasattr(tree, "Muon_pt"):
            for j in range(len(tree.Muon_pt)):
                pt = tree.Muon_pt[j]
                eta = tree.Muon_eta[j]
                phi = tree.Muon_phi[j]
                dxy = abs(tree.Muon_dxy[j])
                dz = abs(tree.Muon_dz[j])
                tightId = tree.Muon_tightId[j]
                iso = tree.Muon_pfRelIso04_all[j]
                charge = tree.Muon_charge[j] if hasattr(tree, "Muon_charge") else 0

                # Paper requirements:
                # pT > 30, |η| < 2.4, tight ID, Irel_PF < 0.1, |dxy| < 0.02 cm, |dz| < 0.05 cm
                if (pt > 30 and abs(eta) < 2.4 and tightId and 
                    iso < 0.1 and dxy < 0.02 and dz < 0.05):
                    
                    mt, pt_w, phi_w = calculate_w_kinematics(pt, phi, met_pt, met_phi)
                    
                    if mt < 40 or mt > 120:
                        continue

                    lepton_data["Muon"]["pt"].append(pt)
                    lepton_data["Muon"]["eta"].append(eta)
                    lepton_data["Muon"]["phi"].append(phi)
                    lepton_data["Muon"]["charge"].append(charge)

                    w_mass_values.append(mt)
                    w_pt_values.append(pt_w)
                    w_phi_values.append(phi_w)
                    found_lepton = True
                    break  

        if found_lepton:
            continue

        # -------- ELECTRON SELECTION (tightened) --------
        if hasattr(tree, "Electron_pt"):
            for j in range(len(tree.Electron_pt)):
                pt = tree.Electron_pt[j]
                eta = tree.Electron_eta[j]
                phi = tree.Electron_phi[j]
                dxy = abs(tree.Electron_dxy[j])
                dz = abs(tree.Electron_dz[j])
                wp80 = tree.Electron_mvaFall17V2Iso_WP80[j]
                charge = tree.Electron_charge[j] if hasattr(tree, "Electron_charge") else 0

                abs_eta = abs(eta)
                in_barrel = abs_eta < 1.444
                in_endcap = 1.566 < abs_eta < 2.5

                if not (in_barrel or in_endcap):
                    continue
                
                # Paper requirements:
                # pT > 35 GeV, |η| < 2.5 (excluding 1.444-1.566)
                # WP80 MVA ID with isolation
                # Barrel: |dxy| < 0.05 cm, |dz| < 0.1 cm
                # Endcap: |dxy| < 0.1 cm, |dz| < 0.2 cm
                if (pt > 35 and wp80 and
                    ((in_barrel and dxy < 0.05 and dz < 0.1) or 
                     (in_endcap and dxy < 0.1 and dz < 0.2))):
                    
                    mt, pt_w, phi_w = calculate_w_kinematics(pt, phi, met_pt, met_phi)
                    
                    # Skip events outside W mass window
                    if mt < 40 or mt > 120:
                        continue

                    lepton_data["Electron"]["pt"].append(pt)
                    lepton_data["Electron"]["eta"].append(eta)
                    lepton_data["Electron"]["phi"].append(phi)
                    lepton_data["Electron"]["charge"].append(charge)

                    w_mass_values.append(mt)
                    w_pt_values.append(pt_w)
                    w_phi_values.append(phi_w)
                    break  

# Plotting
plot_histogram(lepton_data["Muon"]["pt"], "Muon pT", "#mu p_{T} [GeV]", "combined_muon_pt.png", x_range=(0, 500))
plot_histogram(lepton_data["Muon"]["eta"], "Muon eta", "#mu #eta", "combined_muon_eta.png", x_range=(-3, 3))
plot_histogram(lepton_data["Muon"]["phi"], "Muon phi", "#mu #phi [rad]", "combined_muon_phi.png", x_range=(-3.2, 3.2))

plot_histogram(lepton_data["Electron"]["pt"], "Electron pT", "e p_{T} [GeV]", "combined_electron_pt.png", x_range=(0, 500))
plot_histogram(lepton_data["Electron"]["eta"], "Electron eta", "e #eta", "combined_electron_eta.png", x_range=(-3, 3))
plot_histogram(lepton_data["Electron"]["phi"], "Electron phi", "e #phi [rad]", "combined_electron_phi.png", x_range=(-3.2, 3.2))

# MET plots
plot_histogram(met_pt_values, "MET pT", "MET p_{T} [GeV]", "combined_met_pt.png", x_range=(0, 500))
plot_histogram(met_phi_values, "MET phi", "MET #phi [rad]", "combined_met_phi.png", x_range=(-3.2, 3.2))

# W boson kinematics (focus on W mass region)
plot_histogram(
    w_mass_values, 
    "W Boson Transverse Mass", 
    "W m_{T} [GeV]", 
    "w_transverse_mass.png", 
    bins=50, 
    x_range=(40, 120) 
)
plot_histogram(w_pt_values, "W Boson pT", "W p_{T} [GeV]", "w_pt.png", x_range=(0, 500))
plot_histogram(w_phi_values, "W Boson phi", "W #phi [rad]", "w_phi.png", x_range=(-3.2, 3.2))

print(f"W Transverse Mass Stats: Mean = {sum(w_mass_values)/len(w_mass_values):.1f} GeV, StdDev = {math.sqrt(sum((x - sum(w_mass_values)/len(w_mass_values))**2 for x in w_mass_values)/len(w_mass_values)):.1f} GeV")
print("All plots generated successfully!")