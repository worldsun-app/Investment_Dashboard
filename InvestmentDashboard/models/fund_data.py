import pandas as pd
import pygsheets
import os
import numpy as np
import yfinance as yf
from models.fund_config import FUND_CONFIG


SHEET_URL = "https://docs.google.com/spreadsheets/d/14uXT0z3TIry_vlEAMiEV1i-MYiaVSgiO5FZ5f8szDUM/edit?gid=0#gid=0"
SERVICE_KEY_FILE = "../service-account.json"

# Mapping strategy to worksheet name
PERFORMANCE_SHEET_MAP = {
    "All Weather": "all_weather_performance",
    "SMART 500": "SMART_500_performance",
}
HOLDINGS_SHEET_MAP = {
    "All Weather": "all_weather_holdings",
    "SMART 500": "SMART_500_holdings",
}

class FundData(object):
    """
    提供指定策略的基金數據存取，包括績效、持倉、資產與產業配置等。
    """

    def __init__(self, strategy="All Weather"):
        """
        從 Google Sheets 載入指定策略的基金數據。

        Args:
            strategy: 策略名稱（如 'All Weather', 'SMART 500'）
        """
        self.strategy = strategy

        # 連線並讀取 Google Sheets
        gc = pygsheets.authorize(service_file=SERVICE_KEY_FILE)
        sheet = gc.open_by_url(SHEET_URL)

        # 載入績效數據
        perf_ws = sheet.worksheet_by_title(PERFORMANCE_SHEET_MAP[strategy])
        perf_df = pd.DataFrame(perf_ws.get_all_records())
        perf_df["date"] = pd.to_datetime(perf_df["date"])
        perf_df = perf_df.sort_values("date")
        self.performance_df = perf_df

        # 載入持倉數據
        hold_ws = sheet.worksheet_by_title(HOLDINGS_SHEET_MAP[strategy])
        hold_df = pd.DataFrame(hold_ws.get_all_records())
        hold_df["date"] = pd.to_datetime(hold_df["date"])
        
        # 最新日資產與產業配置
        if not hold_df.empty:
            latest_date = hold_df["date"].max()
            latest_holdings = hold_df[hold_df["date"] == latest_date]
            self.holdings_df = latest_holdings
            if "symbol" in latest_holdings.columns:
                self.asset_allocation = latest_holdings.groupby("symbol")["weight"].sum().to_dict()
            else:
                self.asset_allocation = {}
            if "sector" in latest_holdings.columns:
                self.sector_allocation = latest_holdings.groupby("sector")["weight"].sum().to_dict()
            else:
                self.sector_allocation = {}
        else:
            self.asset_allocation = {}
            self.sector_allocation = {}

        # 基金介紹文本
        self._set_fund_intro_content()
        self._components_acc_ret = None  # 成分股累積報酬快取

    def _set_fund_intro_content(self):
        """
        設定基金介紹相關內容（理念、資訊、理念列表、風險管理）。
        """
        config = FUND_CONFIG.get(self.strategy, {})
        self.fund_description = config.get("description", "")
        self.fund_info_table = config.get("info_table", [])
        self.philosophy_list = config.get("philosophy_list", [])
        self.risk_framework_list = config.get("risk_framework_list", [])

    def get_fund_intro_content(self):
        """
        取得基金介紹：理念描述、資訊表、理念列表。

        Returns:
            tuple: (描述, 資訊表, 理念列表)
        """
        return self.fund_description, self.fund_info_table, self.philosophy_list

    def get_performance_data(self):
        """
        取得基金與指標累積報酬資料。

        Returns:
            DataFrame: ['date', 'fund_value', 'benchmark_value']
        """
        df = self.performance_df[["date", "cum_return", "benchmark_cum_return"]].copy()
        df = df.rename(columns={"cum_return": "fund_value", "benchmark_cum_return": "benchmark_value"})
        return df

    def get_asset_allocation(self):
        """
        取得最新日的資產配置。

        Returns:
            dict: {資產類型: 權重}
        """
        return self.asset_allocation

    def get_sector_allocation(self):
        """
        取得最新日的產業配置。

        Returns:
            dict: {產業類型: 權重}
        """
        return self.sector_allocation

    def get_performance_metrics(self):
        """
        計算並回傳績效指標，包括年化報酬、波動度、Sharpe、最大回檔等。

        Returns:
            dict: 各項績效指標
        """
        df = self.performance_df
        metrics = {
            "annualized_return": "N/A",
            "volatility": "N/A",
            "sharpe_ratio": "N/A",
            "max_drawdown": "N/A",
            "alpha": "N/A",
            "beta": "N/A",
            "total_return": "N/A",
            "best_month": "N/A",
            "worst_month": "N/A",
            "pos_month_pct": "N/A",
            "corr": "N/A",
        }
        if not df.empty and "cum_return" in df.columns:
            df = df.sort_values("date")
            df[["month_return", "benchmark_month_return"]] = df[["cum_return", "benchmark_cum_return"]].pct_change()
            
            # 年化報酬率
            ret = df["month_return"].mean() * 12
            metrics["annualized_return"] = "{:.1f}%".format(ret * 100)
            
            # 波動度
            vol = df["month_return"].std() * (12 ** 0.5)
            metrics["volatility"] = "{:.1f}%".format(vol * 100)

            # Sharpe ratio（假設無風險利率為 0）
            sharpe = ret / vol if vol > 0 else 0
            metrics["sharpe_ratio"] = "{:.2f}".format(sharpe)

            # 最大回檔
            curve = (1 + df["month_return"]).cumprod()
            peak = curve.cummax()
            dd = (curve - peak) / peak
            max_dd = dd.min()
            metrics["max_drawdown"] = "{:.1f}%".format(max_dd * 100)
            
            # Alpha/Beta
            # 去除 NA
            valid = df[["month_return", "benchmark_month_return"]].dropna()
            if not valid.empty and valid["benchmark_month_return"].std() > 0:
                x = valid["benchmark_month_return"].values
                y = valid["month_return"].values
                # 一元線性回歸：y = alpha + beta * x
                beta = np.cov(x, y)[0, 1] / np.var(x)
                alpha = y.mean() - beta * x.mean() 
                metrics["beta"] = "{:.2f}".format(beta)
                metrics["alpha"] = "{:.2f}%".format(alpha * 100)         
                
            # 累積總報酬
            total_return = df["cum_return"].iloc[-1] - 1
            metrics["total_return"] = "{:.0f}%".format(total_return * 100)
            
            # 最佳單月
            best_month = df["month_return"].max()
            metrics["best_month"] = "{:.1f}%".format(best_month * 100)
            
            # 最差單月
            worst_month = df["month_return"].min()
            metrics["worst_month"] = "{:.1f}%".format(worst_month * 100)
            
            # 正報酬月數比
            pos_month_pct = sum(df["month_return"] > 0) / len(df)
            metrics["pos_month_pct"] = "{:.0f}%".format(pos_month_pct * 100)
            
            # 相關性
            corr = valid.corr().iloc[0,1]
            metrics["corr"] = "{:.2f}".format(corr)
        return metrics

    def get_components_acc_ret(self):
        """
        取得成分股自買入後至今的累積報酬。

        Returns:
            String: 計算日期
            Series: 各成分股的累積報酬（排序由高至低）
        """
        comps = list(self.asset_allocation.keys())
        if not comps:
            return "", pd.Series(dtype=float)
        start_date = self.holdings_df.date.iloc[0]
        date = (start_date + pd.DateOffset(months=1)).strftime("%Y年%m月")
        if self._components_acc_ret is not None:
            return date, self._components_acc_ret
        try:
            df = yf.download(comps, start=start_date, auto_adjust=True)["Close"]
            acc_ret = df.iloc[-1, :] / df.iloc[0, :] - 1
            acc_ret.fillna(0, inplace=True)
            acc_ret.sort_values(ascending=False, inplace=True)
            self._components_acc_ret = acc_ret
            return date, acc_ret
        except Exception as e:
            # 異常處理：取得資料失敗時回傳空值並加註警告
            print(f"[警告] 成分股累積報酬抓取失敗: {str(e)}")
            return date, pd.Series(dtype=float)
        
    def get_port_mtd_ret(self):
        _, acc_ret = self.get_components_acc_ret()
        weights_dict = self.get_asset_allocation()
        weights = pd.Series(weights_dict)
        weights = weights[acc_ret.index]        
        port_mtd_ret = np.dot(weights, acc_ret)
        return port_mtd_ret

    def get_port_ytd_ret(self, port_mtd_ret):
        today = pd.Timestamp.today()
        last_year_end = pd.Timestamp(year=today.year-1, month=12, day=31)
        df_this_year = self.performance_df[self.performance_df['date'] >= last_year_end]
        ret = df_this_year['cum_return'].iloc[-1] / df_this_year['cum_return'].iloc[0] - 1
        port_ytd_ret = (1 + ret) * (1 + port_mtd_ret) - 1
        return port_ytd_ret

