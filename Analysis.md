# What Predicts Machine Failure? A Predictive Maintenance Analysis

## Background
This analysis uses the AI4I 2020 Predictive Maintenance Dataset (https://archive.ics.uci.edu/dataset/601/ai4i), a synthetic dataset modeled on real industrial data from the UCI Machine Learning Repository (S. Matzka, 2020), downloaded via Kaggle. It shows the operating readings of 10,000 machines such as air and process temperatures, rotational speed, torque, tool wear, and machine type. This analysis examines which conditions are most associated with failure. In this data, 339 of the 10,000 machines (3.39%) failed. The most common recorded failure types were heat dissipation (112) and power (95).


## Approach
To examine the data I first checked for missing values and duplicates. After that I checked for any discrepancies in the data and found 27 rows where the failure flag and the failure type disagree. Next I compared the averages of the machines that failed with the ones that didn't, and measured the correlations. The results showed that the torque and tool wear differed most between failed and non-failed machines, while temperatures and speed barely differed. I therefore divided and examined the torque and tool wear more closely and calculated the failure rate in each range. I then visualized the results in four charts. Finally I re-ran the key results in SQL (SQLite), which confirmed the same patterns.

## Key Findings
Failure risk across torque is lowest in the middle ranges and rises at both extremes. The middle range sits below the 3.39% overall rate, with 0.6% at 20 to 39 Nm and 2.9% at 40 to 54 Nm. Failure rates rise to 15% below 20 Nm (228 machines), 17% at 55 to 64 (553 machines) and 83% at 65 and above (65 machines).

Tool wear on the other hand, stays at or below the base rate (3.39%) until about 200 minutes and then climbs. In the bands below 200 minutes, the failure rate is about 2 to 2.6%, then 14% at 200 to 229 (756 machines) and 31% at 230 and above (45 machines).

The correlations look weak (0.19 for torque and 0.11 for tool wear), even though the effects are strong, because correlation only measures straight-line relationships and misses a U-shape and a threshold. Temperature and speed differed little between failed and non-failed machines; for example, the average speed was 1,496 rpm for failed machines and 1,540 for the rest, and the air temperature differed by under 1 K.

## Limitations
The extreme bands are small groups (65 machines in the top torque band and 45 in the top tool wear band). Therefore, they are less precise. Additionally, the rates depend on where the band edges are drawn. Since the data is synthetic, the patterns reflect how the data was generated and may not transfer to real-world machines. This analysis displays associations, not cause. Moreover, 27 of the 10,000 rows have a failure flag that disagrees with the failure type, and all rates use the flag.


## Recommendations
Based on the analysis, I would recommend monitoring machines whose torque falls below 20 Nm or goes above 55 Nm. Additionally, I recommend planning tool replacements before about 200 minutes of wear. However, the thresholds should be verified on real equipment, because the data is synthetic.