# -*- coding: utf-8 -*-
import warnings

import numpy as np
import pandas as pd
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api
from rqdatac.services.calendar import (get_next_trading_date,
                                       get_previous_trading_date)
from rqdatac.validators import (check_items_in_container, ensure_date_int,
                                ensure_date_range, ensure_list_of_string,
                                ensure_order_book_ids, ensure_string,
                                ensure_string_in)

VALID_FACTOR_TYPES = [
    "income_statement",
    "balance_sheet",
    "cash_flow_statement",
    "eod_indicator",
    "operational_indicator",
    "cash_flow_indicator",
    "financial_indicator",
    "growth_indicator",
    "alpha101",
    "moving_average_indicator",
    "obos_indicator",
    "energy_indicator",
    "other",
]


_UNIVERSE_MAPPING = {
    "whole_market": "whole_market",
    "000300.XSHG": "csi_300",
    "000905.XSHG": "csi_500",
    "000906.XSHG": "csi_800",
    "399303.XSHE": "399303_XSHE",
    "000852.XSHG": "000852_XSHG",
}

_METHOD_MAPPING = {
    "explicit": "explicit_factor_return",
    "implicit": "implicit_factor_return",
}


def model_to_server_api_prefix(model: str):
    """Convert model name to the corresponding server API prefix."""
    # client v2 --> server rqd6
    # client v1 --> server empty
    return model.replace("v2", "rqd6").replace("v1_", "")


@export_as_api(namespace="risk_model")
def get_factor_return(
    start_date,
    end_date,
    factors=None,
    universe="whole_market",
    method="implicit",
    industry_mapping="sws_2021",
    model="v1",
    market="cn",
):
    """获取因子收益率数据

    :param start_date: 开始日期（例如：‘2017-03-03’)
    :param end_date: 结束日期（例如：‘2017-03-20’)
    :param factors: 因子。默认获取全部因子的因子收益率
        当 method 参数取值为'implicit' ，可返回全部因子（风格、行业、市场联动）的隐式因子收益率；
        当 method 参数取值为'explicit' , 只返回风格因子的显式因子收益率。具体因子名称见说明文档 (Default value = None)
    :param universe: 股票池。默认调用全市场收益率。可选沪深300（‘000300.XSHG’）、中证500（'000905.XSHG'）
        、中证800（'000906.XSHG'）, 中证1000('000852.XSHG'), 国证2000('399303.XSHE') (Default value = "whole_market")
    :param method: 计算方法。默认为'implicit'（隐式因子收益率），可选'explicit'（显式风格因子收益率) (Default value = "implicit")
    :param market: 地区代码， 现在仅支持 'cn' (Default value = "cn")
    :param industry_mapping(str): 使用的行业类别，可选 sws_2021, citics_2019, 默认为 sws_2021
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :returns: pd.DataFrame. index 为日期，column 为因子字段名称。

    Usage example::
        # 获取介于2017-03-03 到 2017-03-20到隐式因子收益率数据
        get_factor_return('2017-03-03', '2017-03-20')

    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    start_date, end_date = ensure_date_range(start_date, end_date)

    if factors:
        factors = ensure_list_of_string(factors)
        if method == "implicit":
            check_items_in_container(factors, _IMPLICIT_RETURN_FACTORS, "factors")
        elif method == "explicit":
            check_items_in_container(factors, _EXPLICIT_RETURN_FACTORS, "factors")

    method = ensure_string(method)
    if method not in _METHOD_MAPPING:
        raise ValueError(
            "invalid method: {!r}, valid: explicit, implicit".format(method)
        )
    method = _METHOD_MAPPING[method]

    if universe not in _UNIVERSE_MAPPING:
        raise ValueError(
            "invalid universe: {!r}, valid: {}".format(
                universe, list(_UNIVERSE_MAPPING.keys())
            )
        )
    universe = _UNIVERSE_MAPPING[universe]

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_factor_return"
    data = get_client().execute(
        server_api,
        start_date,
        end_date,
        factors,
        universe,
        method,
        market=market,
        industry_mapping=industry_mapping,
    )
    data = [item for item in data if universe in item]
    if not data:
        return None
    df = pd.DataFrame(data)
    # convert to required format.
    df = df.pivot(index="date", columns="factor")[universe]
    df.sort_index(inplace=True)
    return df


def _get_all_industries(industry_name):
    if industry_name == "sw2021":
        return SHENWAN_INDUSTRY_2021
    elif industry_name == "citics2019":
        return CITICS_INDUSTRY_2019
    else:
        return SHENWAN_INDUSTRY_2014


@export_as_api(namespace="risk_model")
def get_factor_exposure(
    order_book_ids,
    start_date=None,
    end_date=None,
    factors=None,
    industry_mapping="sws_2021",
    model="v1",
    market="cn",
):
    """获取因子暴露度

    :param order_book_ids: 股票代码或代码列表
    :param start_date: 如'2013-01-04' (Default value = None)
    :param end_date: 如'2014-01-04' (Default value = None)
    :param factors: 如'yield', 'beta', 'volatility' (Default value = None)
    :param market: 地区代码, 如'cn' (Default value = "cn")
    :param industry_mapping: 是否按 2014 年后的申万行业分类标 准计算行业暴露度.默认为 True.
        若取值为 False,则 2014 年前的行业 暴露度按旧行业分类标准计算
    :param industry_mapping (str): 行业分类标准, 可选值包括 'sws_2021'(申万2021行业分类), 'sws_2014'(申万2014行业分类)
        默认取 'sws_2021' 行业分类
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :returns: MultiIndex DataFrame. index 第一个 level 为 order_book_id，第 二个 level 为 date，columns 为因子字段名称
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)

    check_items_in_container(
        industry_mapping, ["sw2014", "sw2021", "citics2019"], "industry_mapping"
    )

    order_book_ids = ensure_order_book_ids(order_book_ids)
    if not order_book_ids:
        raise ValueError("no valid order_book_id found")

    start_date, end_date = ensure_date_range(start_date, end_date)

    if factors is not None:
        factors = ensure_list_of_string(factors)
        if model == "v1":
            check_items_in_container(factors, exposure_factors, "factors")
        elif model == "v2":
            check_items_in_container(factors, exposure_factors_rqd6, "factors")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_factor_exposure"
    results = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        factors,
        industry_mapping=industry_mapping,
        market=market,
    )

    if not results:
        return None
    index_pairs = []
    data = []

    fields = [
        field
        for field in results[0].keys()
        if field not in ("order_book_id", "date", "industry")
    ]
    industry_factors = _get_all_industries(industry_mapping)
    for result in results:
        index_pairs.append((result["date"], result["order_book_id"]))
        row_data = [result.get(field, np.nan) for field in fields]

        # 填充行业因子数据
        for industry in industry_factors:
            if "industry" in result and result["industry"] == industry:
                industry_label = 1
            else:
                industry_label = 0
            row_data.append(industry_label)

        data.append(row_data)

    index = pd.MultiIndex.from_tuples(index_pairs, names=["date", "order_book_id"])
    fields.extend(industry_factors)
    result_df = pd.DataFrame(columns=fields, index=index, data=data)
    result_df.sort_index(inplace=True)

    no_data_book_id = set(order_book_ids) - set(result_df.index.levels[1])
    if no_data_book_id:
        warnings.warn("No data for this order_book_id :{}".format(no_data_book_id))

    if factors is not None:
        return result_df[factors]
    return result_df


exposure_factors = [
    "residual_volatility",
    "growth",
    "liquidity",
    "beta",
    "non_linear_size",
    "leverage",
    "earnings_yield",
    "size",
    "momentum",
    "book_to_price",
    "comovement",
]

exposure_factors_rqd6 = [
    "liquidity",
    "leverage",
    "earnings_variability",
    "earnings_quality",
    "profitability",
    "investment_quality",
    "book_to_price",
    "earnings_yield",
    "longterm_reversal",
    "growth",
    "momentum",
    "mid_cap",
    "size",
    "beta",
    "residual_volatility",
    "dividend_yield",
    "comovement",
]

# 申万2021行业分类
SHENWAN_INDUSTRY_2021 = [
    "银行",
    "计算机",
    "环保",
    "商贸零售",
    "电力设备",
    "建筑装饰",
    "建筑材料",
    "农林牧渔",
    "电子",
    "交通运输",
    "汽车",
    "纺织服饰",
    "医药生物",
    "房地产",
    "通信",
    "公用事业",
    "综合",
    "机械设备",
    "石油石化",
    "有色金属",
    "传媒",
    "家用电器",
    "基础化工",
    "非银金融",
    "社会服务",
    "轻工制造",
    "国防军工",
    "美容护理",
    "煤炭",
    "食品饮料",
    "钢铁",
]

# 申万2014 行业分类
SHENWAN_INDUSTRY_2014 = [
    "农林牧渔",
    "采掘",
    "化工",
    "钢铁",
    "有色金属",
    "电子",
    "家用电器",
    "食品饮料",
    "纺织服装",
    "轻工制造",
    "医药生物",
    "公用事业",
    "交通运输",
    "房地产",
    "商业贸易",
    "休闲服务",
    "综合",
    "建筑材料",
    "建筑装饰",
    "电气设备",
    "国防军工",
    "计算机",
    "传媒",
    "通信",
    "银行",
    "非银金融",
    "汽车",
    "机械设备",
]

# 中信2019 行业分类
CITICS_INDUSTRY_2019 = [
    "交通运输",
    "传媒",
    "农林牧渔",
    "医药",
    "商贸零售",
    "国防军工",
    "基础化工",
    "家电",
    "建材",
    "建筑",
    "房地产",
    "有色金属",
    "机械",
    "汽车",
    "消费者服务",
    "煤炭",
    "电力及公用事业",
    "电力设备及新能源",
    "电子",
    "石油石化",
    "纺织服装",
    "综合",
    "综合金融",
    "计算机",
    "轻工制造",
    "通信",
    "钢铁",
    "银行",
    "非银行金融",
    "食品饮料",
]

exposure_factors.extend(SHENWAN_INDUSTRY_2021)
exposure_factors.extend(SHENWAN_INDUSTRY_2014)
exposure_factors.extend(CITICS_INDUSTRY_2019)

exposure_factors_rqd6.extend(SHENWAN_INDUSTRY_2021)
exposure_factors_rqd6.extend(CITICS_INDUSTRY_2019)

_STYLE_FACTORS = {
    "residual_volatility",
    "growth",
    "liquidity",
    "beta",
    "non_linear_size",
    "leverage",
    "earnings_yield",
    "size",
    "momentum",
    "book_to_price",
}

_STYLE_FACTORS_RQD6 = {
    "liquidity",
    "leverage",
    "earnings_variability",
    "earnings_quality",
    "profitability",
    "investment_quality",
    "book_to_price",
    "earnings_yield",
    "longterm_reversal",
    "growth",
    "momentum",
    "mid_cap",
    "size",
    "beta",
    "residual_volatility",
    "dividend_yield",
}

_STYLE_FACTORS_RQD6TRD = _STYLE_FACTORS_RQD6.copy()
_STYLE_FACTORS_RQD6TRD.update(
    {"sentiment", "seasonality", "shortterm_reversal", "industry_momentum"}
)

_IMPLICIT_RETURN_FACTORS = exposure_factors
_EXPLICIT_RETURN_FACTORS = _STYLE_FACTORS


@export_as_api(namespace="risk_model")
def get_style_factor_exposure(
    order_book_ids,
    start_date,
    end_date,
    factors=None,
    model="v1",
    industry_mapping="sws_2021",
    market="cn",
):
    """获取个股风格因子暴露度

    :param order_book_ids: 证券代码（例如：‘600705.XSHG’）
    :param start_date: 开始日期（例如：‘2017-03-03’）
    :param end_date: 结束日期（例如：‘2017-03-20’）
    :param factors: 风格因子。默认调用全部因子的暴露度（'all'）。
        具体因子名称见说明文档 (Default value = None)
    :param market:  (Default value = "cn")
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1

    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)

    if factors is not None:
        factors = ensure_list_of_string(factors)
        if model == "v1":
            check_items_in_container(factors, _STYLE_FACTORS, "factors")
        elif model == "v2":
            check_items_in_container(factors, _STYLE_FACTORS_RQD6, "factors")
        elif model == "v2trd":
            check_items_in_container(factors, _STYLE_FACTORS_RQD6TRD, "factors")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_style_factor_exposure"
    df = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        factors,
        industry_mapping=industry_mapping,
        market=market,
    )
    if not df:
        return
    return pd.DataFrame(df).set_index(["order_book_id", "date"]).sort_index(level=1)


_DESCRIPTORS = {
    "daily_standard_deviation",
    "cumulative_range",
    "historical_sigma",
    "one_month_share_turnover",
    "three_months_share_turnover",
    "twelve_months_share_turnover",
    "earnings_to_price_ratio",
    "cash_earnings_to_price_ratio",
    "market_leverage",
    "debt_to_assets",
    "book_leverage",
    "sales_growth",
    "earnings_growth",
    "predicted_earning_to_price",
    "short_term_predicted_earnings_growth",
    "long_term_predicted_earnings_growth",
}

_DESCRIPTORS_RQD6 = {
    "one_month_share_turnover",
    "three_months_share_turnover",
    "twelve_months_share_turnover",
    "annualized_trade_value_ratio",
    "market_leverage",
    "debt_to_assets",
    "book_leverage",
    "variation_in_sales",
    "variation_in_earnings",
    "variation_in_cashflows",
    "variation_in_fw_eps",
    "accruals_balancesheet_version",
    "accruals_cashflow_version",
    "asset_turnover",
    "gross_profitability",
    "gross_margin",
    "returns_on_asset",
    "asset_growth",
    "capital_expenditure_growth",
    "issuance_growth",
    "predicted_earning_to_price",
    "earnings_to_price_ratio",
    "cash_earnings_to_price_ratio",
    "enterprice_multiple",
    "sales_growth",
    "earnings_growth",
    "predicted_growth_3_year",
    "relative_strength",
    "historical_alpha",
    "daily_standard_deviation",
    "cumulative_range",
    "historical_sigma",
    "dividend_to_price",
    "longterm_relative_strength",
    "longterm_historical_alpha",
}

_DESCRIPTORS_RQD6TRD = _DESCRIPTORS_RQD6.update({"earn", "epibs", "rribs"})


@export_as_api(namespace="risk_model")
def get_descriptor_exposure(
    order_book_ids,
    start_date,
    end_date,
    descriptors=None,
    model="v1",
    industry_mapping="sws_2021",
    market="cn",
):
    """获取个股细分因子暴露度

    :param order_book_ids: 证券代码（例如：‘600705.XSHG’）
    :param start_date: 开始日期（例如：‘2017-03-03’）
    :param end_date: 结束日期（例如：‘2017-03-20’）
    :param descriptors: 细分风格因子。默认调用全部因子的暴露度（'all'）。
        具体细分因子名称见说明文档 (Default value = None)
    :param market:  (Default value = "cn")
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :returns: MultiIndex DataFrame. index 第一个 level 为 order_book_id，第 二个 level 为 date，column 为细分风格因子字段名称。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)

    if descriptors is not None:
        if descriptors == "all":
            descriptors = None
        else:
            descriptors = ensure_list_of_string(descriptors)
            if model == "v1":
                check_items_in_container(descriptors, _DESCRIPTORS, "descriptors")
            elif model == "v2":
                check_items_in_container(descriptors, _DESCRIPTORS_RQD6, "descriptors")
            elif model == "v2trd":
                check_items_in_container(
                    descriptors, _DESCRIPTORS_RQD6TRD, "descriptors"
                )

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_descriptor_exposure"
    df = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        descriptors,
        industry_mapping=industry_mapping,
        market=market,
    )
    if not df:
        return
    return pd.DataFrame(df).set_index(["order_book_id", "date"]).sort_index(level=1)


@export_as_api(namespace="risk_model")
def get_stock_beta(
    order_book_ids,
    start_date,
    end_date,
    benchmark="000300.XSHG",
    model="v1",
    industry_mapping="sws_2021",
    market="cn",
):
    """获取个股相对于基准的贝塔

    :param order_book_ids: 证券代码（例如：‘600705.XSHG’）
    :param start_date: 开始日期（例如：‘2017-03-03’)
    :param end_date: 结束日期（例如：‘2017-03-20’）
    :param benchmark: 基准指数。默认为沪深300（‘000300.XSHG’）
        可选上证50（'000016.XSHG'）、中证500（'000905.XSHG'）、
        中证800（'000906.XSHG'）以及中证全指（'000985.XSHG'） (Default value = "000300.XSHG")
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param market:  (Default value = "cn")
    :returns: pandas.DataFrame，index 为日期，column 为个股的 order_book_id
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)

    all_benchmark = (
        "000300.XSHG",
        "000016.XSHG",
        "000905.XSHG",
        "000906.XSHG",
        "000985.XSHG",
        "000852.XSHG",
    )
    benchmark = ensure_string(benchmark, "benchmark")
    check_items_in_container(benchmark, all_benchmark, "benchmark")
    benchmark = benchmark.replace(".", "_")
    server_api = f"factor_{model_to_server_api_prefix(model)}.get_stock_beta"
    df = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        benchmark,
        industry_mapping=industry_mapping,
        market=market,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df = df.pivot(index="date", columns="order_book_id", values=benchmark).sort_index()
    return df


@export_as_api(namespace="risk_model")
def get_eigenfactor_adjusted_covariance(
    date,
    horizon="daily",
    model="v1",
    industry_mapping="sws_2021",
):
    """获取因子协方差矩阵（特征因子调整）

    :param date: str 日期（例如：‘2017-03-20’）
    :param horizon: str 预测期限。默认为日度（'daily'），可选月度（‘monthly’）或季度（'quarterly'）。
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param industry_mapping str                     所选用的行业映射, 可选值包括 sws_2021

    :return: pandas.DataFrame，其中 index 和 column 均为因子名称。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    date = get_previous_trading_date(get_next_trading_date(date))
    date = ensure_date_int(date)
    ensure_string_in(horizon, HORIZON_CONTAINER, "horizon")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_eigenfactor_adjusted_covariance"
    df = get_client().execute(
        server_api,
        date,
        horizon=horizon,
        industry_mapping=industry_mapping,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df.drop("date", axis=1, inplace=True)
    return df.reindex(columns=df.index)


@export_as_api(namespace="risk_model")
def get_factor_covariance(
    date,
    horizon="daily",
    model="v1",
    industry_mapping="sws_2021",
):
    """获取因子协方差矩阵

    :param date: str 日期（例如：‘2017-03-20’）
    :param horizon: str 预测期限。默认为日度（'daily'），可选月度（‘monthly’）或季度（'quarterly'）。
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param industry_mapping str                     所选用的行业映射, 可选值包括 sws_2021

    :return: pandas.DataFrame，其中 index 和 column 均为因子名称。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    date = get_previous_trading_date(get_next_trading_date(date))
    date = ensure_date_int(date)
    ensure_string_in(horizon, HORIZON_CONTAINER, "horizon")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_factor_covariance"
    df = get_client().execute(
        server_api,
        date,
        horizon=horizon,
        industry_mapping=industry_mapping,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df.drop("date", axis=1, inplace=True)
    return df.reindex(columns=df.index)


@export_as_api(namespace="risk_model")
def get_specific_return(
    order_book_ids,
    start_date,
    end_date,
    model="v1",
    industry_mapping="sws_2021",
):
    """获取个股特异收益率

    :param order_book_ids	str or [list of str]	证券代码（例如：‘600705.XSHG’）
    :param start_date	    str                 	开始日期（例如：‘2017-03-03’）
    :param end_date	        str	                    结束日期（例如：‘2017-03-20’）
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param industry_mapping str                     所选用的行业映射, 可选值包括 sws_2021

    :return: pandas.DataFrame，其中 index 为date, column 为 order_book_ids。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_specific_return"
    df = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        industry_mapping=industry_mapping,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df = df.pivot(
        index="date", columns="order_book_id", values="specific_return"
    ).sort_index()
    return df


@export_as_api(namespace="risk_model")
def get_specific_risk(
    order_book_ids,
    start_date,
    end_date,
    horizon="daily",
    model="v1",
    industry_mapping="sws_2021",
):
    """获取个股特异波动率(标准差)

    :param order_book_ids	str or [list of str]	证券代码（例如：‘600705.XSHG’）
    :param start_date	    str                 	开始日期（例如：‘2017-03-03’）
    :param end_date	        str	                    结束日期（例如：‘2017-03-20’）
    :param horizon	        str	    预测期限。默认为日度（'daily'），可选月度（‘monthly’）或季度（'quarterly'）
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param industry_mapping str                     所选用的行业映射, 可选值包括 sws_2021

    :return: pandas.DataFrame，其中 index 为date, column 为 order_book_ids。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)
    ensure_string_in(horizon, HORIZON_CONTAINER, "horizon")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_specific_risk"
    df = get_client().execute(
        server_api,
        order_book_ids,
        start_date,
        end_date,
        horizon=horizon,
        industry_mapping=industry_mapping,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df = df.pivot(
        index="date", columns="order_book_id", values="specific_risk"
    ).sort_index()
    return df


@export_as_api(namespace="risk_model")
def get_cross_sectional_bias(
    start_date,
    end_date,
    type="factor",
    model="v1",
    industry_mapping="sws_2021",
):
    """获取横截面偏差系数

    :param start_date	    str                 	开始日期（例如：‘2017-03-03’）
    :param end_date	        str	                    结束日期（例如：‘2017-03-20’）
    :param type	            str	                    默认为 'factor'，可选 'specific'
    :param model: 选用的模型, 可选模型包括 v1, v2; 默认为 v1
    :param industry_mapping str                     所选用的行业映射, 可选值包括 sws_2021

    :return: pandas.DataFrame，其中 index 为date, column 包含 'daily'、'monthly'  和 'quarterly' 三个字段。
    """
    industry_mapping = _convert_industry_mapping(industry_mapping)
    start_date, end_date = ensure_date_range(start_date, end_date)
    ensure_string_in(type, ["factor", "specific"], "horizon")

    server_api = f"factor_{model_to_server_api_prefix(model)}.get_cross_sectional_bias"
    df = get_client().execute(
        server_api,
        start_date,
        end_date,
        type=type,
        industry_mapping=industry_mapping,
    )
    if not df:
        return
    df = pd.DataFrame(df)
    df = df.pivot(index="date", columns="horizon", values="bias").sort_index()
    return df


HORIZON_CONTAINER = ["daily", "monthly", "quarterly"]


# 将行业信息定义成与 rqdatad 统一的形式.
def _convert_industry_mapping(industry_mapping):
    """处理用户输入的 industry_mapping 信息"""
    # True 与 False是为了跟旧版本兼容
    input_mapping = {
        True: "sw2021",
        False: "sw2014",
        "sws_2021": "sw2021",
        "sws_2014": "sw2014",
        "citics_2019": "citics2019",
    }
    return input_mapping.get(industry_mapping, industry_mapping)
