import os
import ROOT

root_files_directory = "/home/ctv19/root_macros/SuepDistribution1/"

all_met = []
all_met_phi = []

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
        if hasattr(tree, "MET_pt") and hasattr(tree, "MET_phi"):
            met = tree.MET_pt
            met_phi = tree.MET_phi
            all_met.append(met)
            all_met_phi.append(met_phi)

def plot_histogram(data, title, x_label, filename, bins=50, x_range=None):
    hist = ROOT.TH1F(title, title, bins, *(x_range if x_range else (min(data), max(data))))
    for val in data:
        hist.Fill(val)

    c = ROOT.TCanvas()
    hist.GetXaxis().SetTitle(x_label)
    hist.GetYaxis().SetTitle("Counts")
    hist.Draw()
    c.Print(os.path.join(root_files_directory, filename))

plot_histogram(all_met, "Missing Transverse Energy", "MET [GeV]", "combined_met_pt.png", bins=50, x_range=(0, 500))
plot_histogram(all_met_phi, "MET Azimuthal Angle", "MET_phi [rad]", "combined_met_phi.png", bins=50, x_range=(-3.2, 3.2))

print("MET histograms generated successfully!")