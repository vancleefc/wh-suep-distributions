import os
import ROOT

root_files_directory = "" #file path
pt_threshold = 5

all_photon_pts = []
all_photon_etas = []
all_photon_phis = []

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
        if hasattr(tree, "Photon_pt") and hasattr(tree, "Photon_eta") and hasattr(tree, "Photon_phi"):
            n_photons = len(tree.Photon_pt)
            for j in range(n_photons):
                pt = tree.Photon_pt[j]
                if pt > pt_threshold:
                    all_photon_pts.append(pt)
                    all_photon_etas.append(tree.Photon_eta[j])
                    all_photon_phis.append(tree.Photon_phi[j])

def plot_histogram(data, title, x_label, filename, bins=50, x_range=None):
    hist = ROOT.TH1F(title, title, bins, *(x_range if x_range else (min(data), max(data))))
    for val in data:
        hist.Fill(val)

    c = ROOT.TCanvas()
    hist.GetXaxis().SetTitle(x_label)
    hist.GetYaxis().SetTitle("Counts")
    hist.Draw()
    c.Print(os.path.join(root_files_directory, filename))

plot_histogram(all_photon_pts, "Photon Transverse Momentum", "pT [GeV]", "combined_photon_pt.png", bins=50, x_range=(0, max(all_photon_pts) if all_photon_pts else 100))
plot_histogram(all_photon_etas, "Photon Pseudorapidity", "η", "combined_photon_eta.png", bins=50, x_range=(-3, 3))
plot_histogram(all_photon_phis, "Photon Azimuthal Angle", "ϕ [rad]", "combined_photon_phi.png", bins=50, x_range=(-3.2, 3.2))

print("Photon plots generated successfully!")
