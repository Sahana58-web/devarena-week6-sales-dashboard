"""
Interactive Sales Dashboard (Week 6)
Makes Seaborn charts, interactive Plotly charts and a demo GIF from sales_data.csv.

Run with:  python dashboard.py
Output:    the visualizations/ folder and dashboard_demo.gif
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')                      # draw charts without opening a window
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image, ImageDraw, ImageFont

DATA_FILE = 'sales_data.csv'
OUT_FOLDER = 'visualizations'
REQUIRED_COLUMNS = ['Date', 'Product', 'Quantity', 'Price', 'Customer_ID', 'Region', 'Total_Sales']

# One colour scheme for the whole dashboard
NAVY = '#1f3a5f'
PRODUCT_COLORS = {'Laptop': '#1f3a5f', 'Tablet': '#2a9d8f', 'Phone': '#e9c46a',
                  'Headphones': '#f4a261', 'Monitor': '#e76f51'}
REGION_COLORS = {'North': '#1f3a5f', 'South': '#2a9d8f', 'East': '#e9c46a', 'West': '#e76f51'}
PRODUCTS = list(PRODUCT_COLORS.keys())
REGIONS = list(REGION_COLORS.keys())
MONTH_ORDER = ['Jan', 'Feb', 'Mar', 'Apr']


# ---------------------------------------------------------------- data
def load_data(path):
    """Load and clean the CSV file. Return None and print a message if something is wrong."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: file '{path}' was not found.")
        return None
    except Exception as error:
        print("Error while reading the file:", error)
        return None
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print("Error: these columns are missing:", missing)
        return None
    df = df.dropna().drop_duplicates()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Month'] = df['Date'].dt.month
    df['MonthName'] = df['Date'].dt.strftime('%b')
    if df.empty:
        print("Error: no valid rows left after cleaning.")
        return None
    return df


# ------------------------------------------------------ seaborn charts
def seaborn_charts(df):
    """Charts 1 to 4: box plot, violin plot, correlation heatmap and a 2x2 dashboard grid."""
    sns.set_theme(style='whitegrid', font_scale=1.05)

    order = df.groupby('Product')['Total_Sales'].median().sort_values(ascending=False).index
    plt.figure(figsize=(9, 5))
    sns.boxplot(data=df, x='Product', y='Total_Sales', hue='Product',
                order=order, palette=PRODUCT_COLORS, legend=False)
    plt.title('Order Value Distribution by Product', fontsize=14, fontweight='bold')
    plt.ylabel('Order value (Rs.)')
    plt.savefig(f'{OUT_FOLDER}/1_boxplot_product.png', dpi=150, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 5))
    sns.violinplot(data=df, x='Region', y='Total_Sales', hue='Region',
                   palette=REGION_COLORS, inner='quartile', legend=False, cut=0)
    plt.title('Order Value Distribution by Region', fontsize=14, fontweight='bold')
    plt.ylabel('Order value (Rs.)')
    plt.savefig(f'{OUT_FOLDER}/2_violin_region.png', dpi=150, bbox_inches='tight')
    plt.close()

    corr = df[['Quantity', 'Price', 'Total_Sales', 'Month']].corr()
    plt.figure(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='YlGnBu', vmin=-1, vmax=1,
                linewidths=1, linecolor='white')
    plt.title('Correlation Between Numbers', fontsize=14, fontweight='bold')
    plt.savefig(f'{OUT_FOLDER}/3_correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Sales Dashboard Overview', fontsize=20, fontweight='bold', color=NAVY)

    by_product = df.groupby('Product')['Total_Sales'].sum().sort_values(ascending=False).reset_index()
    by_product['Sales_M'] = by_product['Total_Sales'] / 1_000_000
    sns.barplot(data=by_product, x='Product', y='Sales_M', hue='Product',
                palette=PRODUCT_COLORS, legend=False, ax=axes[0, 0])
    axes[0, 0].set_title('Total Sales by Product', fontweight='bold')
    axes[0, 0].set_ylabel('Sales (Rs. millions)')
    for bar in axes[0, 0].patches:
        axes[0, 0].annotate(f"{bar.get_height():.2f}",
                            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            ha='center', va='bottom')

    monthly = df.groupby(['Month', 'MonthName'])['Total_Sales'].sum().reset_index()
    monthly['Sales_M'] = monthly['Total_Sales'] / 1_000_000
    sns.lineplot(data=monthly, x='Month', y='Sales_M', marker='o', markersize=9,
                 linewidth=3, color='#2a9d8f', ax=axes[0, 1])
    axes[0, 1].set_xticks(monthly['Month'])
    axes[0, 1].set_xticklabels(monthly['MonthName'])
    axes[0, 1].set_title('Monthly Sales Trend (April has 9 days)', fontweight='bold')
    axes[0, 1].set_xlabel('Month (2024)')
    axes[0, 1].set_ylabel('Sales (Rs. millions)')
    axes[0, 1].set_ylim(0, monthly['Sales_M'].max() * 1.2)

    sns.scatterplot(data=df, x='Price', y='Quantity', hue='Product', palette=PRODUCT_COLORS,
                    s=90, alpha=0.85, ax=axes[1, 0])
    axes[1, 0].set_title('Price vs Quantity (colour = product)', fontweight='bold')
    axes[1, 0].set_xlabel('Price (Rs.)')
    axes[1, 0].set_ylim(0, 11)
    axes[1, 0].legend(ncol=5, fontsize=8, loc='upper center', frameon=False)

    sns.histplot(df['Total_Sales'], bins=15, kde=True, color='#e76f51', ax=axes[1, 1])
    axes[1, 1].set_title('Distribution of Order Values', fontweight='bold')
    axes[1, 1].set_xlabel('Order value (Rs.)')
    axes[1, 1].set_ylabel('Number of orders')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f'{OUT_FOLDER}/4_dashboard_grid.png', dpi=150, bbox_inches='tight')
    plt.close()


# ------------------------------------------------------ plotly charts
def plotly_charts(df):
    """Charts 5 to 8: interactive charts saved as HTML files (open them in a browser)."""
    prod = df.groupby('Product').agg(Total_Sales=('Total_Sales', 'sum'),
                                     Units_Sold=('Quantity', 'sum'),
                                     Average_Order=('Total_Sales', 'mean'),
                                     Orders=('Total_Sales', 'count'))
    prod = prod.sort_values('Total_Sales', ascending=False).reset_index()

    # 5) Bar chart with hover details and a dropdown to change the measure
    metrics = {'Total Sales (Rs.)': 'Total_Sales', 'Units Sold': 'Units_Sold',
               'Average Order (Rs.)': 'Average_Order', 'Number of Orders': 'Orders'}
    fig1 = go.Figure(go.Bar(
        x=prod['Product'], y=prod['Total_Sales'],
        marker_color=[PRODUCT_COLORS[p] for p in prod['Product']],
        customdata=prod[['Units_Sold', 'Orders']],
        hovertemplate='<b>%{x}</b><br>Value: %{y:,.0f}<br>Units sold: %{customdata[0]}'
                      '<br>Orders: %{customdata[1]}<extra></extra>'))
    fig1.update_layout(
        title='Product Performance (use the dropdown to change the measure)',
        template='plotly_white', height=500, yaxis_title='Total Sales (Rs.)',
        updatemenus=[dict(type='dropdown', x=0.0, y=1.18, xanchor='left',
                          buttons=[dict(label=label, method='update',
                                        args=[{'y': [prod[col]]}, {'yaxis.title.text': label}])
                                   for label, col in metrics.items()])])
    fig1.write_html(f'{OUT_FOLDER}/5_interactive_bar_dropdown.html', include_plotlyjs='cdn')

    # 6) Line chart with a region dropdown
    reg_month = df.groupby(['Month', 'MonthName', 'Region'])['Total_Sales'].sum().reset_index()
    all_month = df.groupby(['Month', 'MonthName'])['Total_Sales'].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=all_month['MonthName'], y=all_month['Total_Sales'],
                              name='All regions', mode='lines+markers',
                              line=dict(color=NAVY, width=4),
                              hovertemplate='%{x}: Rs.%{y:,.0f}<extra>All regions</extra>'))
    for r in REGIONS:
        d = reg_month[reg_month['Region'] == r]
        fig2.add_trace(go.Scatter(x=d['MonthName'], y=d['Total_Sales'], name=r,
                                  mode='lines+markers', visible=False,
                                  line=dict(color=REGION_COLORS[r], width=4),
                                  hovertemplate='%{x}: Rs.%{y:,.0f}<extra>' + r + '</extra>'))
    names = ['All regions'] + REGIONS
    buttons = [dict(label=n, method='update',
                    args=[{'visible': [n == m for m in names]}, {'title': f'Monthly Sales: {n}'}])
               for n in names]
    fig2.update_layout(title='Monthly Sales: All regions (use the dropdown to pick a region)',
                       template='plotly_white', height=500, yaxis_title='Sales (Rs.)',
                       xaxis=dict(categoryorder='array', categoryarray=MONTH_ORDER),
                       updatemenus=[dict(type='dropdown', x=0.0, y=1.18, xanchor='left',
                                         buttons=buttons)])
    fig2.write_html(f'{OUT_FOLDER}/6_interactive_line_dropdown.html', include_plotlyjs='cdn')

    # 7) Animated bar chart: press Play to see each month
    wide = df.pivot_table(index=['Month', 'MonthName'], columns='Product', values='Total_Sales',
                          aggfunc='sum', fill_value=0).reset_index()
    anim = wide.melt(id_vars=['Month', 'MonthName'], var_name='Product',
                     value_name='Sales').sort_values('Month')
    fig3 = px.bar(anim, x='Product', y='Sales', color='Product', animation_frame='MonthName',
                  color_discrete_map=PRODUCT_COLORS, range_y=[0, anim['Sales'].max() * 1.15],
                  category_orders={'MonthName': MONTH_ORDER, 'Product': PRODUCTS},
                  title='Sales by Product, Month by Month (press Play)')
    fig3.update_layout(template='plotly_white', height=520, yaxis_title='Sales (Rs.)',
                       showlegend=False)
    fig3.write_html(f'{OUT_FOLDER}/7_animated_sales_by_month.html', include_plotlyjs='cdn')

    # 8) The full interactive dashboard (4 panels)
    dash = make_subplots(rows=2, cols=2, specs=[[{}, {}], [{'type': 'domain'}, {}]],
                         subplot_titles=('Total Sales by Product', 'Monthly Sales Trend',
                                         'Share of Sales by Region',
                                         'Price vs Quantity (hover for customer)'))
    dash.add_trace(go.Bar(x=prod['Product'], y=prod['Total_Sales'], showlegend=False,
                          marker_color=[PRODUCT_COLORS[p] for p in prod['Product']],
                          hovertemplate='<b>%{x}</b><br>Rs.%{y:,.0f}<extra></extra>'),
                   row=1, col=1)
    dash.add_trace(go.Scatter(x=all_month['MonthName'], y=all_month['Total_Sales'],
                              showlegend=False, mode='lines+markers',
                              line=dict(color='#2a9d8f', width=4),
                              hovertemplate='%{x}: Rs.%{y:,.0f}<extra></extra>'), row=1, col=2)
    by_region = df.groupby('Region')['Total_Sales'].sum().reindex(REGIONS)
    dash.add_trace(go.Pie(labels=by_region.index, values=by_region.values, hole=0.45,
                          marker=dict(colors=[REGION_COLORS[r] for r in by_region.index]),
                          hovertemplate='<b>%{label}</b><br>Rs.%{value:,.0f} (%{percent})<extra></extra>'),
                   row=2, col=1)
    for p in PRODUCTS:
        d = df[df['Product'] == p]
        dash.add_trace(go.Scatter(
            x=d['Price'], y=d['Quantity'], mode='markers', name=p,
            marker=dict(color=PRODUCT_COLORS[p], size=10, opacity=0.85),
            customdata=d[['Customer_ID', 'Total_Sales']],
            hovertemplate='<b>%{customdata[0]}</b><br>Price: Rs.%{x:,.0f}<br>Quantity: %{y}'
                          '<br>Order: Rs.%{customdata[1]:,.0f}<extra>' + p + '</extra>'),
            row=2, col=2)
    dash.update_xaxes(categoryorder='array', categoryarray=MONTH_ORDER, row=1, col=2)
    dash.update_xaxes(title_text='Price (Rs.)', row=2, col=2)
    dash.update_yaxes(title_text='Sales (Rs.)', row=1, col=1)
    dash.update_yaxes(title_text='Sales (Rs.)', row=1, col=2)
    dash.update_yaxes(title_text='Quantity', row=2, col=2)
    dash.update_layout(title=dict(text='Interactive Sales Dashboard', font=dict(size=24, color=NAVY)),
                       template='plotly_white', height=800, legend=dict(title='Product'))
    dash.write_html(f'{OUT_FOLDER}/8_interactive_dashboard.html', include_plotlyjs='cdn')


# ---------------------------------------------------------- demo gif
def make_demo_gif(df, path='dashboard_demo.gif'):
    """Make a short animated GIF that walks through the dashboard.
    It shows the Seaborn charts one by one and then plays the month-by-month animation."""
    size = (1000, 640)
    try:
        font_big = ImageFont.truetype('DejaVuSans-Bold.ttf', 34)
        font_small = ImageFont.truetype('DejaVuSans.ttf', 22)
    except OSError:
        font_big = font_small = ImageFont.load_default()

    def with_caption(img, text):
        canvas = Image.new('RGB', size, 'white')
        img = img.convert('RGB')
        img.thumbnail((size[0] - 40, size[1] - 90))
        canvas.paste(img, ((size[0] - img.width) // 2, 70))
        ImageDraw.Draw(canvas).text((20, 18), text, fill=NAVY, font=font_small)
        return canvas

    frames, durations = [], []

    title = Image.new('RGB', size, NAVY)
    d = ImageDraw.Draw(title)
    d.text((60, 220), 'Interactive Sales Dashboard', fill='white', font=font_big)
    d.text((60, 280), 'Seaborn + Plotly demo', fill='#e9c46a', font=font_small)
    frames.append(title); durations.append(1800)

    steps = [('1_boxplot_product.png', 'Box plot: order values by product'),
             ('2_violin_region.png', 'Violin plot: order values by region'),
             ('3_correlation_heatmap.png', 'Heatmap: correlation between numbers'),
             ('4_dashboard_grid.png', '2x2 dashboard grid: bar, line, scatter, histogram')]
    for file, text in steps:
        frames.append(with_caption(Image.open(f'{OUT_FOLDER}/{file}'), text))
        durations.append(2200)

    # Animated part: sales by product, month by month (the same idea as the Plotly animation)
    wide = df.pivot_table(index='MonthName', columns='Product', values='Total_Sales',
                          aggfunc='sum', fill_value=0).reindex(MONTH_ORDER)[PRODUCTS]
    ymax = wide.values.max() / 1_000_000 * 1.15
    for month in MONTH_ORDER:
        fig, ax = plt.subplots(figsize=(8, 5))
        vals = wide.loc[month] / 1_000_000
        ax.bar(PRODUCTS, vals, color=[PRODUCT_COLORS[p] for p in PRODUCTS])
        ax.set_ylim(0, ymax)
        ax.set_ylabel('Sales (Rs. millions)')
        ax.set_title(f'Sales by Product: {month} 2024', fontweight='bold')
        for i, v in enumerate(vals):
            ax.text(i, v + ymax * 0.01, f'{v:.2f}', ha='center')
        fig.savefig('_frame.png', dpi=110, bbox_inches='tight')
        plt.close(fig)
        frames.append(with_caption(Image.open('_frame.png'), 'Animation: sales month by month'))
        durations.append(1100)
    os.remove('_frame.png')

    end = Image.new('RGB', size, NAVY)
    d = ImageDraw.Draw(end)
    d.text((60, 220), 'Open the HTML files in a browser', fill='white', font=font_big)
    d.text((60, 280), 'to hover, use the dropdowns and press Play', fill='#e9c46a', font=font_small)
    frames.append(end); durations.append(2200)

    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=True)
    print(f"Demo GIF saved as {path}")


# ---------------------------------------------------------------- main
def main():
    df = load_data(DATA_FILE)
    if df is None:
        return
    os.makedirs(OUT_FOLDER, exist_ok=True)
    print(f"Rows loaded: {len(df)}")
    seaborn_charts(df)
    print("Seaborn charts saved (1 to 4).")
    plotly_charts(df)
    print("Interactive Plotly charts saved (5 to 8). Open the .html files in a browser.")
    make_demo_gif(df)
    print("Done. Everything is in the 'visualizations' folder and dashboard_demo.gif.")


if __name__ == '__main__':
    main()
