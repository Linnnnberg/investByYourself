#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a stock analysis Markdown report (ASML by default) that maps to a reusable stock-picking framework.

Sections:
1) Business Segments (manual or from file)
2) Profitability & Growth
3) Industry Position & Competitiveness (peer snapshot)
4) Macro/Cycle Sensitivity (rates, indices)
5) Composite Scoring (weights adjustable, can be tied to a risk score later)

Usage:
  python asml_stock_framework_report.py --ticker ASML --output asml_report.md

Optional:
  --segments_json path/to/segments.json   # to provide custom segment breakdown
  --peers ASML,AMAT,8035.T,KLAC           # peer tickers (default provided)
  --period 5y                             # price history window for sensitivity
  --risk 60                               # risk score (1-100) to auto-adjust weights

Author: InvestByYourself
"""

import argparse
import json
import math
import sys
from datetime import datetime

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception as e:
    print("Please install yfinance: pip install yfinance", file=sys.stderr)
    raise

# -----------------------------
# Helpers
# -----------------------------


def pct(x):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return f"{x:.2%}"


def safe_div(a, b):
    try:
        if b == 0 or b is None or a is None:
            return np.nan
        return a / b
    except Exception:
        return np.nan


def yfi_get_ratio(tkr, numer_label, denom_label, df="financials"):
    """Generic helper to fetch ratio from yfinance statements."""
    try:
        obj = getattr(tkr, df)  # financials, balance_sheet, cashflow
        if (
            isinstance(obj, pd.DataFrame)
            and (numer_label in obj.index)
            and (denom_label in obj.index)
        ):
            numer = obj.loc[numer_label]
            denom = obj.loc[denom_label]
            s = (numer / denom).dropna()
            if not s.empty:
                # Latest period first in yfinance; take the first non-na entry
                return float(s.iloc[0])
    except Exception:
        pass
    return np.nan


def latest_value(series_or_dict, key):
    try:
        return float(series_or_dict.get(key, np.nan))
    except Exception:
        return np.nan


def compute_eps_growth(tkr):
    """Compute CAGR of earnings (yfinance .earnings) over available years."""
    try:
        earn = tkr.earnings  # columns: Revenue, Earnings, index: Year
        if (
            isinstance(earn, pd.DataFrame)
            and "Earnings" in earn.columns
            and len(earn) >= 2
        ):
            first = float(earn["Earnings"].iloc[0])
            last = float(earn["Earnings"].iloc[-1])
            years = len(earn) - 1
            if first > 0 and last > 0 and years > 0:
                cagr = (last / first) ** (1 / years) - 1
                return float(cagr)
    except Exception:
        pass
    return np.nan


def compute_revenue_cagr(tkr):
    try:
        earn = tkr.earnings  # revenue in same df
        if (
            isinstance(earn, pd.DataFrame)
            and "Revenue" in earn.columns
            and len(earn) >= 2
        ):
            first = float(earn["Revenue"].iloc[0])
            last = float(earn["Revenue"].iloc[-1])
            years = len(earn) - 1
            if first > 0 and last > 0 and years > 0:
                cagr = (last / first) ** (1 / years) - 1
                return float(cagr)
    except Exception:
        pass
    return np.nan


def compute_margins(tkr):
    # Gross and Operating margins from income statement
    gm = yfi_get_ratio(tkr, "Gross Profit", "Total Revenue", "financials")
    opm = yfi_get_ratio(tkr, "Operating Income", "Total Revenue", "financials")
    return gm, opm


def compute_roic(tkr):
    # ROIC ≈ NOPAT / Invested Capital; approximate via (Operating Income * (1 - tax)) / (Total Equity + Total Debt - Cash)
    try:
        fin = tkr.financials
        bs = tkr.balance_sheet
        cf = tkr.cashflow

        if isinstance(fin, pd.DataFrame) and isinstance(bs, pd.DataFrame):
            op_inc = (
                fin.loc["Operating Income"].dropna().iloc[0]
                if "Operating Income" in fin.index
                else np.nan
            )
            tax_exp = (
                fin.loc["Income Tax Expense"].dropna().iloc[0]
                if "Income Tax Expense" in fin.index
                else np.nan
            )
            pre_tax_inc = (
                fin.loc["Pretax Income"].dropna().iloc[0]
                if "Pretax Income" in fin.index
                else np.nan
            )

            eff_tax = 0.21
            if not (pd.isna(tax_exp) or pd.isna(pre_tax_inc)) and pre_tax_inc != 0:
                eff_tax = max(0.0, min(0.5, float(tax_exp) / float(pre_tax_inc)))

            nopat = op_inc * (1 - eff_tax) if not pd.isna(op_inc) else np.nan

            total_equity = (
                bs.loc["Total Stockholder Equity"].dropna().iloc[0]
                if "Total Stockholder Equity" in bs.index
                else np.nan
            )
            total_debt = 0.0
            for lab in [
                "Short Long Term Debt",
                "Short/Long Term Debt",
                "Short Term Debt",
                "Long Term Debt",
            ]:
                if lab in bs.index:
                    v = bs.loc[lab].dropna()
                    if not v.empty:
                        total_debt += float(v.iloc[0])
            cash = (
                bs.loc["Cash"].dropna().iloc[0]
                if "Cash" in bs.index
                else (
                    bs.loc["Cash And Cash Equivalents"].dropna().iloc[0]
                    if "Cash And Cash Equivalents" in bs.index
                    else 0.0
                )
            )

            invested_cap = (
                (total_equity if not pd.isna(total_equity) else 0.0)
                + total_debt
                - (cash if not pd.isna(cash) else 0.0)
            )
            if invested_cap and invested_cap > 0 and not pd.isna(nopat):
                return float(nopat / invested_cap)
    except Exception:
        pass
    return np.nan


def get_price_history(ticker, period="5y"):
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df["Close"].rename(ticker)
    except Exception:
        pass
    return pd.Series(dtype=float, name=ticker)


def rolling_corr(s1, s2, window=63):
    try:
        return s1.pct_change().rolling(window).corr(s2.pct_change()).dropna()
    except Exception:
        return pd.Series(dtype=float)


def annualized_vol(s):
    # 252 trading days
    try:
        return float(s.pct_change().std() * np.sqrt(252))
    except Exception:
        return np.nan


# -----------------------------
# Scoring Utilities
# -----------------------------


def risk_adjusted_weights(risk_score):
    """
    Map risk score (1-100) to weights for the 5 pillars.
    Conservative (low risk_score): emphasize quality/stability.
    Aggressive (high risk_score): emphasize growth/momentum.
    """
    risk = max(1, min(100, risk_score))
    # base weights
    w = {
        "BusinessStability": 0.18,
        "Profitability": 0.24,
        "Growth": 0.20,
        "Moat_Position": 0.23,
        "Macro_Sensitivity": 0.15,
    }
    # tilt: +growth, -macro_sensitivity penalty, +profitability for low risk
    growth_tilt = (risk - 50) / 100.0  # -0.49 .. +0.5
    w["Growth"] += 0.08 * growth_tilt
    w["Profitability"] += -0.04 * growth_tilt
    w["Macro_Sensitivity"] += -0.04 * growth_tilt
    # normalize
    tot = sum(w.values())
    for k in w:
        w[k] = max(0.05, w[k] / tot)  # floor 5%
    # renormalize after floor
    tot = sum(w.values())
    for k in w:
        w[k] /= tot
    return w


def zscore(x, mean, std):
    if pd.isna(x) or pd.isna(mean) or pd.isna(std) or std == 0:
        return 0.0
    return float((x - mean) / std)


def bounded_score(x, lo, hi, higher_better=True):
    if pd.isna(x):
        return 0.5
    x = float(x)
    if higher_better:
        return float(np.clip((x - lo) / (hi - lo), 0, 1))
    else:
        return float(np.clip((hi - x) / (hi - lo), 0, 1))


# -----------------------------
# Main
# -----------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="ASML")
    ap.add_argument("--output", default="asml_report.md")
    ap.add_argument(
        "--segments_json",
        default=None,
        help="Optional JSON file with segment breakdown",
    )
    ap.add_argument(
        "--peers", default="ASML,AMAT,8035.T,KLAC", help="Comma-separated peer tickers"
    )
    ap.add_argument(
        "--period",
        default="5y",
        help="History period for sensitivity (e.g., 3y, 5y, 10y)",
    )
    ap.add_argument(
        "--risk", type=int, default=60, help="Risk score (1-100) for weight tilting"
    )
    args = ap.parse_args()

    tkr = yf.Ticker(args.ticker)
    info = tkr.info if hasattr(tkr, "info") else {}

    # 1) Business Segments
    segments = None
    if args.segments_json:
        try:
            with open(args.segments_json, "r", encoding="utf-8") as f:
                segments = pd.DataFrame(json.load(f))
        except Exception as e:
            print(f"Failed to load segments_json: {e}", file=sys.stderr)

    if segments is None or segments.empty:
        # Provide a reasonable default template for ASML; users should customize from annual reports
        segments = pd.DataFrame(
            {
                "Segment": ["EUV", "DUV", "Services/Software"],
                "Revenue_%": [45, 35, 20],
                "Profitability_level": ["High", "Medium", "High"],
            }
        )

    # 2) Profitability & Growth
    gross_margin, op_margin = compute_margins(tkr)
    roic = compute_roic(tkr)
    rev_cagr = compute_revenue_cagr(tkr)
    eps_cagr = compute_eps_growth(tkr)

    profitability_df = pd.DataFrame(
        {
            "Metric": [
                "Gross Margin",
                "Operating Margin",
                "ROIC",
                "Revenue CAGR",
                "Earnings CAGR",
            ],
            "Value": [gross_margin, op_margin, roic, rev_cagr, eps_cagr],
            "Display": [
                pct(gross_margin),
                pct(op_margin),
                pct(roic),
                pct(rev_cagr),
                pct(eps_cagr),
            ],
        }
    )

    # 3) Industry Position & Competitiveness (peers snapshot by simple metrics)
    peer_tickers = [x.strip() for x in args.peers.split(",") if x.strip()]
    peer_rows = []
    for pt in peer_tickers:
        try:
            p = yf.Ticker(pt)
            gm, om = compute_margins(p)
            pe = None
            try:
                # yfinance's fast info may contain trailing PE; fallback to info
                pe = getattr(p, "fast_info", {}).get("trailing_pe", None)
            except Exception:
                pass
            if pe is None:
                pinf = getattr(p, "info", {})
                pe = pinf.get("trailingPE", None)
            mkcap = None
            try:
                mkcap = getattr(p, "fast_info", {}).get("market_cap", None)
            except Exception:
                pass
            if mkcap is None:
                pinf = getattr(p, "info", {})
                mkcap = pinf.get("marketCap", None)
            peer_rows.append(
                {
                    "Ticker": pt,
                    "GrossMargin": gm,
                    "OperatingMargin": om,
                    "PE": pe,
                    "MarketCap": mkcap,
                }
            )
        except Exception:
            peer_rows.append(
                {
                    "Ticker": pt,
                    "GrossMargin": np.nan,
                    "OperatingMargin": np.nan,
                    "PE": np.nan,
                    "MarketCap": np.nan,
                }
            )

    peers_df = pd.DataFrame(peer_rows)
    # Simple "moat" proxy composite for display: avg of normalized GM and OM
    if not peers_df.empty:
        peers_df["MoatScoreProxy"] = peers_df[["GrossMargin", "OperatingMargin"]].mean(
            axis=1, skipna=True
        )

    # 4) Macro/Cycle Sensitivity
    px_asml = get_price_history(args.ticker, period=args.period)
    px_ixic = get_price_history("^IXIC", period=args.period)
    px_gspc = get_price_history("^GSPC", period=args.period)
    px_tnx = get_price_history(
        "^TNX", period=args.period
    )  # 10Y yield index (x10); still ok for corr

    macro_rows = []
    if not px_asml.empty:
        macro_rows.append(("Volatility (ann.)", annualized_vol(px_asml)))
        if not px_ixic.empty:
            macro_rows.append(
                (
                    "Corr(ASML, NASDAQ)",
                    float(px_asml.pct_change().corr(px_ixic.pct_change())),
                )
            )
        if not px_gspc.empty:
            macro_rows.append(
                (
                    "Corr(ASML, S&P500)",
                    float(px_asml.pct_change().corr(px_gspc.pct_change())),
                )
            )
        if not px_tnx.empty:
            macro_rows.append(
                (
                    "Corr(ASML, 10Y Yield)",
                    float(px_asml.pct_change().corr(px_tnx.pct_change())),
                )
            )

    macro_df = pd.DataFrame(macro_rows, columns=["Metric", "Value"])

    # 5) Composite Scoring (0-1 per pillar)
    # Pillars: BusinessStability, Profitability, Growth, Moat_Position, Macro_Sensitivity (lower sensitivity is better)
    weights = risk_adjusted_weights(args.risk)

    # Business stability: favor balanced segments and services %
    try:
        rev_pct = segments["Revenue_%"].astype(float)
        # entropy for diversification (higher better)
        p = rev_pct / rev_pct.sum()
        entropy = -np.nansum([pi * np.log(pi) for pi in p if pi > 0]) / np.log(len(p))
        services_share = 0.0
        for i, s in segments.iterrows():
            if (
                isinstance(s.get("Segment"), str)
                and "service" in s.get("Segment").lower()
            ):
                services_share += float(s.get("Revenue_%", 0)) / 100.0
        business_stability_score = 0.7 * entropy + 0.3 * min(1.0, services_share)
    except Exception:
        business_stability_score = 0.5

    # Profitability: gross & operating margin (bounded scores)
    prof_score = np.nanmean(
        [
            bounded_score(gross_margin, 0.3, 0.7, True),
            bounded_score(op_margin, 0.15, 0.35, True),
            bounded_score(roic, 0.05, 0.25, True),
        ]
    )

    # Growth: revenue/earnings CAGR
    growth_score = np.nanmean(
        [
            bounded_score(rev_cagr, 0.05, 0.25, True),
            bounded_score(eps_cagr, 0.05, 0.30, True),
        ]
    )

    # Moat/Position: relative to peers by margin proxy & market cap scale
    moat_score = 0.5
    try:
        if not peers_df.empty:
            # Normalize moat proxy and market cap (log scale) within peers
            peers_df["LogMktCap"] = np.log(peers_df["MarketCap"].replace({0: np.nan}))
            moat = peers_df["MoatScoreProxy"]
            logm = peers_df["LogMktCap"]
            # rank the target ticker
            row = peers_df[peers_df["Ticker"] == args.ticker]
            if not row.empty:
                m = float(row["MoatScoreProxy"].iloc[0])
                lm = (
                    float(row["LogMktCap"].iloc[0])
                    if not pd.isna(row["LogMktCap"].iloc[0])
                    else np.nan
                )
                moat_score = np.nanmean(
                    [
                        bounded_score(
                            m,
                            float(np.nanpercentile(moat, 10)),
                            float(np.nanpercentile(moat, 90)),
                            True,
                        ),
                        bounded_score(
                            lm,
                            float(np.nanpercentile(logm, 10)),
                            float(np.nanpercentile(logm, 90)),
                            True,
                        ),
                    ]
                )
    except Exception:
        pass

    # Macro sensitivity: lower corr to rates and lower vol gets higher score
    try:
        vol = annualized_vol(px_asml) if not px_asml.empty else np.nan
        corr_rate = (
            float(px_asml.pct_change().corr(px_tnx.pct_change()))
            if (not px_asml.empty and not px_tnx.empty)
            else np.nan
        )
        macro_score = np.nanmean(
            [
                bounded_score(vol, 0.15, 0.55, False),  # lower vol better
                bounded_score(
                    abs(corr_rate) if not pd.isna(corr_rate) else np.nan,
                    0.0,
                    0.4,
                    False,
                ),  # lower |corr| better
            ]
        )
    except Exception:
        macro_score = 0.5

    pillar_scores = {
        "BusinessStability": float(
            business_stability_score if not pd.isna(business_stability_score) else 0.5
        ),
        "Profitability": float(prof_score if not pd.isna(prof_score) else 0.5),
        "Growth": float(growth_score if not pd.isna(growth_score) else 0.5),
        "Moat_Position": float(moat_score if not pd.isna(moat_score) else 0.5),
        "Macro_Sensitivity": float(macro_score if not pd.isna(macro_score) else 0.5),
    }

    composite = sum(pillar_scores[k] * weights[k] for k in pillar_scores)

    # -----------------------------
    # Build Markdown
    # -----------------------------
    lines = []
    title = f"# Stock-Picking Framework Report – {args.ticker}\n"
    lines.append(title)
    lines.append(
        f"*Generated on:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
    )
    lines.append("---\n")

    # Company header
    name = info.get("longName") if isinstance(info, dict) else None
    sector = info.get("sector") if isinstance(info, dict) else None
    industry = info.get("industry") if isinstance(info, dict) else None
    country = info.get("country") if isinstance(info, dict) else None
    lines.append("## Company Overview\n")
    lines.append(
        f"- **Name**: {name or args.ticker}\n- **Ticker**: `{args.ticker}`\n- **Sector/Industry**: {sector or '-'} / {industry or '-'}\n- **Country**: {country or '-'}\n"
    )

    # 1) Business Segments
    lines.append("\n## 1) 业务分部 (Business Segments)\n")
    lines.append("> 数据优先来自年报/投资者关系；这里允许手动或 JSON 输入（--segments_json）\n")
    try:
        lines.append(segments.to_markdown(index=False))
    except Exception:
        lines.append("- (segments table unavailable)\n")

    # 2) Profitability & Growth
    lines.append("\n## 2) 业务盈利能力 & 成长性 (Profitability & Growth)\n")
    lines.append(profitability_df[["Metric", "Display"]].to_markdown(index=False))

    # 3) Industry Position
    lines.append("\n## 3) 行业位置 & 竞争能力 (Industry Position & Competitiveness)\n")
    lines.append(f"- 同行对比 (peers): {', '.join(peer_tickers)}\n")
    if not peers_df.empty:
        display_cols = [
            "Ticker",
            "GrossMargin",
            "OperatingMargin",
            "PE",
            "MarketCap",
            "MoatScoreProxy",
        ]
        for c in ["GrossMargin", "OperatingMargin"]:
            if c in peers_df:
                peers_df[c] = peers_df[c].apply(
                    lambda v: pct(v) if pd.notna(v) else "-"
                )
        peers_disp = peers_df.copy()
        lines.append(peers_disp[display_cols].to_markdown(index=False))
    else:
        lines.append("- (peer snapshot unavailable)\n")

    # 4) Macro/Cycle Sensitivity
    lines.append("\n## 4) 行业周期 & 宏观敏感度 (Cycle & Macro)\n")
    if not macro_df.empty:
        # Format values
        macro_fmt = macro_df.copy()
        macro_fmt["Display"] = macro_fmt["Value"].apply(
            lambda v: f"{v:.2f}" if pd.notna(v) else "-"
        )
        lines.append(macro_fmt[["Metric", "Display"]].to_markdown(index=False))
    else:
        lines.append("- (macro sensitivity summary unavailable)\n")

    # 5) Composite Score
    lines.append("\n## 5) 综合评分 (Composite Score)\n")
    lines.append(f"- **Risk score** (controls weights): `{args.risk}` (1-100)\n")
    weights_table = pd.DataFrame([weights]).T.reset_index()
    weights_table.columns = ["Pillar", "Weight"]
    lines.append("### Weights\n")
    lines.append(weights_table.to_markdown(index=False))
    pillars_table = pd.DataFrame([pillar_scores]).T.reset_index()
    pillars_table.columns = ["Pillar", "Score(0-1)"]
    lines.append("\n### Pillar Scores\n")
    lines.append(pillars_table.to_markdown(index=False))
    lines.append(
        f"\n> **Composite Score:** `{composite:.3f}` (0–1, higher is better)\n"
    )

    # Save
    md = "\n".join(lines) + "\n"
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Markdown report written to: {args.output}")


if __name__ == "__main__":
    main()
