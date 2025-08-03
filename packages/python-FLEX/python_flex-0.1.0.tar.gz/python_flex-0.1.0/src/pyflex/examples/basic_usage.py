"""
Basic usage example of the pyFLEX package.
Demonstrates initialization, data loading, analysis, and plotting.
"""
#%%
import pyflex 

inputs = {

    "Melanoma (63 Screens)": {
        "path": pyflex.get_example_data_path("melanoma_cell_lines_500_genes.csv"), 
        "sort": "high"
    },
    "Liver (24 Screens)": {
        "path": pyflex.get_example_data_path("liver_cell_lines_500_genes.csv"), 
        "sort": "high"
    },
    "Neuroblastoma (37 Screens)": {
        "path": pyflex.get_example_data_path("neuroblastoma_cell_lines_500_genes.csv"), 
        "sort": "high"
    },


}

default_config = {
    "min_genes_in_complex": 2,
    "min_genes_per_complex_analysis": 2,
    "output_folder": "output",
    "gold_standard": "GOBP",
    "color_map": "RdYlBu",
    "jaccard": True,
    "plotting": {
        "save_plot": True,
        "output_type": "png",
    },
    "preprocessing": {
        "fill_na": True,
        "normalize": False,
    },
    "corr_function": "numpy",
    "logging": {  
        "visible_levels": ["DONE","STARTED"]  # "PROGRESS", "STARTED", ,"INFO","WARNING"
    }
}

# Initialize logger, config, and output folder
pyflex.initialize(default_config)

# Load datasets and gold standard terms

data, _ = pyflex.load_datasets(inputs)
terms, genes_in_terms = pyflex.load_gold_standard()


#%%
# Run analysis
for name, dataset in data.items():
    df, pr_auc = pyflex.pra(name, dataset)
    fpc = pyflex.pra_percomplex(name, dataset, is_corr=False) 
    cc = pyflex.complex_contributions(name)


#%%
# Generate plots
pyflex.plot_auc_scores()
pyflex.plot_precision_recall_curve()
pyflex.plot_percomplex_scatter()
pyflex.plot_percomplex_scatter_bysize()
pyflex.plot_significant_complexes()
pyflex.plot_complex_contributions()


#%%
# Save results to CSV
pyflex.save_results_to_csv()












