import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

print("Creating comprehensive financial comparison charts...")

# Set seaborn style for professional appearance
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Financial data from the analysis
data = {
    'Company': ['AAPL', 'AAPL', 'AAPL', 'MSFT', 'MSFT', 'MSFT'],
    'Year': ['2022', '2023', '2024', '2022', '2023', '2024'],
    'Gross_Margin': [0.4331, 0.4413, 0.4621, 0.6840, 0.6892, 0.6976],
    'Operating_Margin': [0.3029, 0.2982, 0.3151, 0.4206, 0.4177, 0.4464],
    'Net_Profit_Margin': [0.2531, 0.2531, 0.2397, 0.3669, 0.3415, 0.3596],
    'Return_on_Equity': [1.7546, 1.7195, 1.5741, 0.8735, 0.3882, 0.3713],
    'Return_on_Assets': [0.2836, 0.2750, 0.2613, 0.3987, 0.1863, 0.1907]
}

df = pd.DataFrame(data)

# Create comprehensive financial analysis charts
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Comprehensive Financial Analysis: AAPL vs MSFT (2022-2024)', fontsize=18, fontweight='bold', y=0.98)

# Colors for companies
colors = {'AAPL': '#007AFF', 'MSFT': '#00C851'}

# Chart 1: Margin Trends Over Time
metrics = ['Gross_Margin', 'Operating_Margin', 'Net_Profit_Margin']
years = ['2022', '2023', '2024']

for i, metric in enumerate(metrics):
    aapl_values = df[df['Company'] == 'AAPL'][metric].values
    msft_values = df[df['Company'] == 'MSFT'][metric].values
    
    axes[0,0].plot(years, aapl_values, 'o-', label=f'AAPL {metric.replace("_", " ")}', 
                   color=colors['AAPL'], linewidth=2, alpha=0.7 + i*0.1)
    axes[0,0].plot(years, msft_values, 's-', label=f'MSFT {metric.replace("_", " ")}', 
                   color=colors['MSFT'], linewidth=2, alpha=0.7 + i*0.1)

axes[0,0].set_title('Profitability Margins Trends', fontsize=14, fontweight='bold')
axes[0,0].set_xlabel('Year')
axes[0,0].set_ylabel('Margin Ratio')
axes[0,0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0,0].grid(True, alpha=0.3)

# Chart 2: 2024 Margin Comparison (Bar Chart)
margin_2024 = df[df['Year'] == '2024'][['Company', 'Gross_Margin', 'Operating_Margin', 'Net_Profit_Margin']]
margin_data = margin_2024.melt(id_vars=['Company'], var_name='Metric', value_name='Value')
margin_data['Metric'] = margin_data['Metric'].str.replace('_', ' ')

sns.barplot(data=margin_data, x='Metric', y='Value', hue='Company', 
            palette=colors, ax=axes[0,1])
axes[0,1].set_title('2024 Profitability Margins Comparison', fontsize=14, fontweight='bold')
axes[0,1].set_ylabel('Margin Ratio')
axes[0,1].set_xlabel('')
axes[0,1].tick_params(axis='x', rotation=45)
axes[0,1].legend(title='Company')

# Chart 3: Return on Equity Trends
aapl_roe = df[df['Company'] == 'AAPL']['Return_on_Equity'].values
msft_roe = df[df['Company'] == 'MSFT']['Return_on_Equity'].values

axes[0,2].plot(years, aapl_roe, 'o-', label='AAPL ROE', color=colors['AAPL'], linewidth=3, markersize=8)
axes[0,2].plot(years, msft_roe, 's-', label='MSFT ROE', color=colors['MSFT'], linewidth=3, markersize=8)
axes[0,2].set_title('Return on Equity Trends', fontsize=14, fontweight='bold')
axes[0,2].set_xlabel('Year')
axes[0,2].set_ylabel('ROE Ratio')
axes[0,2].legend()
axes[0,2].grid(True, alpha=0.3)

# Chart 4: Return on Assets Trends
aapl_roa = df[df['Company'] == 'AAPL']['Return_on_Assets'].values
msft_roa = df[df['Company'] == 'MSFT']['Return_on_Assets'].values

axes[1,0].plot(years, aapl_roa, 'o-', label='AAPL ROA', color=colors['AAPL'], linewidth=3, markersize=8)
axes[1,0].plot(years, msft_roa, 's-', label='MSFT ROA', color=colors['MSFT'], linewidth=3, markersize=8)
axes[1,0].set_title('Return on Assets Trends', fontsize=14, fontweight='bold')
axes[1,0].set_xlabel('Year')
axes[1,0].set_ylabel('ROA Ratio')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Chart 5: Comprehensive Performance Heatmap
heatmap_data = df.pivot_table(index='Company', columns='Year', values=['Gross_Margin', 'Operating_Margin', 'Net_Profit_Margin'])
heatmap_data.columns = [f'{col[1]} {col[0].replace("_", " ")}' for col in heatmap_data.columns]

sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn', 
           cbar_kws={'label': 'Ratio Value'}, ax=axes[1,1])
axes[1,1].set_title('Financial Metrics Heatmap', fontsize=14, fontweight='bold')
axes[1,1].set_xlabel('')
axes[1,1].set_ylabel('')

# Chart 6: Key Metrics Summary (2024)
summary_2024 = df[df['Year'] == '2024'][['Company', 'Gross_Margin', 'Operating_Margin', 'Return_on_Equity', 'Return_on_Assets']]
summary_melted = summary_2024.melt(id_vars=['Company'], var_name='Metric', value_name='Value')
summary_melted['Metric'] = summary_melted['Metric'].str.replace('_', ' ')

sns.barplot(data=summary_melted, x='Metric', y='Value', hue='Company', 
            palette=colors, ax=axes[1,2])
axes[1,2].set_title('2024 Key Performance Metrics', fontsize=14, fontweight='bold')
axes[1,2].set_ylabel('Ratio Value')
axes[1,2].set_xlabel('')
axes[1,2].tick_params(axis='x', rotation=45)
axes[1,2].legend(title='Company')

# Adjust layout and save
plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.savefig('comprehensive_financial_analysis.png', dpi=300, bbox_inches='tight')
print("Comprehensive financial analysis charts saved as: comprehensive_financial_analysis.png")

# Create a simplified version for the markdown
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
fig2.suptitle('AAPL vs MSFT: Key Financial Metrics Comparison', fontsize=16, fontweight='bold')

# Left chart: 2024 Margins
margin_2024 = ['Gross Margin', 'Operating Margin', 'Net Profit Margin']
aapl_2024_margins = [0.4621, 0.3151, 0.2397]
msft_2024_margins = [0.6976, 0.4464, 0.3596]

x = np.arange(len(margin_2024))
width = 0.35

axes2[0].bar(x - width/2, aapl_2024_margins, width, label='AAPL', color=colors['AAPL'], alpha=0.8)
axes2[0].bar(x + width/2, msft_2024_margins, width, label='MSFT', color=colors['MSFT'], alpha=0.8)

axes2[0].set_title('2024 Profitability Margins', fontweight='bold')
axes2[0].set_ylabel('Margin Ratio')
axes2[0].set_xticks(x)
axes2[0].set_xticklabels(margin_2024)
axes2[0].legend()
axes2[0].grid(True, alpha=0.3)

# Right chart: Margin trends
years_num = [2022, 2023, 2024]
aapl_gross = [0.4331, 0.4413, 0.4621]
msft_gross = [0.6840, 0.6892, 0.6976]
aapl_operating = [0.3029, 0.2982, 0.3151]
msft_operating = [0.4206, 0.4177, 0.4464]

axes2[1].plot(years_num, aapl_gross, 'o-', label='AAPL Gross', color=colors['AAPL'], linewidth=2, markersize=6)
axes2[1].plot(years_num, msft_gross, 's-', label='MSFT Gross', color=colors['MSFT'], linewidth=2, markersize=6)
axes2[1].plot(years_num, aapl_operating, 'o--', label='AAPL Operating', color=colors['AAPL'], linewidth=2, markersize=6, alpha=0.7)
axes2[1].plot(years_num, msft_operating, 's--', label='MSFT Operating', color=colors['MSFT'], linewidth=2, markersize=6, alpha=0.7)

axes2[1].set_title('Margin Trends (2022-2024)', fontweight='bold')
axes2[1].set_xlabel('Year')
axes2[1].set_ylabel('Margin Ratio')
axes2[1].legend()
axes2[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('financial_comparison_charts.png', dpi=300, bbox_inches='tight')
print("Financial comparison charts saved as: financial_comparison_charts.png")

print("All charts created successfully!")
