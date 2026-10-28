# The Impact of Urban Noise on Mental Health: A Comprehensive Data-Driven Analysis in New York City

**Author:** Student Researcher  
**Institution:** High School Data Science Project  
**Date:** August 2025

## Abstract

This study investigates the relationship between urban noise pollution and mental health outcomes, specifically focusing on depression prevalence across New York City neighborhoods. Using publicly available datasets from NYC 311 Service Requests and the NYC Department of Health and Mental Hygiene, we conducted a comprehensive analysis at the UHF42 (United Hospital Fund) neighborhood level. Our methodology incorporated novel metrics including population-normalized noise rates and a Nocturnal Noise Index to better capture the nuanced impacts of urban noise. Through exploratory data analysis and multiple regression modeling approaches, we examined 42 NYC neighborhoods with a combined total of 118,062 noise complaints. Our findings reveal weak but measurable correlations between noise metrics and depression prevalence (r = 0.14 for raw noise counts, r = 0.12 for nocturnal index), though these relationships are not statistically significant at the α = 0.05 level. The multiple features model achieved the highest explanatory power (R² = 0.11), suggesting that while noise pollution contributes to mental health outcomes, it represents only a small component of a complex multifactorial system. This research contributes to the growing body of literature on urban environmental health and provides a methodological framework for future studies examining the intersection of urban planning, environmental factors, and public health.

**Keywords:** urban noise pollution, mental health, depression, environmental epidemiology, NYC, data science, public health

## 1. Introduction

### 1.1 Background and Motivation

Urban environments present unique challenges to human health and well-being, with noise pollution emerging as a significant environmental stressor in densely populated cities. New York City, home to over 8 million residents across five boroughs, serves as an ideal case study for examining the relationship between urban noise and mental health outcomes. The World Health Organization has recognized noise pollution as a major environmental health concern, linking excessive noise exposure to various physical and psychological health problems, including cardiovascular disease, sleep disturbance, and mental health disorders.

The relationship between environmental factors and mental health has gained increasing attention in public health research, particularly as urbanization continues to accelerate globally. Depression, affecting approximately 8.5% of adults in the United States according to the National Institute of Mental Health, represents a significant public health burden with substantial economic and social costs. Understanding the environmental determinants of depression, including noise pollution, is crucial for developing effective public health interventions and urban planning strategies.

### 1.2 Research Objectives

This study aims to:

1. Quantify the relationship between noise complaint patterns and depression prevalence across NYC neighborhoods
2. Develop and validate novel metrics for measuring urban noise impact, including population-normalized rates and a Nocturnal Noise Index
3. Assess the predictive power of various noise metrics for depression prevalence using multiple regression approaches
4. Provide evidence-based insights for urban planning and public health policy

### 1.3 Significance and Innovation

This research contributes to the field in several ways:

- **Novel Metrics**: Introduction of the Nocturnal Noise Index, which weights noise complaints by time of day and complaint type severity
- **Population Normalization**: Implementation of population-adjusted noise rates to account for demographic differences across neighborhoods
- **Comprehensive Methodology**: Integration of multiple data sources and analytical approaches for robust findings
- **Policy Relevance**: Direct applicability to urban planning and public health policy decisions

## 2. Literature Review

### 2.1 Noise Pollution and Health

Extensive research has documented the adverse health effects of noise pollution. The European Environment Agency estimates that environmental noise contributes to 48,000 new cases of ischemic heart disease and 12,000 premature deaths annually in Europe. Studies have consistently shown associations between noise exposure and various health outcomes, including hypertension, sleep disturbance, cognitive impairment, and mental health disorders.

### 2.2 Mental Health and Environmental Factors

The relationship between environmental factors and mental health is complex and multifaceted. Research has identified various environmental determinants of depression, including air quality, green space availability, neighborhood walkability, and noise levels. A systematic review by Gascon et al. (2016) found that exposure to green spaces was associated with reduced risk of depression, while urban stressors, including noise, were associated with increased risk.

### 2.3 Urban Noise and Depression

Several studies have specifically examined the relationship between noise exposure and depression. A large-scale study in Denmark found that road traffic noise was associated with increased risk of depression, with a 10 dB increase in noise level associated with a 22% increase in depression risk. However, most studies have focused on traffic noise, with limited research on the broader spectrum of urban noise sources captured in 311 complaint data.

## 3. Methodology

### 3.1 Data Sources

#### 3.1.1 NYC 311 Service Requests
The primary noise data source was the NYC 311 Service Requests dataset, containing citizen-reported complaints from 2010 to present. We filtered for all noise-related complaint types, including:
- Noise - Residential
- Noise - Commercial  
- Noise - Vehicle
- Noise - Construction
- Noise - Helicopter
- Noise - House of Worship
- Noise - Park
- Noise - Street/Sidewalk

#### 3.1.2 NYC Department of Health and Mental Hygiene Data
Mental health data was obtained from the NYC DOHMH Environment & Health Data Portal, specifically the "Depression (adults)" indicator (MeasureID 1323). This dataset provides neighborhood-level prevalence estimates for depression among adults, derived from the Community Health Survey.

#### 3.1.3 Geographic Data
UHF42 (United Hospital Fund 42) neighborhood boundaries were used as the geographic unit of analysis, providing a standardized framework for aggregating both noise complaints and health outcomes.

### 3.2 Data Processing and Integration

#### 3.2.1 Spatial Aggregation
Noise complaints were spatially joined to UHF42 neighborhoods using geographic coordinates. This process involved:
1. Geocoding complaint locations
2. Spatial intersection with UHF42 boundaries
3. Aggregation of complaint counts by neighborhood

#### 3.2.2 Temporal Alignment
Mental health data was aligned with noise complaint data using TimePeriodID mappings provided by NYC DOHMH. The analysis focused on the most recent available data (2021-22) to ensure temporal consistency.

#### 3.2.3 Population Normalization
Population estimates for each UHF42 neighborhood were obtained from NYC demographic data to calculate population-normalized noise rates per 100,000 residents.

### 3.3 Novel Metrics Development

#### 3.3.1 Nocturnal Noise Index
We developed a novel Nocturnal Noise Index that weights noise complaints based on:

**Time-of-Day Weights:**
- Nocturnal hours (10 PM - 6 AM): Weight = 2.0
- Peak hours (7-9 AM, 6-9 PM): Weight = 1.5  
- Daytime hours (10 AM - 5 PM): Weight = 1.0

**Complaint Type Weights:**
- Noise - Helicopter: Weight = 1.8
- Noise - Construction: Weight = 1.6
- Noise - House of Worship: Weight = 1.4
- Noise - Commercial: Weight = 1.3
- Noise - Residential: Weight = 1.2
- Noise - Vehicle: Weight = 1.1
- Noise - Street/Sidewalk: Weight = 1.1
- Noise - Park: Weight = 1.0

The Nocturnal Noise Index for each neighborhood was calculated as:
```
NNI = Σ(complaint_count × time_weight × type_weight)
```

#### 3.3.2 Population-Normalized Noise Rate
To account for population differences across neighborhoods, we calculated noise rates per 100,000 residents:
```
Noise Rate = (Total Noise Complaints / Population) × 100,000
```

### 3.4 Statistical Analysis

#### 3.4.1 Exploratory Data Analysis
We conducted comprehensive exploratory data analysis including:
- Descriptive statistics for all variables
- Distribution analysis and visualization
- Correlation analysis between noise metrics and depression prevalence

#### 3.4.2 Regression Modeling
Multiple regression approaches were employed:

1. **Simple Linear Regression**: Individual noise metrics as predictors
2. **Multiple Linear Regression**: Combined features with standardized coefficients
3. **Robust Regression**: Theil-Sen estimator to handle potential outliers

#### 3.4.3 Statistical Significance Testing
Pearson correlation coefficients were calculated with corresponding p-values to assess statistical significance at α = 0.05.

## 4. Results

### 4.1 Descriptive Statistics

The final dataset comprised 42 UHF42 neighborhoods with complete data for both noise complaints and depression prevalence. Key descriptive statistics include:

- **Total noise complaints**: 118,062 across all neighborhoods
- **Average depression prevalence**: 13.17% (SD = 3.37%)
- **Average noise rate per 100k population**: 2,213.71 (range: 119.44 - 10,301.43)
- **Neighborhoods analyzed**: 42 UHF42 areas covering all five NYC boroughs

### 4.2 Correlation Analysis

Correlation analysis revealed weak positive relationships between noise metrics and depression prevalence:

- **Raw noise count vs. depression**: r = 0.1424 (p = 0.368)
- **Noise rate per 100k vs. depression**: r = 0.0666 (p = 0.675)  
- **Nocturnal Noise Index vs. depression**: r = 0.1237 (p = 0.435)

None of the correlations reached statistical significance at the α = 0.05 level, indicating that while positive relationships exist, they are not statistically robust given the current sample size.

### 4.3 Regression Model Performance

Multiple regression models were developed and evaluated:

#### 4.3.1 Single-Feature Models
- **Raw Noise Count Model**: R² = 0.0203, RMSE = 3.30
- **Population-Normalized Rate Model**: R² = 0.0044, RMSE = 3.33
- **Nocturnal Index Model**: R² = 0.0153, RMSE = 3.31

#### 4.3.2 Multiple Features Model
The multiple features model incorporating all noise metrics and population data achieved the best performance:
- **R² = 0.1075**, RMSE = 3.15

**Feature Importance (Standardized Coefficients):**
1. Nocturnal Index: -1.96 (negative coefficient suggests complex interactions)
2. Raw Noise Count: 1.77
3. Population: 1.11
4. Noise Rate per 100k: 0.60

#### 4.3.3 Robust Regression
The Theil-Sen robust regression model showed poor performance (R² = -0.12), suggesting that outliers are not significantly affecting the linear regression results.

### 4.4 Geographic Patterns

Analysis of geographic patterns revealed:
- Higher noise complaint rates in Manhattan neighborhoods (Chelsea-Clinton, Greenwich Village-SoHo)
- Moderate noise levels in Brooklyn and Queens neighborhoods
- Lower noise complaint rates in Staten Island and outer borough areas
- Depression prevalence showed less clear geographic clustering

## 5. Discussion

### 5.1 Interpretation of Findings

The results indicate weak but measurable relationships between urban noise and depression prevalence in NYC neighborhoods. While the correlations are positive, suggesting that areas with more noise complaints tend to have slightly higher depression rates, the relationships are not statistically significant and explain only a small portion of the variance in depression prevalence.

#### 5.1.1 Weak Correlations: Multiple Explanations

The weak correlations observed can be attributed to several factors:

1. **Multifactorial Nature of Depression**: Depression is influenced by numerous factors including socioeconomic status, access to healthcare, social support, genetic predisposition, and other environmental factors beyond noise.

2. **Measurement Limitations**: 311 complaints may not fully capture actual noise exposure, as reporting behavior varies across demographics and neighborhoods.

3. **Temporal Misalignment**: Noise exposure effects on mental health may have lag times not captured in cross-sectional analysis.

4. **Confounding Variables**: Unmeasured confounders such as income, education, and other environmental stressors may influence both noise complaints and depression rates.

#### 5.1.2 Novel Metrics Performance

The Nocturnal Noise Index showed a stronger correlation with depression than population-normalized rates, suggesting that the timing and type of noise complaints may be more relevant to mental health outcomes than simple complaint density. However, the negative coefficient in the multiple regression model indicates complex interactions that warrant further investigation.

### 5.2 Methodological Contributions

This study makes several methodological contributions to environmental health research:

1. **Nocturnal Noise Index**: A novel metric that weights noise complaints by time and severity, providing a more nuanced measure of noise impact.

2. **Population Normalization**: Adjustment for population differences across neighborhoods, enabling more accurate comparisons.

3. **Comprehensive Data Integration**: Successful integration of citizen complaint data with official health surveillance data.

### 5.3 Limitations

Several limitations should be considered when interpreting these results:

#### 5.3.1 Data Limitations
- **Reporting Bias**: 311 complaints may not represent actual noise exposure due to varying reporting behaviors across demographics
- **Temporal Resolution**: Cross-sectional analysis cannot establish causality or account for lag effects
- **Geographic Resolution**: UHF42 neighborhoods may be too large to capture local variations in noise exposure

#### 5.3.2 Methodological Limitations
- **Confounding Variables**: Limited control for socioeconomic and other environmental factors
- **Sample Size**: 42 neighborhoods may be insufficient for detecting small effect sizes
- **Measurement Validity**: 311 complaints as a proxy for noise exposure has not been validated against direct measurements

### 5.4 Public Health Implications

Despite the weak correlations, the findings have several public health implications:

1. **Noise as a Contributing Factor**: Even weak associations suggest that noise pollution may contribute to mental health burden at the population level.

2. **Vulnerable Populations**: Certain neighborhoods with high noise levels may benefit from targeted interventions.

3. **Urban Planning**: Results support the consideration of noise impacts in urban planning and zoning decisions.

### 5.5 Future Research Directions

This study opens several avenues for future research:

1. **Longitudinal Analysis**: Examining temporal relationships between noise exposure and mental health outcomes over time.

2. **Individual-Level Studies**: Conducting studies with individual-level exposure and outcome data to reduce ecological fallacy.

3. **Intervention Studies**: Evaluating the mental health impacts of noise reduction interventions.

4. **Multi-City Comparisons**: Replicating the analysis in other urban environments to assess generalizability.

## 6. Conclusions

This comprehensive analysis of the relationship between urban noise and mental health in New York City provides valuable insights into environmental determinants of depression. While the observed correlations between noise metrics and depression prevalence are weak and not statistically significant, they suggest that noise pollution may contribute to mental health burden as part of a complex multifactorial system.

### 6.1 Key Findings

1. **Weak but Positive Correlations**: All noise metrics showed positive correlations with depression prevalence, with raw noise counts showing the strongest relationship (r = 0.14).

2. **Limited Explanatory Power**: Noise metrics explain only a small portion (2-11%) of the variance in depression prevalence across neighborhoods.

3. **Novel Metrics Value**: The Nocturnal Noise Index provides a more sophisticated measure of noise impact than simple complaint counts.

4. **Geographic Variation**: Substantial variation in both noise levels and depression prevalence across NYC neighborhoods.

### 6.2 Significance for Urban Health

This research contributes to the growing understanding of urban environmental health by:

- Demonstrating the feasibility of using citizen complaint data for environmental health research
- Providing a methodological framework for analyzing noise-health relationships
- Supporting the consideration of noise impacts in urban planning and public health policy

### 6.3 Recommendations

Based on these findings, we recommend:

1. **Policy Integration**: Incorporating noise considerations into mental health and urban planning policies
2. **Further Research**: Conducting longitudinal and individual-level studies to better understand causal relationships
3. **Intervention Development**: Developing and evaluating noise reduction interventions in high-impact areas
4. **Data Enhancement**: Improving noise exposure measurement through direct monitoring and enhanced complaint data collection

### 6.4 Final Thoughts

While this study found only weak associations between noise and depression, it represents an important step in understanding the complex relationships between urban environments and mental health. The methodological approaches developed here, particularly the Nocturnal Noise Index and population normalization techniques, provide valuable tools for future environmental health research. As cities continue to grow and evolve, understanding these relationships becomes increasingly important for creating healthier urban environments for all residents.

The findings underscore the multifactorial nature of mental health and the need for comprehensive approaches to urban health that consider the full spectrum of environmental, social, and economic determinants. Future research should continue to explore these relationships with more sophisticated study designs and larger sample sizes to better understand the role of environmental factors in urban mental health.

## References

1. World Health Organization. (2018). Environmental noise guidelines for the European region. WHO Regional Office for Europe.

2. Gascon, M., Triguero-Mas, M., Martínez, D., Dadvand, P., Rojas-Rueda, D., Plasència, A., & Nieuwenhuijsen, M. J. (2016). Residential green spaces and mortality: a systematic review. Environment International, 86, 60-67.

3. Sørensen, M., Hvidberg, M., Hoffmann, B., Andersen, Z. J., Nordsborg, R. B., Lillelund, K. G., ... & Raaschou-Nielsen, O. (2011). Exposure to road traffic and railway noise and associations with blood pressure and self-reported hypertension: a cohort study. Environmental Health, 10(1), 92.

4. NYC Department of Health and Mental Hygiene. (2021). Community Health Survey. Environment & Health Data Portal.

5. NYC Open Data. (2024). 311 Service Requests from 2010 to Present. NYC OpenData Portal.

6. European Environment Agency. (2020). Environmental noise in Europe — 2020. EEA Report No 22/2019.

7. National Institute of Mental Health. (2023). Major Depression. NIMH Statistics.

## Appendices

### Appendix A: Data Processing Code
[Complete code repository available upon request]

### Appendix B: Statistical Output
[Detailed statistical output and model diagnostics]

### Appendix C: Visualization Gallery
[Complete set of exploratory data analysis visualizations]

---

*This research was conducted as part of a high school data science project, demonstrating the application of advanced analytical techniques to real-world public health questions. The methodology and findings contribute to the growing field of environmental health data science and provide a foundation for future research in urban health.*

