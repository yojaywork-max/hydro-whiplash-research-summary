# HYDRO-WHIPLASH-RESEARCH-SUMMARY
A summary of my study on hydrological whiplashes.
Whiplash, a newly coined term by climate scientist to refer to the quick transition from one extreme to the other. This project focuses on hydrological whiplash, which in this case we are looking at quick Dry-to-Wet or Wet-to-Dry event. We learn from the method of the paper: [Increasing global precipitation whiplash due to anthropogenic greenhouse gas emissions(Tan et al., 2023)](https://doi.org/10.1038/s41467-023-38510-9)

The document aim to summarize how whiplash is calculated based on Tan's framework, and some revision that we propose for further study. 
We will walk through the following sections:
**Core idea, Tan's framework, Whiplash calculation under climate change trend, Our proposed revision** .

Data source in our analysis: **ERA5-land-only** 


## Core idea of this hydrological whiplash analysis

- Motivation of moving sum on daily precipitation:

  Roughly speaking by a water resource perspective, a few days of dry or precipitation doesn't cause severe issue to the reservoir water levels, while one or a few months of dry condition can result in serious problems in water resources and thus affect our daily lives.

  Also, if looking at the daily precipitation of an area, we may notice that there are a lot of zero precipitations. This characteristic makes it hard to conduct statitical analysis on a daily basis. By cumulating 30 days of precipitation centered at each day, we can remove this technical zero-padded issue.

- Structure of whiplash
  - extremes
  - fast transition

- From a climatology perspective

  One thing to know about this analysis is that we are comparing precipitation data to the historicals (details to be discussed later in Tan's framework). Thus,a dry spell or drought can be identified as a dry extreme in this anaylsis, which is intuitive; however note that a relative smaller cumulative precipitations in wet season can also be an extreme dry event. Same logic applies to extreme wet.
  
  Now consider a scenario when in the transition seasons from climatological dry season to climatological wet season, a consecutive days of rainy days in dry season followed by a relative smaller precipitation in wet seasons could be identifies as a Wet-to-Dry whiplash event although it the climatological transition is opposite.

  The above scenario may seem counterintuitive and illogical, but in a climatology point, it is assumed that we are used to the expected climate(precipitation) given the time of a year. This example of Wet-to-Dry scenario tells us that the water supply is higher but later lower than usual for the reserviors of that area, supposing other factors remain the same. Therefore, studying whiplash and its future trend in this climatology manner can be informative to those who are managing water resources.

## Tan's framework

For a grid on the global map, we have the following four steps to identify the whiplah event on that grid. Abbbreviate precipitation as pr.

**1. Linearly detrend daily pr by annual sum, then calculate moving sum of detrended pr within 30 days**

- Sum up the daily pr into annual pr, then fit a linear relationship y = ax + b, where y = annual pr  and x = year. For example, we use the pr data from 1979 to 2019, so we have 41 years of annual pr (y) that corresponds to each year (x).
- The detrended daily pr is the original pr subtracted by the annualy trended pr. For example at 2000 Jan 1st, the detrended pr is the pr at 2000 Jan. 1st minus the annual pr of 2001.
- For each daily pr, caluclate the 30-days ( 15 days before and 15 days after ) cumulative detrended pr, denoted as $$P_{i,j}$$, where i, j represent the i-th year and j-th julian day, respectively.


**2. Calculate Standardized annual-cycle-removed cumulative pr anomalies $$P_{i,j}' = \frac{P_{i,j} - \overline{P_j}}{\sigma_j}$$, where $$\overline{P_j}$$ and $$\sigma_j$$ is the mean and standard deviation of j-th julian day over the period.**

For example, $P_{2001,1}' = \frac{P_{2001,1} - \overline{P_1}}{\sigma_1}$, where $\overline{P_1} = \sum\limits_{i = 1979}^{2019} P_{i, 1}$ and $\sigma_1 = \sqrt{\sum\limits_{i = 1979}^{2019} (P_{i, 1} - \overline{P_1})^2}$


**3. Identify wet and dry extremes**
- Let $q_{upper}, q_{lower}$ be the threshold quantiles for wet and dry extremes respectively. Note that there are two sightly different ways of defining extremes:
  - Thresholds based on the whole period:

    This is the method proposed in Tan's paper. They aggregate the $P_{i, j}'$ for all $i, j$, and then define those anomalies that are larger than $q_{upper}$ as wet events and those anomalies that are lower than $q_{lower}$ as dry events.

    > **_NOTE:_** There is one issue to discuss here. Since the variation of pr can differ significantly between wet and dry season of that grid, identifying extremes based on the whole period anomailes could result in bias. For example, consider a case that during the wet seasons, the $P_{i, j}'s$ are left-skewed and during the dry seasons, the  $P_{i, j}'s$ are right-skewed. If we identify extremes combining wet and dry seasons, most wet(dry) extreme events identifies are in wet(dry) seasons. However, what we wish to identify from a climatology perspective includes the relative wets in dry seasons and relative dries in wet seasons. Hence, a revision of the identification is proposed, see next bullet point.

  - Thresholds based on each julian day:
    This is an alternative method. Instaed of identifying extremes for the whole period, we propose to consider the seasonal variability: For each julian day, define its own upper and lower thresholds, then extremes identifies are based on the historical of the julian day.

![alt text](https://github.com/yojaywork-max/hydro-whiplash-research-summary/blob/main/images/combine.png?raw=true)

![alt text](https://github.com/yojaywork-max/hydro-whiplash-research-summary/blob/main/images/seperate.png?raw=true)

**4. Identify whiplash, both Dry-to-Wet and Wet-to-Dry**



## Whiplash calculation under climate change trend

- An idealized model

## Our proposed revision
- Thresholds calculated for each day of year (DoY) rather than threshold for the whole period anomalies: to remove seasonal information.
- Not fixing thresholds( calculate threshold using moving period?).
