
import itertools
import pytest
import sys
import pandas as pd
from pathlib import Path

sys.path.append("./src")

from drive import drive



# @pytest.mark.integtest
# def test_drive_full_run():
#     assert 1==1
@pytest.fixture()
def system_args_no_pheno(monkeypatch):
    monkeypatch.setattr("sys.argv", 
        [
            "drive", 
            "cluster",
            "-i",
            "./tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz",
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            "./tests/test_output/integration_test_results_no_pheno",
            "-m",
            "3",
            "--recluster",
            "--log-filename",
            "integration_test_results_no_pheno.log"
            ])
    
@pytest.fixture()
def system_args_with_pheno(monkeypatch):
    monkeypatch.setattr("sys.argv", 
        [
            "drive", 
            "cluster",
            "-i",
            "./tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz",
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            "./tests/test_output/integration_test_results_with_pheno",
            "-m",
            "3",
            "-c",
            "./tests/test_inputs/test_phenotype_file_withNAs.txt",
            "--recluster",
            "--log-file",
            "integration_test_results_with_pheno.log"
            ])
    
@pytest.fixture()
def system_args_for_dendrogram(monkeypatch):
    monkeypatch.setattr("sys.argv", 
        [
            "drive", 
            "dendrogram",
            "-i",
            "./tests/test_inputs/integration_dendrogram_test_results_no_pheno.drive_networks.txt",
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            "./tests/test_output/",
            "-n",
            "0",
            "-m",
            "3",
            "--ibd",
            "./tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz",
            "--log-file",
            "integration_dendrogram_test_results.log"
            ])


@pytest.mark.integtest
def test_drive_full_run_no_phenotypes(system_args_no_pheno):
    # Make sure the output directory exists
    Path("./tests/test_output").mkdir(exist_ok=True)

    drive.main()

    # we need to make sure the output was properly formed
    output = pd.read_csv("./tests/test_output/integration_test_results_no_pheno.drive_networks.txt", sep="\t")
    # list of errors to keep
    errors = []

    # list of columns it should have
    expected_colnames = ["clstID", "n.total", "n.haplotype", "true.positive.n", "true.positive", "falst.postive", "IDs", "ID.haplotype"]

    if not output.shape == (165, 8):
        errors.append(f"Expected the output to have 165 rows and 8 columns instead it had {output.shape[0]} rows and {output.shape[1]}")
    if [col for col in output.columns if col not in expected_colnames]:
        errors.append(f"Expected the output to have the columns: {','.join(expected_colnames)}, instead these columns were found: {','.join(output.columns)}")
        
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


@pytest.mark.integtest
def test_drive_full_run_with_phenotypes(system_args_with_pheno):
    # Make sure the output directory exists
    Path("./tests/test_output").mkdir(exist_ok=True)

    drive.main()

    # we need to make sure the output was properly formed
    output = pd.read_csv("./tests/test_output/integration_test_results_with_pheno.drive_networks.txt", sep="\t")



    # list of errors to keep
    errors = []

    #lets read in the header of the phenotype file so that we can form the additional columns
    with open("./tests/test_inputs/test_phenotype_file_withNAs.txt", "r") as pheno_input:
        grid_col, pheno1, pheno2, pheno3 = pheno_input.readline().strip().split("\t")
        
        col_combinations = list(itertools.product([pheno1,pheno2, pheno3], ["_case_count_in_network", "cases_in_network", "_excluded_count_in_network", "excluded_in_network", "_pvalue"]))

        phenotype_cols = ["min_pvalue", "min_phenotype", "min_phenotype_description"] + ["".join(val) for val in col_combinations]



    # list of columns it should have
    expected_colnames = ["clstID", "n.total", "n.haplotype", "true.positive.n", "true.positive", "falst.postive", "IDs", "ID.haplotype"] + phenotype_cols

    if not output.shape == (165, 26):
        errors.append(f"Expected the output to have 165 rows and 8 columns instead it had {output.shape[0]} rows and {output.shape[1]}")
    if [col for col in output.columns if col not in expected_colnames]:
        errors.append(f"Expected the output to have the columns: {','.join(expected_colnames)}, instead these columns were found: {','.join(output.columns)}")
        
    assert not errors, "errors occured:\n{}".format("\n".join(errors))

@pytest.mark.integtest
def test_drive_dendrogram_single_network(system_args_for_dendrogram):
    Path("./tests/test_output").mkdir(exist_ok=True)
    
    drive.main()

    output_path = Path("./tests/test_output/network_0_dendrogram.png")

    assert output_path.exists(), f"An error occurred while running the integration test for the dendrogram functionality. This error prevented the appropriate output from being generated."
