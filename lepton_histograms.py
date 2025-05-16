import os
import ROOT

root_files_directory = "" #file path

pt_threshold = 5
pt_upper_cap = 500

triggers_of_interest = [
    "HLT_Mu50",
    "HLT_IsoMu24",
    "HLT_Ele35_WPTight_Gsf",
]

lepton_data = {
    "Muon": {"pt": [], "eta": [], "phi": []},
    "Electron": {"pt": [], "eta": [], "phi": []},
}

def passes_trigger(tree):
    for trig in triggers_of_interest:
        if hasattr(tree, trig) and getattr(tree, trig):
            return True
    return False

for filename in os.listdir(root_files_directory):
    if not filename.endswith(".root"):
        continue

    file_path = os.path.join(root_files_directory, filename)
    root_file = ROOT.TFile.Open(file_path)

    if not root_file or root_file.IsZombie():
        print(f"Skipping corrupted or unreadable file: {filename}")
        continue

    tree = root_file.Get("Events")
    if not tree:
        print(f"No 'Events' tree found in {filename}")
        continue

    n_entries = tree.GetEntries()
    for i in range(n_entries):
        tree.GetEntry(i)

        if not passes_trigger(tree):
            continue

        # ------------------ MUON SELECTION ------------------
        if hasattr(tree, "Muon_pt"):
            for j in range(len(tree.Muon_pt)):
                pt = tree.Muon_pt[j]
                eta = tree.Muon_eta[j]
                phi = tree.Muon_phi[j]
                dxy = abs(tree.Muon_dxy[j])
                dz = abs(tree.Muon_dz[j])
                tightId = tree.Muon_tightId[j]
                iso = tree.Muon_pfRelIso04_all[j]

                if (
                    pt > 30 and abs(eta) < 2.4 and
                    tightId and iso < 0.1 and
                    dxy < 0.02 and dz < 0.05
                ):
                    lepton_data["Muon"]["pt"].append(pt)
                    lepton_data["Muon"]["eta"].append(eta)
                    lepton_data["Muon"]["phi"].append(phi)

        # ------------------ ELECTRON SELECTION ------------------
        if hasattr(tree, "Electron_pt"):
            for j in range(len(tree.Electron_pt)):
                pt = tree.Electron_pt[j]
                eta = tree.Electron_eta[j]
                phi = tree.Electron_phi[j]
                abs_eta = abs(eta)
                dxy = abs(tree.Electron_dxy[j])
                dz = abs(tree.Electron_dz[j])
                wp80 = tree.Electron_mvaFall17V2Iso_WP80[j]

                in_barrel = abs_eta < 1.444
                in_endcap = 1.566 < abs_eta < 2.5

                if not (in_barrel or in_endcap):
                    continue

                if in_barrel and (dxy >= 0.05 or dz >= 0.1):
                    continue
                if in_endcap and (dxy >= 0.1 or dz >= 0.2):
                    continue

                if pt > 35 and wp80:
                    lepton_data["Electron"]["pt"].append(pt)
                    lepton_data["Electron"]["eta"].append(eta)
                    lepton_data["Electron"]["phi"].append(phi)

# ------------------ PLOTTING SECTION ------------------

def plot_histogram(data, title, x_label, filename, bins=50, x_range=None):
    hist = ROOT.TH1F(title, title, bins, *(x_range if x_range else (min(data), max(data))))
    for val in data:
        hist.Fill(val)

    c = ROOT.TCanvas()
    hist.GetXaxis().SetTitle(x_label)
    hist.GetYaxis().SetTitle("Counts")
    hist.Draw()
    c.Print(os.path.join(root_files_directory, filename))

for lepton, values in lepton_data.items():
    if values["pt"]:
        plot_histogram(values["pt"], f"{lepton} Transverse Momentum", "pT [GeV]", f"combined_{lepton.lower()}_pt.png", bins=50, x_range=(pt_threshold, pt_upper_cap))
    if values["eta"]:
        plot_histogram(values["eta"], f"{lepton} Pseudorapidity", "η", f"combined_{lepton.lower()}_eta.png", bins=50, x_range=(-3, 3))
    if values["phi"]:
        plot_histogram(values["phi"], f"{lepton} Azimuthal Angle", "ϕ [rad]", f"combined_{lepton.lower()}_phi.png", bins=50, x_range=(-3.2, 3.2))

print("All combined lepton plots generated successfully!")
