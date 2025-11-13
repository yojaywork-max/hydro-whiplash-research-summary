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

**1. Linearly detrend daily precipitation by annual sum, then calculate moving sum of detrended precipitation within 30 days**

**2. Calculate Standardized annual-cycle-removed cumulative precipitation anomalies $$P_{i,j}' = \frac{P_{i,j} - \overline{P_j}}{\sigma_j}$$**

**3. Identify wet and dry extremes**

**4. Identify whiplash, both Dry-to-Wet and Wet-to-Dry**



## Whiplash calculation under climate change trend

- An idealized model

## Our proposed revision
- Thresholds calculated for each day of year (DoY) rather than threshold for the whole period anomalies: to remove seasonal information.
- Not fixing thresholds( calculate threshold using moving period?).
