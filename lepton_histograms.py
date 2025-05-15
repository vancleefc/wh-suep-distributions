import os
import ROOT

root_files_directory = "/home/ctv19/root_macros/SuepDistribution1/"
pt_threshold = 5
pt_upper_cap = 500

lepton_data = {
    "Muon": {"pt": [], "eta": [], "phi": []},
    "Electron": {"pt": [], "eta": [], "phi": []},
    "Tau": {"pt": [], "eta": [], "phi": []},
}

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

        for lepton in lepton_data.keys():
            pt_attr = f"{lepton}_pt"
            eta_attr = f"{lepton}_eta"
            phi_attr = f"{lepton}_phi"

            if hasattr(tree, pt_attr) and hasattr(tree, eta_attr) and hasattr(tree, phi_attr):
                pts = getattr(tree, pt_attr)
                etas = getattr(tree, eta_attr)
                phis = getattr(tree, phi_attr)

                for j in range(len(pts)):
                    pt = pts[j]
                    if pt_threshold < pt < pt_upper_cap:
                        lepton_data[lepton]["pt"].append(pt)
                        lepton_data[lepton]["eta"].append(etas[j])
                        lepton_data[lepton]["phi"].append(phis[j])

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