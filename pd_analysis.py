import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import LogNorm

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

data = pd.read_csv(r"predictive_maintenance.csv")

## General Info
print(data.info(), "\n")
print(data.describe(), "\n")
print(data.head(), "\n")

# which operating conditions are most associated with machine failure

print(data.isnull().sum(), "\n") # no NAN
print(data.duplicated().sum(), "\n") # no rows are duplicated

# Failures
summary = data.groupby(["Failure Type"]).agg(count=("Failure Type", "count"),
                                              avg_torque=("Torque [Nm]", "mean"),
                                              avg_tool_wear=("Tool wear [min]", "mean"),
                                              avg_speed=("Rotational speed [rpm]", "mean")).sort_values(by=["count"], ascending=False)
print(summary, "\n")

summary_drop = summary.drop('No Failure')

"""while not counting No Failure as an actual failure, from the data we can deduce the most failure is due to Heat Dissipation 
at 112 and from the mean it has the one of the highest torque right behind Overstrain Failure
after that the highest amount of failures is in Power failure and it has the highest mean speed
after that it is overstrain failure which has the highest mean torque and second highest tool wear
and tool wear failure has the highest tool wear"""

target_summary = data.groupby(["Target"]).agg(count=("Target", "count"),
                                              avg_torque=("Torque [Nm]", "mean"),
                                              avg_tool_wear=("Tool wear [min]", "mean"),
                                              avg_speed=("Rotational speed [rpm]", "mean"),
                                              avg_air_temp=("Air temperature [K]", "mean"),
                                              avg_process_temp=("Process temperature [K]", "mean"))
print(target_summary, "\n")
# From this we can deduce avg_air_temp and avg_process_temp had almost no effect on the part failing and i think the avg_speed although 
# there is a slight difference didn't have an effect on the part failing and is more of a by product of it the main thing to look at i think
# is the tool wear and torque

print(data[["Target", "Torque [Nm]", "Tool wear [min]"]].corr(),"\n")

pct_diff = ((target_summary.loc[1] - target_summary.loc[0]) / target_summary.loc[0]) * 100
pct_diff = pct_diff.drop('count')
print(pct_diff) 

## Failure-rate-by-bin-check
data['wear_bin'] = pd.cut(data['Tool wear [min]'], bins=9)
wear_failure_rate = data.groupby('wear_bin').agg(failure_rate = ('Target', 'mean'),
                                         count=('Target', 'count'))

data['torque_bin'] = pd.cut(data['Torque [Nm]'], bins=9)
torque_failure_rate = data.groupby('torque_bin').agg(failure_rate=('Target', 'mean'),
                                                     count=('Target', 'count'))
print(wear_failure_rate, '\n\n', torque_failure_rate)

## charts
###Bar chart
sns.set_theme(style='darkgrid', palette='Set2')

fig1, ax1 = plt.subplots(figsize=(10,8))
sns.barplot(summary_drop, x=summary_drop.index, y='count', ax=ax1)
plt.xticks(rotation=45, ha='right')
ax1.set_title('Failure Type Count', size=18)
n_excluded = summary.loc['No Failure', 'count']
plt.figtext(0.5, 0.01, f'Note: {n_excluded} "No Failure" machines excluded',
            ha='center', color='gray')
plt.tight_layout(rect=[0,0.06,1,1])
plt.savefig('failure_type_count.png', bbox_inches='tight', dpi=150)

### Boxplot of Torque and toolwear by target
fig2, (ax_t, ax_w)= plt.subplots(1, 2, figsize=(10,5))

sns.boxplot(data, x='Target', y='Torque [Nm]', ax=ax_t)
ax_t.set_title('Torque By Failure')
ax_t.set_xticks([0,1])
ax_t.set_xticklabels(['No Failure', 'Failure'])

sns.boxplot(data, x='Target', y='Tool wear [min]', ax=ax_w)
ax_w.set_title('Tool Wear By Failure')
ax_w.set_xticks([0,1])
ax_w.set_xticklabels(['No Failure', 'Failure'])

plt.tight_layout()
plt.savefig('wear_and_torque_failure.png', bbox_inches='tight', dpi=150)

### Correlation Heatmap 

correlation = data.drop(columns=['UDI']).corr(numeric_only=True)

fig3, ax_cor = plt.subplots(figsize=(10,8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax_cor)
plt.xticks(rotation=45, ha='right')
ax_cor.set_title('Correlation HeatMap', size=18)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', bbox_inches='tight', dpi=150)

### Scatter plot of the Failure Rate bin
plot_df_w = wear_failure_rate.reset_index()
plot_df_w['wear_mid'] = plot_df_w['wear_bin'].astype(object).apply(lambda b:b.mid).astype(float)

plot_df_t = torque_failure_rate.reset_index()
plot_df_t['torque_mid'] = plot_df_t['torque_bin'].astype(object).apply(lambda b:b.mid).astype(float)

overall = data['Target'].mean()
all_counts = pd.concat([plot_df_w['count'], plot_df_t['count']])
norm = LogNorm(vmin=all_counts.min(), vmax=all_counts.max())

fig4, (ax_tor, ax_wear) = plt.subplots(1,2, figsize=(10,5), sharey=True)

#### Wear Scatterplot
sns.scatterplot(data=plot_df_w, x='wear_mid', y='failure_rate',
                size='count', hue='count', palette='coolwarm', 
                sizes=(40,150), legend='full', ax=ax_wear)
ax_wear.set_title('Tool Wear Failure Rate')
ax_wear.axhline(data['Target'].mean(), linestyle='dashed', 
                color='gray', 
                label=f'Overall Failure Rate {overall:.1%}')
ax_wear.legend(title='Machine Count', loc='upper center', 
               bbox_to_anchor=(0.5, -0.22), ncol=5, fontsize=8,
               title_fontsize=9)
ax_wear.set_xlabel('Tool Wear (bin midpoint, min)')
ax_wear.plot(plot_df_w['wear_mid'], plot_df_w['failure_rate'],
             color='lightgreen', alpha=0.5, zorder=0)

#### Torque Scatterplot
sns.scatterplot(data=plot_df_t, x='torque_mid', y='failure_rate',
                size='count', hue='count', palette='coolwarm',
                  sizes=(40, 150),legend='full', hue_norm=norm,
                  size_norm=norm, ax=ax_tor)
ax_tor.set_title('Torque Failure Rate')
ax_tor.axhline(data['Target'].mean(), linestyle='dashed', 
               color='gray',
               label=f'Overall Failure Rate {overall:.1%}')
ax_tor.legend(title='Machine Count', loc='upper center', 
              bbox_to_anchor=(0.5, -0.22), ncol=5, fontsize=8,
              title_fontsize=9)
ax_tor.set_xlabel('Torque (bin midpoint, Nm)')
ax_tor.set_ylabel('Failure Rate')
ax_tor.yaxis.set_major_formatter(PercentFormatter(1.0))
ax_tor.plot(plot_df_t['torque_mid'], plot_df_t['failure_rate'],
            color='lightgreen', alpha=0.5, zorder=0)

plt.tight_layout()
fig4.subplots_adjust(bottom=0.3)
plt.savefig('failure_rate_scatterplot.png', bbox_inches='tight', dpi=150)
plt.show()