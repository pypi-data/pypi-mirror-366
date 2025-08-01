import ROOT
import argparse
import pandas as pd
from uncertainties import ufloat
import prettytable as pt

"""
Usage: cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference --separate-selections --relative-error --save my_results --colored
Make sure you use the same names for regions in both .root files.
"""
def get_file_name(file):
    file = file.split("/")[-1]
    file_name = file.replace("histoOut-", "")
    file_name = file_name.replace(".root", "")
    # if from dir was passed,
    return file_name

def main():
    parser = argparse.ArgumentParser(description='Compare cutflow histograms')
    parser.add_argument('-f', '--files', nargs='+', required=True, help='Input ROOT files')
    parser.add_argument('-r', '--regions', nargs='+', required=True, help='Regions to compare')
    parser.add_argument('--labels', nargs='+', required=False, help='Labels for input files')
    parser.add_argument('--separate-selections', action='store_true', help='Keep selections separate instead of merging')
    parser.add_argument('--relative-error', action='store_true', help='Include error in the output')
    parser.add_argument('--save', nargs='?', const=True, help='Save the results to CSV files. Optionally specify a custom filename prefix.')
    parser.add_argument('--colored', action='store_true', help='Display table with colored columns for better contrast')
    
    args = parser.parse_args()    

    # Color codes for different files
    colors = ['\033[92m', '\033[94m', '\033[95m', '\033[96m', '\033[93m']  # Green, Blue, Magenta, Cyan, Yellow
    reset = '\033[0m'

    # Parse the input arguments
    files = args.files
    regions = args.regions
    labels = args.labels if args.labels else [get_file_name(file) for file in files]

    if len(labels) != len(files):
        print("Error: Number of labels must match number of files.")
        raise SystemExit(1)
    
    # Process each region separately
    for region in regions:
        df = pd.DataFrame()
        cont_dict = {}
        
        print(f"\n*** Processing region: {region} ***")
        
        for file, label in zip(files, labels):
            f = ROOT.TFile(file)
            if not f.IsOpen():
                print(f"Error: File {file} could not be opened.")
                raise SystemExit(1)

            print(f"*** Starting analysis for file: {file}, region: {region} ***")

            if not f.Get(region + "/" + "cutflow"):
                print(f"Error: No cutflow histogram found in file {file} for region {region}.")
                f.Close()
                continue
            
            hc = f.Get(region + "/" + "cutflow")
            nbins = hc.GetXaxis().GetNbins()

            labels_list = []
            contents = []
            contents_errored = []
            for i in range(1, nbins):
                labels_list.append(hc.GetXaxis().GetBinLabel(i+1))
                contents.append(ufloat(hc.GetBinContent(i+1), hc.GetBinError(i+1)))
                contents_errored.append(f"{hc.GetBinContent(i+1)} ±{format(hc.GetBinError(i+1),'.2f')}")

            if args.separate_selections:
                df[f"{label}_Selection"] = labels_list
            else: 
                df[f"Selection in region {region}"] = labels_list
            df[f"{label}_Event_After_Cut"] = contents_errored
            cont_dict[f"{label}_Event_After_Cut_ufloat"] = contents
            f.Close()

        if args.relative_error and len(cont_dict) > 1:
            print(f"*** Calculating relative error for region: {region} ***")
            error_df = pd.DataFrame.from_dict(cont_dict)
            # Collect all columns for this region
            cols = [f"{label}_Event_After_Cut_ufloat" for label in labels]
            # Get the nominal values for each file/selection
            values = error_df[cols].apply(lambda row: [x.n for x in row], axis=1)
            # Calculate mean and std for each selection
            means = values.apply(lambda x: sum(x)/len(x))
            stds = values.apply(lambda x: pd.Series(x).std())
            # Relative error: std/mean
            rel_error = stds / means
            df[f"{region}_RelativeError_AllFiles"] = rel_error

            # Print results (default behavior)
        print(f"\n*** Results for region: {region} ***")
        table = pt.PrettyTable()
        table.field_names = df.columns.tolist()
        
        for _, row in df.iterrows():
            if args.colored:
                colored_row = []
                for i, cell in enumerate(row.tolist()):
                    # Color each file's data with different colors
                    if i == 0:  # Selection column stays uncolored
                        colored_row.append(str(cell))
                    else:
                        # Determine which file this column belongs to
                        file_index = (i - 1) % len(labels)
                        colored_row.append(f"{colors[file_index % len(colors)]}{cell}{reset}")
                table.add_row(colored_row)
            else:
                table.add_row(row.tolist())
        print(table)
    if args.save:
        # Determine filename
        if isinstance(args.save, str):
            # Custom filename prefix provided
            output_filename = f"{args.save}_{region}.csv"
        else:
            # Default filename
            output_filename = f"cutflow_comparison_{region}.csv"
        
        df.to_csv(output_filename, index=False)
        print(f"*** Results for region {region} saved to \033[92m{output_filename}\033[0m ***")
        print("\n" + "*" * 50)
        print("*** All comparison results saved successfully! ***")
        print("*" * 50 + "\n")
    else:
        print("\033[91m The Table is not saved!")
        print("\033[0m*** To save the table, use \033[92m--save\033[0m option. Optionally, add a custom filename: \033[92m--save my_filename\033[0m ***\033[0m")
    
if __name__ == "__main__":
    main()