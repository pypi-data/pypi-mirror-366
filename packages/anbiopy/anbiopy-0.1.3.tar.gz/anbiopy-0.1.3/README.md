# Amapy Library

Author: Juan Sebastián Pardo
License: MIT License

## Introduction
anbiopy is a Python library designed for microbiota data analysis. It is specifically intented to use when users have the following data:
- OTU observations
- OTU taxonomy
- OTU Tree
- Any kind of anthropometric or additional data

Based on these, anbiopy is able to assist users in analyzing microbiota data and possible relationships with anthropometric variables e.g., alpha diversity vs height/weight/sex/etc. 


## Library Components
anbiopy consists of 3 categories of analysis: 
1. Basic microbiota analysis
2. Graphic analysis
3. Numeric analysis

In the following segments we will go through the functionalities of each component using examples. 

## Installation
Using `pip`
```bash
pip install anbiopy
```

## Dependencies
This library is built using:
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- scikit-learn
- statsmodels
- scikit-bio

All these dependencies should be installed along with anbiopy
