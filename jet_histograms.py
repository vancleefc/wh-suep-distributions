import os
import ROOT

root_files_directory = "" #file path
pt_threshold = 30

all_jet_pts = []
all_jet_etas = []
all_jet_phis = []

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
        if hasattr(tree, "Jet_pt") and hasattr(tree, "Jet_eta") and hasattr(tree, "Jet_phi"):
            n_jets = len(tree.Jet_pt)
            for j in range(n_jets):
                pt = tree.Jet_pt[j]
                if pt > pt_threshold:
                    all_jet_pts.append(pt)
                    all_jet_etas.append(tree.Jet_eta[j])
                    all_jet_phis.append(tree.Jet_phi[j])

def plot_histogram(data, title, x_label, filename, bins=50, x_range=None):
    hist = ROOT.TH1F(title, title, bins, *(x_range if x_range else (min(data), max(data))))
    for val in data:
        hist.Fill(val)

    c = ROOT.TCanvas()
    hist.GetXaxis().SetTitle(x_label)
    hist.GetYaxis().SetTitle("Counts")
    hist.Draw()
    c.Print(os.path.join(root_files_directory, filename))

plot_histogram(all_jet_pts, "Jet Transverse Momentum", "Jet pT [GeV]", "combined_jet_pt.png", bins=50, x_range=(pt_threshold, 1000))
plot_histogram(all_jet_etas, "Jet Pseudorapidity", "Jet η", "combined_jet_eta.png", bins=50, x_range=(-5, 5))
plot_histogram(all_jet_phis, "Jet Azimuthal Angle", "Jet ϕ [rad]", "combined_jet_phi.png", bins=50, x_range=(-3.2, 3.2))

print("All combined jet plots generated successfully!")
