# pyFLEX

🧬 **pyFLEX** is a benchmarking toolkit for evaluating CRISPR screen results against biological gold standards. It provides precision-recall analysis using reference gene sets from CORUM protein complexes, Gene Ontology Biological Processes (GO-BP), KEGG pathways, and other curated resources. The toolkit computes gene-level and complex-level performance metrics, helping researchers systematically assess the biological relevance and resolution of their CRISPR screening data.


---

## 🔧 Features

- Precision-recall curve generation for ranked gene lists

- Evaluation using CORUM complexes, GO terms, pathways

- Complex-level resolution analysis and visualization

- Easy integration into CRISPR screen workflows

---

## 📦 Installation

Suggested to use Python version `3.10` with `virtual env`.

Create `venv`

```bash
conda create -n p310 python=3.10
conda activate p310
pip install uv
```

Install pyFLEX via pip

``` bash
uv pip install pyflex
```

or 

```bash
pip install pyflex
```

or Install pyFLEX via git (to develop package in local)

```bash
git clone https://github.com/tyasird/pyFLEX.git
cd pyflex
uv pip install -e .
```



---

## 🚀 Quickstart

```python
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
    "min_genes_in_complex": 3,
    "min_genes_per_complex_analysis": 3,
    "output_folder": "output",
    "gold_standard": "CORUM",
    "color_map": "RdYlBu",
    "jaccard": False,
    "plotting": {
        "save_plot": True,
        "output_type": "png",
    },
    "preprocessing": {
        "fill_na": True,
        "normalize": False,
    },
    "corr_function": "numpy",
}

# Initialize logger, config, and output folder
pyflex.initialize(default_config)

# Load datasets and gold standard terms
data, _ = pyflex.load_datasets(inputs)
terms, genes_in_terms = pyflex.load_gold_standard()

# Run analysis
for name, dataset in data.items():
    df, pr_auc = pyflex.pra(name, dataset)
    fpc = pyflex.pra_percomplex(name, dataset, is_corr=False) 
    cc = pyflex.complex_contributions(name)

# Generate plots
pyflex.plot_auc_scores()
pyflex.plot_precision_recall_curve()
pyflex.plot_percomplex_scatter()
pyflex.plot_percomplex_scatter_bysize()
pyflex.plot_significant_complexes()
pyflex.plot_complex_contributions()

# Save Result CSVspyflex.save_results_to_csv()
pyflex.save_results_to_csv()


```

---

## 📂 Examples

- [src/pyflex/examples/basic_usage.py](src/pyflex/examples/basic_usage.py)

---

## 📃 License

MIT
