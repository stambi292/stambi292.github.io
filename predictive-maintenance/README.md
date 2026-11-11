# Fix it before it fails: predictive maintenance

**Live page:** https://stambi292.github.io/predictive-maintenance/

Service a machine too early and you throw away good life; too late and it breaks in the field. I trained machine learning models on NASA's C-MAPSS turbofan data (100 engines run to failure, 15 sensors) to predict remaining useful life, and priced maintenance policies.

## Results
| Model | RMSE on 100 test engines (cycles) |
|---|---|
| Average engine (no model) | 40.1 |
| Linear regression | 19.0 |
| Random forest | 14.8 |
| **Gradient boosting (used)** | **14.4** |

With a €100k failure cost and €10k planned service (assumptions, adjustable on the page), predictive service with a 20-cycle safety margin had **zero failures** and cost **33% less per 1,000 operating cycles** than the best fixed schedule (every 125 cycles), with **49% more operating cycles** from the same engines.

## How to run
```
pip install pandas scikit-learn
python scripts/train_model.py data   # writes data/results.json
python scripts/build_page.py         # writes index.html
```

## Data
NASA Prognostics Center of Excellence, Turbofan Engine Degradation Simulation Data Set (C-MAPSS), FD001: Saxena, Goebel, Simon and Eklund (2008). Not included here.

Independent analysis by Stephen tAMBI. Not affiliated with NASA or any manufacturer.
