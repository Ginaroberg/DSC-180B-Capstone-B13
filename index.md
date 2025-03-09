---
title: "Projecting Crop Yields Based on ESM Emulation"
---

## Introduction

The world continues to face the impact of climate change, posing great challenges, particularly with global agriculture. Policymakers and researchers need efficient tools to assess crop productivity under certain climate scenarios. Traditional crop modeling approaches offer high accuracy, but are often computationally intensive and difficult to scale. In response, this study aims to develop a machine learning-based emulator to predict crop yields, specifically for maize, rice, wheat, and soybeans using climate and environmental data from Earth System Model simulations.

## Methods

Our methodology integrates crop yield data from the Inter-Sectoral Impact Model Intercomparison Project (ISIMIP) with emissions data to assess the long-term effects of climate change on agricultural productivity.

We focus on key emissions variables that influence crop growth:

- **Carbon Dioxide (CO₂):** A primary driver of climate change, impacting temperature and precipitation patterns.
- **Methane (CH₄):** Contributes to warming and affects atmospheric composition.
- **Black Carbon (BC) and Sulfur Dioxide (SO₂):** Influence radiative forcing and cloud formation, affecting sunlight availability and precipitation.

## Machine Learning Models

Machine learning approaches explored:

**Gaussian Process Regression (GPR):**  
GPR is a non-parametric Bayesian method that models relationships in data without assuming a fixed equation. Instead, it uses a flexible, kernel-based approach to make predictions while naturally handling uncertainty.

- Uncertainty Quantification: Provides confidence intervals to access prediction reliability
- Nonlinear Modeling: Able to capture complex relationships between emissions and crop yields
- Data Efficiency: Performs well with limited emissions data compared to Deep Learning Models
- Automatic Relevance Determination (ARD): Allows automatic identification of the most influential emission factors during training


**Random Forest Regressor (RF):**  


## Results

![RMSE_table](/assets/images/rmse_table.png)






## Discussion/Future work

The comparison between the Gaussian Process model and the Random Forest model shows key differences in prediction accuracy for crop yields. The GP model produced lower RMSE values throughout all crop yields, indicating better performance in capturing climate to yield production relationships. However, its sensitivity to missing data may limit its scalability for large scale agricultural predictions. In contrast, the RF model, while computationally efficient, showed higher RMSE values in all crops, suggesting a greater difficulty in modeling yield variability with correct accuracy. The variability in RMSE across different crops highlights how some crops, such as soybeans and wheat, are harder to predict due to their complex relationship with climate factors like precipitation, temperature, and aerosol gases like carbon dioxide, unlike the crop rice, which showed the lowest RMSE generally with both models. 

For farmers, these findings provide valuable insight into how different crops might respond to changing climate conditions. The higher RMSE for soybeans suggests that its yield is more sensitive to climate variability, making soybeans a riskier choice in regions that experience extreme weather conditions. Maize and rice show significantly lower RMSE values, which means that their yields can be predicted with more confidence. This information can guide crop selection, schedules for crop planting, and irrigation planning which can help farmers reduce the risks that come with climate change. To add on, policymakers and scientists can use these insights to develop agricultural policies and possibly a early warning systems for farmers in high-risk areas.

In the future, improving such predictive models will be crucial for increasing food security and farming practices. Refinement of the GP model by balancing accuracy and computational efficiency could enhance its  applicability in the real world. In addition, incorporating additional data sources such as soil quality and extreme weather events could further improve predictions, particularly for crops with higher RMSE values. Understanding which crops are most affected by climate variability allows for the correct adaptation strategies, such as developing drought resistant crop variations, improving irrigation systems, and/or adjusting planting schedules. Using these insights into policy frameworks and agricultural planning, farmers and decision makers can make more informed decisions, ensuring flexibility against climate-related challenges in global food production.


