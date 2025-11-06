1. create & activate venv, install deps
python -m venv .venv
# windows
.venv\Scripts\activate
# mac/linux
# source .venv/bin/activate

pip install -r requirements.txt

2. Generate dataset (or run whole pipeline runner)
# either run generate manually
python generate_data.py --rows 15000

# then train
python train.py --config config.yaml

# test single prediction
python predict.py --model models/revenue_model.joblib --single --price 120 --marketing_spend 300 --units_sold 100 --prev_month_revenue 10000 --product_id P001 --region North --channel Online --date 2021-08-01

3. Or run the pipeline runner (generate → train → predict)
python pipeline_runner.py

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Revenue Predictor – Automated ML Pipeline (Train → Predict → Visualize)

Overview
---------
This project is an end-to-end machine learning pipeline for predicting revenue based on generated synthetic business data. The workflow includes:
1. Data generation
2. Model training
3. Batch and single-instance prediction
4. Visualization in Power BI

It uses Python, scikit-learn, pandas, and joblib, with YAML configuration for easy customization.

Folder Structure
----------------
revenue_predictor/
│
├── data/
│   ├── revenue_data.csv
│   └── predictions.csv
│
├── models/
│   └── revenue_model.joblib
│
├── config.yaml
├── pipeline.yaml
├── generate_data.py
├── train.py
├── predict.py
├── utils.py
└── README.txt

Virtual Environment Setup
--------------------------
It’s strongly recommended to run this project in a virtual environment.

Create a virtual environment:
    python -m venv .venv

Activate it:
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate

Install dependencies:
    pip install -r requirements.txt

Dependencies
-------------
You can create a requirements.txt file like this:

    pandas
    numpy
    scikit-learn==1.7.2
    joblib
    pyyaml

Run the Pipeline
----------------
The automated pipeline is defined in pipeline.yaml.

Example (in PowerShell or terminal):

    python run_pipeline.py

Each step in pipeline.yaml looks like this:

    steps:
      - name: generate
        script: generate_data.py
        args: ["--rows", "15000", "--out", "data/revenue_data.csv"]

      - name: train
        script: train.py
        args: ["--config", "config.yaml", "--out", "models/revenue_model.joblib"]

      - name: predict
        script: predict.py
        args: ["--config", "config.yaml", "--input", "data/revenue_data.csv",
               "--model", "models/revenue_model.joblib", "--output", "data/predictions.csv"]

This will sequentially:
1. Generate synthetic data.
2. Train a regression model on the data.
3. Predict revenue for all rows in the dataset.

Manual Step-by-Step Run
-----------------------
You can also run each step individually:

1. Generate data:
    python generate_data.py --rows 15000 --out data/revenue_data.csv

2. Train model:
    python train.py --config config.yaml --out models/revenue_model.joblib

3. Predict batch:
    python predict.py --config config.yaml --input data/revenue_data.csv \
                      --model models/revenue_model.joblib --output data/predictions.csv

4. Predict a single instance:
    python predict.py --config config.yaml --model models/revenue_model.joblib \
                      --single --data 300 10 2 5

(Replace numeric values according to your feature order in config.yaml.)

Fixing Unicode Errors on Windows
--------------------------------
If you see errors like:
    UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'

You can fix this by:
1. Replacing emoji characters in all print() statements.
2. Running Python with UTF-8 mode:
       set PYTHONUTF8=1
3. Using PowerShell or VS Code Terminal (both handle UTF-8 correctly).

Visualizing Predictions in Power BI
-----------------------------------
Once you have data/predictions.csv generated, you can visualize it in Power BI:

1. Open Power BI Desktop.
2. Go to “Get Data” → “Text/CSV”.
3. Load data/predictions.csv.
4. Create visuals:
   - X-axis: feature (e.g., marketing_spend or day_of_week)
   - Y-axis: predicted_revenue
   - Add slicers for filtering categorical fields
   - Add line charts to show trends across date or month

Recommended visuals:
- Line chart: date vs predicted_revenue
- Bar chart: marketing_spend vs predicted_revenue
- Table: All features + predicted_revenue
- KPI card: Average predicted revenue

Files Description
-----------------
config.yaml
Defines features and model configuration.

pipeline.yaml
Specifies step-by-step execution of the data pipeline.

generate_data.py
Creates synthetic training data.

train.py
Trains a regression pipeline using numeric, categorical, and date features.
Saves the model as models/revenue_model.joblib.

predict.py
Loads the trained model and generates predictions for batch or single inputs.

utils.py
Contains helper functions for date feature extraction used in the pipeline.

License
-------
MIT License — free for educational and commercial use.

Author
------
Developed by Nihal Manohar
For questions or improvements: contact via GitHub or email.

