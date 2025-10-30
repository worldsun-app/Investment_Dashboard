"""
Charts module for fund dashboard.
整合績效分析、基金介紹頁面所有圖表產生函式。
僅專注於資料視覺化（Plotly 圖形）；不做任何資料運算。
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def make_performance_figure(performance_df, start_date, end_date):
    """
    根據指定日期區間產生績效比較圖，並自動 rebase。

    Args:
        performance_df: 基金績效 DataFrame
        start_date: 區間起始日
        end_date: 區間結束日

    Returns:
        Plotly Figure
    """


    df = performance_df[(performance_df['date'] >= start_date) & (performance_df['date'] <= end_date)].copy()
    if df.empty:
        df = performance_df.copy()
    df = df.reset_index(drop=True)

    base_fund = df["fund_value"].iloc[0]
    base_bench = df["benchmark_value"].iloc[0]
    df["fund_value_rebase"] = df["fund_value"] / base_fund - 1
    df["benchmark_value_rebase"] = df["benchmark_value"] / base_bench - 1

    primary = "#00585C"    # 品牌主色
    neutral = "#6b7280"    # 中性灰

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"].values,
        y=df["fund_value_rebase"] * 100,
        mode='lines',
        name='基金累積報酬',
        line=dict(color=primary, width=3),
        hovertemplate='<b>基金</b><br>累積報酬: %{y:.2f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df["date"].values,
        y=df["benchmark_value_rebase"] * 100,
        mode='lines',
        name='S&P 500',
        line=dict(color=neutral, width=2, dash='dot'),
        hovertemplate='<b>S&P 500</b><br>累積報酬: %{y:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        hovermode='x unified',
        yaxis=dict(
            title='區間累積報酬 (%)',
            gridcolor='#e5e7eb',
            linecolor='#d1d5db',
            title_font=dict(color='#374151')
        ),
        legend=dict(orientation="h", yanchor="top", y=1.15, xanchor="center", x=0.5, font=dict(size=16)),
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, Roboto, sans-serif", color='#374151'),
        margin=dict(l=40, r=40, t=40, b=40),
        height=420
    )
    return fig


def make_heatmap_figure(monthly_df):
    """
    產生月報酬熱力圖。

    Args:
        monthly_df: 含月報酬欄位的 DataFrame

    Returns:
        Plotly Figure
    """


    if not monthly_df.empty and "cum_return" in monthly_df.columns:
        monthly_df = monthly_df.sort_values("date")
        monthly_df["year"] = monthly_df["date"].dt.year
        monthly_df["month"] = monthly_df["date"].dt.month
        monthly_df["month_return"] = monthly_df["cum_return"].pct_change()
        monthly_df["month_return"] = np.round(monthly_df["month_return"], 3)
        monthly_df = monthly_df[monthly_df["date"] >= pd.Timestamp("2021-01-01")]
        heatmap_pivot = monthly_df.pivot(index="year", columns="month", values="month_return") * 100
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        heatmap_pivot.columns = [month_names[m - 1] for m in heatmap_pivot.columns]
    else:
        heatmap_pivot = pd.DataFrame()

    # 品牌化色階：負回報（副色磚紅）→ 中性 → 正回報（偏青綠）
    color_scale = ['#B73932', '#f8fafc', '#0FAF97']

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="月份", y="年度", color="月報酬 (%)"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale=color_scale,
        color_continuous_midpoint=0,
        aspect="auto",
        title="月度報酬率 (%)",
        text_auto=True,
    )

    fig.update_layout(
        title=dict(
            font=dict(size=16, color='#1f2937', family="Segoe UI, Roboto, sans-serif"),
            x=0.5
        ),
        font=dict(family="Segoe UI, Roboto, sans-serif", color='#374151'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40),
        height=250,
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None
    )
    return fig


def make_asset_pie_figure(asset_allocation):
    """
    產生資產配置圓餅圖。

    Args:
        asset_allocation: dict，{資產類型: 權重}

    Returns:
        Plotly Figure
    """

    # 品牌化色盤（含主色、變體與副色系）
    professional_colors = [
        '#00585C', '#0B6F73', '#2B8A8E', '#4CA5A8',
        '#7FBFC1', '#B73932', '#D0655F', '#E59A95'
    ]
    fig = px.pie(
        names=list(asset_allocation.keys()),
        values=list(asset_allocation.values()),
        title="資產配置",
        color_discrete_sequence=professional_colors,
        hole=0.4
    )
    fig.update_traces(
        hovertemplate='%{label} (%{percent})<extra></extra>',
        textposition='inside',
        textinfo='label'
    )
    fig.update_layout(
        font=dict(size=13, family="Segoe UI, Roboto, sans-serif"),
        title_font=dict(size=16, color='#1f2937'),
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280
    )
    return fig


def make_sector_pie_figure(sector_allocation):
    """
    產生產業配置圓餅圖。

    Args:
        sector_allocation: dict，{產業類型: 權重}

    Returns:
        Plotly Figure
    """

    # 與資產配置一致的品牌色盤
    professional_colors = [
        '#00585C', '#0B6F73', '#2B8A8E', '#4CA5A8',
        '#7FBFC1', '#B73932', '#D0655F', '#E59A95'
    ]
    fig = px.pie(
        names=list(sector_allocation.keys()),
        values=list(sector_allocation.values()),
        title="產業配置",
        color_discrete_sequence=professional_colors,
        hole=0.4
    )
    fig.update_traces(
        hovertemplate='%{label} (%{percent})<extra></extra>',
        textposition='inside',
        textinfo='label'
    )
    fig.update_layout(
        font=dict(size=13, family="Segoe UI, Roboto, sans-serif"),
        title_font=dict(size=16, color='#1f2937'),
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280
    )
    return fig

def make_components_bar_figure(date, acc_ret):
    """
    產生成分股累積報酬 bar chart。

    Args:
        date: 字串，計算起始日
        acc_ret: Series，各成分股的累積報酬

    Returns:
        Plotly Figure
    """

    pos_color = '#0FAF97'   # 正報酬：青綠，呼應主色系
    neg_color = '#B73932'   # 負報酬：副色系磚紅
    colors = [pos_color if v > 0 else neg_color for v in acc_ret.values]

    bar_fig = px.bar(
        x=acc_ret.index.tolist(),
        y=(acc_ret.values * 100).tolist(),
        labels={'x': '成分股', 'y': '累積報酬 (%)'},
        title=f"成分股自{date}以來累積報酬",
        color_discrete_sequence=colors
    )
    bar_fig.update_traces(
        marker_color=colors,
        textposition='outside',
        hovertemplate='%{y:.1f}%<extra></extra>'
    )
    bar_fig.update_layout(
        font=dict(size=13, family="Segoe UI, Roboto, sans-serif"),
        title_font=dict(size=16, color='#1f2937'),
        xaxis_tickangle=-30,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        margin=dict(l=30, r=30, t=40, b=40),
        height=360
    )
    return bar_fig