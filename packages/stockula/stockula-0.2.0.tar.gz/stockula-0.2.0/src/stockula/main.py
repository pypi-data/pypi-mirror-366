"""Stockula main entry point."""

# Suppress warnings early - before any imports that might trigger them
import logging

logging.getLogger("alembic.runtime.migration").setLevel(logging.WARNING)
logging.getLogger("alembic").setLevel(logging.WARNING)

import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="joblib")

import os

os.environ["JOBLIB_TEMP_FOLDER"] = "/tmp"

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from .backtesting import (
    DoubleEMACrossStrategy,
    FRAMAStrategy,
    KAMAStrategy,
    KaufmanEfficiencyStrategy,
    MACDStrategy,
    RSIStrategy,
    SMACrossStrategy,
    TRIMACrossStrategy,
    TripleEMACrossStrategy,
    VAMAStrategy,
    VIDYAStrategy,
)
from .config import StockulaConfig
from .config.models import (
    BacktestResult,
    PortfolioBacktestResults,
    StrategyBacktestSummary,
)
from .container import Container, create_container
from .domain import Category
from .interfaces import IBacktestRunner, IDataFetcher, ILoggingManager, IStockForecaster
from .technical_analysis import TechnicalIndicators

# Global logging manager and console instances
log_manager: ILoggingManager | None = None
console = Console()


def date_to_string(date_value: str | date | None) -> str | None:
    """Convert date or string to string format."""
    if date_value is None:
        return None
    if isinstance(date_value, str):
        return date_value
    return date_value.strftime("%Y-%m-%d")


@inject
def setup_logging(
    config: StockulaConfig,
    logging_manager: ILoggingManager = Provide[Container.logging_manager],
) -> None:
    """Configure logging based on configuration."""
    global log_manager
    log_manager = logging_manager
    log_manager.setup(config)


def get_strategy_class(strategy_name: str) -> type[Any] | None:
    """Get strategy class by name."""
    strategies = {
        "smacross": SMACrossStrategy,
        "rsi": RSIStrategy,
        "macd": MACDStrategy,
        "doubleemacross": DoubleEMACrossStrategy,
        "tripleemacross": TripleEMACrossStrategy,
        "trimacross": TRIMACrossStrategy,
        "vidya": VIDYAStrategy,
        "kama": KAMAStrategy,
        "frama": FRAMAStrategy,
        "vama": VAMAStrategy,
        "er": KaufmanEfficiencyStrategy,
    }
    return strategies.get(strategy_name.lower())


@inject
def run_technical_analysis(
    ticker: str,
    config: StockulaConfig,
    data_fetcher: IDataFetcher = Provide[Container.data_fetcher],
    show_progress: bool = True,
) -> dict[str, Any]:
    """Run technical analysis for a ticker.

    Args:
        ticker: Stock symbol
        config: Configuration object
        data_fetcher: Injected data fetcher
        show_progress: Whether to show progress bars

    Returns:
        Dictionary with indicator results
    """
    data = data_fetcher.get_stock_data(
        ticker,
        start=date_to_string(config.data.start_date),
        end=date_to_string(config.data.end_date),
        interval=config.data.interval,
    )

    ta = TechnicalIndicators(data)
    results = {"ticker": ticker, "indicators": {}}
    ta_config = config.technical_analysis

    # Count total indicators to calculate
    total_indicators = 0
    if "sma" in ta_config.indicators:
        total_indicators += len(ta_config.sma_periods)
    if "ema" in ta_config.indicators:
        total_indicators += len(ta_config.ema_periods)
    if "rsi" in ta_config.indicators:
        total_indicators += 1
    if "macd" in ta_config.indicators:
        total_indicators += 1
    if "bbands" in ta_config.indicators:
        total_indicators += 1
    if "atr" in ta_config.indicators:
        total_indicators += 1
    if "adx" in ta_config.indicators:
        total_indicators += 1

    if show_progress and total_indicators > 0:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            transient=True,  # Remove progress bar when done
        ) as progress:
            task = progress.add_task(
                f"[cyan]Computing {total_indicators} technical indicators for {ticker}...",
                total=total_indicators,
            )

            current_step = 0

            if "sma" in ta_config.indicators:
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                for period in ta_config.sma_periods:
                    progress.update(
                        task,
                        description=f"[cyan]Computing SMA({period}) for {ticker}...",
                    )
                    indicators_dict[f"SMA_{period}"] = ta.sma(period).iloc[-1]
                    current_step += 1
                    progress.advance(task)

            if "ema" in ta_config.indicators:
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                for period in ta_config.ema_periods:
                    progress.update(
                        task,
                        description=f"[cyan]Computing EMA({period}) for {ticker}...",
                    )
                    indicators_dict[f"EMA_{period}"] = ta.ema(period).iloc[-1]
                    current_step += 1
                    progress.advance(task)

            if "rsi" in ta_config.indicators:
                progress.update(task, description=f"[cyan]Computing RSI for {ticker}...")
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                indicators_dict["RSI"] = ta.rsi(ta_config.rsi_period).iloc[-1]
                current_step += 1
                progress.advance(task)

            if "macd" in ta_config.indicators:
                progress.update(task, description=f"[cyan]Computing MACD for {ticker}...")
                macd_data = ta.macd(**ta_config.macd_params)
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                indicators_dict["MACD"] = macd_data.iloc[-1].to_dict()
                current_step += 1
                progress.advance(task)

            if "bbands" in ta_config.indicators:
                progress.update(task, description=f"[cyan]Computing Bollinger Bands for {ticker}...")
                bbands_data = ta.bbands(**ta_config.bbands_params)
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                indicators_dict["BBands"] = bbands_data.iloc[-1].to_dict()
                current_step += 1
                progress.advance(task)

            if "atr" in ta_config.indicators:
                progress.update(task, description=f"[cyan]Computing ATR for {ticker}...")
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                indicators_dict["ATR"] = ta.atr(ta_config.atr_period).iloc[-1]
                current_step += 1
                progress.advance(task)

            if "adx" in ta_config.indicators:
                progress.update(task, description=f"[cyan]Computing ADX for {ticker}...")
                indicators_dict = results["indicators"]
                assert isinstance(indicators_dict, dict)
                indicators_dict["ADX"] = ta.adx(14).iloc[-1]
                current_step += 1
                progress.advance(task)
    else:
        # Run without progress bars (for single indicators or when disabled)
        if "sma" in ta_config.indicators:
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            for period in ta_config.sma_periods:
                indicators_dict[f"SMA_{period}"] = ta.sma(period).iloc[-1]

        if "ema" in ta_config.indicators:
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            for period in ta_config.ema_periods:
                indicators_dict[f"EMA_{period}"] = ta.ema(period).iloc[-1]

        if "rsi" in ta_config.indicators:
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            indicators_dict["RSI"] = ta.rsi(ta_config.rsi_period).iloc[-1]

        if "macd" in ta_config.indicators:
            macd_data = ta.macd(**ta_config.macd_params)
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            indicators_dict["MACD"] = macd_data.iloc[-1].to_dict()

        if "bbands" in ta_config.indicators:
            bbands_data = ta.bbands(**ta_config.bbands_params)
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            indicators_dict["BBands"] = bbands_data.iloc[-1].to_dict()

        if "atr" in ta_config.indicators:
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            indicators_dict["ATR"] = ta.atr(ta_config.atr_period).iloc[-1]

        if "adx" in ta_config.indicators:
            indicators_dict = results["indicators"]
            assert isinstance(indicators_dict, dict)
            indicators_dict["ADX"] = ta.adx(14).iloc[-1]

    return results


@inject
def run_backtest(
    ticker: str,
    config: StockulaConfig,
    backtest_runner: IBacktestRunner = Provide[Container.backtest_runner],
) -> list[dict[str, Any]]:
    """Run backtesting for a ticker.

    Args:
        ticker: Stock symbol
        config: Configuration object
        backtest_runner: Injected backtest runner

    Returns:
        List of backtest results
    """
    runner = backtest_runner

    results = []

    # Check if we should use train/test split for backtesting
    # Note: This is for backtest parameter optimization, not forecast evaluation
    use_train_test_split = False  # Disabled for now since train/test is in forecast config

    for strategy_config in config.backtest.strategies:
        strategy_class = get_strategy_class(strategy_config.name)
        if not strategy_class:
            print(f"Warning: Unknown strategy '{strategy_config.name}'")
            continue

        # Set strategy parameters if provided
        if strategy_config.parameters:
            # Set class attributes from parameters
            for key, value in strategy_config.parameters.items():
                setattr(strategy_class, key, value)

        try:
            if use_train_test_split:
                # Run with train/test split
                backtest_result = runner.run_with_train_test_split(
                    ticker,
                    strategy_class,
                    train_start_date=date_to_string(config.forecast.train_start_date),
                    train_end_date=date_to_string(config.forecast.train_end_date),
                    test_start_date=date_to_string(config.forecast.test_start_date),
                    test_end_date=date_to_string(config.forecast.test_end_date),
                    optimize_on_train=config.backtest.optimize,
                    param_ranges=config.backtest.optimization_params
                    if config.backtest.optimize and config.backtest.optimization_params
                    else None,
                )

                # Create result entry with train/test results
                result_entry = {
                    "ticker": ticker,
                    "strategy": strategy_config.name,
                    "parameters": backtest_result.get("optimized_parameters", strategy_config.parameters),
                    "train_period": backtest_result["train_period"],
                    "test_period": backtest_result["test_period"],
                    "train_results": backtest_result["train_results"],
                    "test_results": backtest_result["test_results"],
                    "performance_degradation": backtest_result.get("performance_degradation", {}),
                }

                # For backward compatibility, also include test results as top-level metrics
                result_entry.update(
                    {
                        "return_pct": backtest_result["test_results"]["return_pct"],
                        "sharpe_ratio": backtest_result["test_results"]["sharpe_ratio"],
                        "max_drawdown_pct": backtest_result["test_results"]["max_drawdown_pct"],
                        "num_trades": backtest_result["test_results"]["num_trades"],
                        "win_rate": backtest_result["test_results"]["win_rate"],
                    }
                )

            else:
                # Run traditional backtest without train/test split
                # Determine which dates to use for backtesting
                backtest_start = None
                backtest_end = None

                # First check if backtest has specific dates
                if config.backtest.start_date and config.backtest.end_date:
                    backtest_start = date_to_string(config.backtest.start_date)
                    backtest_end = date_to_string(config.backtest.end_date)
                # Fall back to general data dates
                elif config.data.start_date and config.data.end_date:
                    backtest_start = date_to_string(config.data.start_date)
                    backtest_end = date_to_string(config.data.end_date)

                backtest_result = runner.run_from_symbol(
                    ticker,
                    strategy_class,
                    start_date=backtest_start,
                    end_date=backtest_end,
                )

                # Handle NaN values for win rate when there are no trades
                win_rate = backtest_result.get("Win Rate [%]", 0)
                if pd.isna(win_rate):
                    win_rate = None if backtest_result["# Trades"] == 0 else 0

                result_entry = {
                    "ticker": ticker,
                    "strategy": strategy_config.name,
                    "parameters": strategy_config.parameters,
                    "return_pct": backtest_result["Return [%]"],
                    "sharpe_ratio": backtest_result["Sharpe Ratio"],
                    "max_drawdown_pct": backtest_result["Max. Drawdown [%]"],
                    "num_trades": backtest_result["# Trades"],
                    "win_rate": win_rate,
                }

                # Add portfolio information from the raw backtest result
                if "Initial Cash" in backtest_result:
                    result_entry["initial_cash"] = backtest_result["Initial Cash"]
                if "Start Date" in backtest_result:
                    result_entry["start_date"] = backtest_result["Start Date"]
                if "End Date" in backtest_result:
                    result_entry["end_date"] = backtest_result["End Date"]
                if "Trading Days" in backtest_result:
                    result_entry["trading_days"] = backtest_result["Trading Days"]
                if "Calendar Days" in backtest_result:
                    result_entry["calendar_days"] = backtest_result["Calendar Days"]

            results.append(result_entry)
        except Exception as e:
            print(f"Error backtesting {strategy_config.name} on {ticker}: {e}")

    return results


@inject
def run_forecast_with_evaluation(
    ticker: str,
    config: StockulaConfig,
    stock_forecaster: IStockForecaster = Provide[Container.stock_forecaster],
) -> dict[str, Any]:
    """Run forecasting with train/test split and evaluation.

    Args:
        ticker: Stock symbol
        config: Configuration object
        stock_forecaster: Injected stock forecaster

    Returns:
        Dictionary with forecast results and evaluation metrics
    """
    if log_manager:
        log_manager.info(f"\nForecasting {ticker} with train/test evaluation...")

    forecaster = stock_forecaster

    try:
        # Use forecast date fields if available, otherwise fall back to data dates
        train_start = config.forecast.train_start_date or config.data.start_date
        train_end = config.forecast.train_end_date or config.data.end_date
        test_start = config.forecast.test_start_date
        test_end = config.forecast.test_end_date

        result = forecaster.forecast_from_symbol_with_evaluation(
            ticker,
            train_start_date=date_to_string(train_start),
            train_end_date=date_to_string(train_end),
            test_start_date=date_to_string(test_start),
            test_end_date=date_to_string(test_end),
            model_list=config.forecast.model_list,
            ensemble=config.forecast.ensemble,
            max_generations=config.forecast.max_generations,
        )

        predictions = result["predictions"]
        model_info = forecaster.get_best_model()

        if log_manager:
            log_manager.info(f"Forecast completed for {ticker} using {model_info['model_name']}")

        forecast_result = {
            "ticker": ticker,
            "current_price": float(predictions["forecast"].iloc[0]),
            "forecast_price": float(predictions["forecast"].iloc[-1]),
            "lower_bound": float(predictions["lower_bound"].iloc[-1]),
            "upper_bound": float(predictions["upper_bound"].iloc[-1]),
            "forecast_length": config.forecast.forecast_length,
            "start_date": predictions.index[0].strftime("%Y-%m-%d"),
            "end_date": predictions.index[-1].strftime("%Y-%m-%d"),
            "best_model": model_info["model_name"],
            "model_params": model_info.get("model_params", {}),
            "train_period": result["train_period"],
            "test_period": result["test_period"],
        }

        # Add evaluation metrics if available
        if result["evaluation_metrics"]:
            forecast_result["evaluation"] = result["evaluation_metrics"]
            if log_manager:
                log_manager.info(
                    f"Evaluation metrics for {ticker}: RMSE={result['evaluation_metrics']['rmse']:.2f}, "
                    f"MAPE={result['evaluation_metrics']['mape']:.2f}%"
                )

        return forecast_result

    except KeyboardInterrupt:
        if log_manager:
            log_manager.warning(f"Forecast for {ticker} interrupted by user")
        return {"ticker": ticker, "error": "Interrupted by user"}
    except Exception as e:
        if log_manager:
            log_manager.error(f"Error forecasting {ticker}: {e}")
        return {"ticker": ticker, "error": str(e)}


def run_forecast(
    ticker: str,
    config: StockulaConfig,
    stock_forecaster: IStockForecaster = Provide[Container.stock_forecaster],
) -> dict[str, Any]:
    """Run forecasting for a ticker.

    Args:
        ticker: Stock symbol
        config: Configuration object
        stock_forecaster: Injected stock forecaster

    Returns:
        Dictionary with forecast results
    """
    if log_manager:
        log_manager.info(f"\nForecasting {ticker} for {config.forecast.forecast_length} days...")

    forecaster = stock_forecaster

    try:
        predictions = forecaster.forecast_from_symbol(
            ticker,
            start_date=date_to_string(config.data.start_date),
            end_date=date_to_string(config.data.end_date),
            model_list=config.forecast.model_list,
            ensemble=config.forecast.ensemble,
            max_generations=config.forecast.max_generations,
        )

        model_info = forecaster.get_best_model()

        if log_manager:
            log_manager.info(f"Forecast completed for {ticker} using {model_info['model_name']}")

        return {
            "ticker": ticker,
            "current_price": predictions["forecast"].iloc[0],
            "forecast_price": predictions["forecast"].iloc[-1],
            "lower_bound": predictions["lower_bound"].iloc[-1],
            "upper_bound": predictions["upper_bound"].iloc[-1],
            "forecast_length": config.forecast.forecast_length,
            "start_date": predictions.index[0].strftime("%Y-%m-%d"),
            "end_date": predictions.index[-1].strftime("%Y-%m-%d"),
            "best_model": model_info["model_name"],
            "model_params": model_info.get("model_params", {}),
        }
    except KeyboardInterrupt:
        if log_manager:
            log_manager.warning(f"Forecast for {ticker} interrupted by user")
        return {"ticker": ticker, "error": "Interrupted by user"}
    except Exception as e:
        if log_manager:
            log_manager.error(f"Error forecasting {ticker}: {e}")
        return {"ticker": ticker, "error": str(e)}


def save_detailed_report(
    strategy_name: str,
    strategy_results: list[dict],
    results: dict[str, Any],
    config: StockulaConfig,
    portfolio_results: PortfolioBacktestResults | None = None,
) -> str:
    """Save detailed strategy report to file.

    Args:
        strategy_name: Name of the strategy
        strategy_results: List of backtest results for this strategy
        results: Overall results dictionary
        config: Configuration object

    Returns:
        Path to the saved report file
    """
    import json
    from pathlib import Path

    # Create reports directory if it doesn't exist
    reports_dir = Path(config.output.get("results_dir", "./results")) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"strategy_report_{strategy_name}_{timestamp}.json"

    # Prepare detailed report data
    report_data = {
        "strategy": strategy_name,
        "timestamp": timestamp,
        "date_range": {
            "start": date_to_string(config.data.start_date),
            "end": date_to_string(config.data.end_date),
        },
        "portfolio": {
            "initial_value": results.get("initial_portfolio_value", 0),
            "initial_capital": results.get("initial_capital", 0),
        },
        "broker_config": {
            "name": config.backtest.broker_config.name if config.backtest.broker_config else "legacy",
            "commission_type": config.backtest.broker_config.commission_type
            if config.backtest.broker_config
            else "percentage",
            "commission_value": config.backtest.broker_config.commission_value
            if config.backtest.broker_config
            else config.backtest.commission,
            "min_commission": config.backtest.broker_config.min_commission if config.backtest.broker_config else None,
            "regulatory_fees": config.backtest.broker_config.regulatory_fees if config.backtest.broker_config else 0,
        },
        "detailed_results": strategy_results,
        "summary": {
            "total_trades": sum(r.get("num_trades", 0) for r in strategy_results),
            "winning_stocks": sum(1 for r in strategy_results if r.get("return_pct", 0) > 0),
            "losing_stocks": sum(1 for r in strategy_results if r.get("return_pct", 0) < 0),
            "average_return": sum(r.get("return_pct", 0) for r in strategy_results) / len(strategy_results)
            if strategy_results
            else 0,
            "average_sharpe": sum(r.get("sharpe_ratio", 0) for r in strategy_results) / len(strategy_results)
            if strategy_results
            else 0,
        },
    }

    # Save report
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2, default=str)

    # Also save structured results if provided
    if portfolio_results:
        structured_file = reports_dir / f"portfolio_backtest_{timestamp}.json"
        with open(structured_file, "w") as f:
            # Convert to dict using model_dump
            json.dump(portfolio_results.model_dump(), f, indent=2, default=str)

    return str(report_file)


def create_portfolio_backtest_results(
    results: dict[str, Any],
    config: StockulaConfig,
    strategy_results: dict[str, list[dict]],
) -> PortfolioBacktestResults:
    """Create structured backtest results.

    Args:
        results: Main results dictionary with initial values
        config: Configuration object
        strategy_results: Raw backtest results grouped by strategy

    Returns:
        Structured portfolio backtest results
    """
    # Build strategy summaries
    strategy_summaries = []

    for strategy_name, backtests in strategy_results.items():
        # Create BacktestResult objects
        detailed_results = []
        for backtest in backtests:
            detailed_results.append(
                BacktestResult(
                    ticker=backtest["ticker"],
                    strategy=backtest["strategy"],
                    parameters=backtest.get("parameters", {}),
                    return_pct=backtest["return_pct"],
                    sharpe_ratio=backtest["sharpe_ratio"],
                    max_drawdown_pct=backtest["max_drawdown_pct"],
                    num_trades=backtest["num_trades"],
                    win_rate=backtest.get("win_rate"),
                )
            )

        # Calculate summary metrics
        total_return = sum(r.return_pct for r in detailed_results)
        avg_return = total_return / len(detailed_results) if detailed_results else 0
        avg_sharpe = sum(r.sharpe_ratio for r in detailed_results) / len(detailed_results) if detailed_results else 0
        total_trades = sum(r.num_trades for r in detailed_results)
        winning_stocks = sum(1 for r in detailed_results if r.return_pct > 0)
        losing_stocks = sum(1 for r in detailed_results if r.return_pct < 0)

        # Calculate approximate final portfolio value
        final_value = results["initial_portfolio_value"] * (1 + avg_return / 100)

        # Get strategy parameters from first result
        strategy_params = detailed_results[0].parameters if detailed_results else {}

        # Create strategy summary
        summary = StrategyBacktestSummary(
            strategy_name=strategy_name,
            parameters=strategy_params,
            initial_portfolio_value=results["initial_portfolio_value"],
            final_portfolio_value=final_value,
            total_return_pct=avg_return,
            total_trades=total_trades,
            winning_stocks=winning_stocks,
            losing_stocks=losing_stocks,
            average_return_pct=avg_return,
            average_sharpe_ratio=avg_sharpe,
            detailed_results=detailed_results,
        )

        strategy_summaries.append(summary)

    # Create broker config dict
    broker_config = {}
    if config.backtest.broker_config:
        broker_config = {
            "name": config.backtest.broker_config.name,
            "commission_type": config.backtest.broker_config.commission_type,
            "commission_value": config.backtest.broker_config.commission_value,
            "min_commission": config.backtest.broker_config.min_commission,
            "regulatory_fees": config.backtest.broker_config.regulatory_fees,
            "exchange_fees": getattr(config.backtest.broker_config, "exchange_fees", 0),
        }
    else:
        broker_config = {
            "name": "legacy",
            "commission_type": "percentage",
            "commission_value": config.backtest.commission,
            "min_commission": None,
            "regulatory_fees": 0,
            "exchange_fees": 0,
        }

    # Create portfolio results
    # Get date range from config or results
    date_start: str = "N/A"
    date_end: str = "N/A"

    # First try backtest dates, then data dates
    if config.backtest.start_date:
        date_start_val = date_to_string(config.backtest.start_date)
        if date_start_val is not None:
            date_start = date_start_val
    elif config.data.start_date:
        date_start_val = date_to_string(config.data.start_date)
        if date_start_val is not None:
            date_start = date_start_val

    if config.backtest.end_date:
        date_end_val = date_to_string(config.backtest.end_date)
        if date_end_val is not None:
            date_end = date_end_val
    elif config.data.end_date:
        date_end_val = date_to_string(config.data.end_date)
        if date_end_val is not None:
            date_end = date_end_val

    # If dates not in config, try to get from backtest results
    if (date_start == "N/A" or date_end == "N/A") and results.get("backtesting") and len(results["backtesting"]) > 0:
        # Look through all results to find one with dates
        for backtest_result in results["backtesting"]:
            if date_start == "N/A" and "start_date" in backtest_result:
                date_start = backtest_result["start_date"]
            if date_end == "N/A" and "end_date" in backtest_result:
                date_end = backtest_result["end_date"]
            # Stop if we found both dates
            if date_start != "N/A" and date_end != "N/A":
                break

    portfolio_results = PortfolioBacktestResults(
        initial_portfolio_value=results.get("initial_portfolio_value", 0),
        initial_capital=results.get("initial_capital", 0),
        date_range={
            "start": date_start,
            "end": date_end,
        },
        broker_config=broker_config,
        strategy_summaries=strategy_summaries,
    )

    return portfolio_results


def print_results(results: dict[str, Any], output_format: str = "console", config=None, container=None):
    """Print results in specified format.

    Args:
        results: Results dictionary
        output_format: Output format (console, json)
        config: Optional configuration object for portfolio composition
        container: Optional DI container for fetching data
    """
    if output_format == "json":
        console.print_json(json.dumps(results, indent=2, default=str))
    else:
        # Console output with Rich formatting

        if "technical_analysis" in results:
            console.print("\n[bold blue]Technical Analysis Results[/bold blue]", style="bold")

            for ta_result in results["technical_analysis"]:
                table = Table(title=f"Technical Analysis - {ta_result['ticker']}")
                table.add_column("Indicator", style="cyan", no_wrap=True)
                table.add_column("Value", style="magenta")

                for indicator, value in ta_result["indicators"].items():
                    if isinstance(value, dict):
                        for k, v in value.items():
                            formatted_value = f"{v:.2f}" if isinstance(v, int | float) else str(v)
                            table.add_row(f"{indicator} - {k}", formatted_value)
                    else:
                        formatted_value = f"{value:.2f}" if isinstance(value, int | float) else str(value)
                        table.add_row(indicator, formatted_value)

                console.print(table)

        if "backtesting" in results:
            # Check if we have multiple strategies
            strategies = {b["strategy"] for b in results["backtesting"]}

            # Display general portfolio information
            console.print("\n[bold green]=== Backtesting Results ===[/bold green]")

            # Create portfolio information panel
            portfolio_info = []

            # Extract portfolio info from results metadata
            if "portfolio" in results:
                portfolio_data = results["portfolio"]
                if "initial_capital" in portfolio_data:
                    portfolio_info.append(f"[cyan]Initial Capital:[/cyan] ${portfolio_data['initial_capital']:,.2f}")
                if "start" in portfolio_data and portfolio_data["start"]:
                    portfolio_info.append(f"[cyan]Start Date:[/cyan] {portfolio_data['start']}")
                if "end" in portfolio_data and portfolio_data["end"]:
                    portfolio_info.append(f"[cyan]End Date:[/cyan] {portfolio_data['end']}")

            # If portfolio info not in metadata, try to extract from backtest results
            if not portfolio_info and results.get("backtesting"):
                # Get portfolio information from the first backtest result
                first_backtest = results["backtesting"][0] if results["backtesting"] else {}

                if "initial_cash" in first_backtest:
                    portfolio_info.append(f"[cyan]Initial Capital:[/cyan] ${first_backtest['initial_cash']:,.2f}")
                if "start_date" in first_backtest:
                    portfolio_info.append(f"[cyan]Start Date:[/cyan] {first_backtest['start_date']}")
                if "end_date" in first_backtest:
                    portfolio_info.append(f"[cyan]End Date:[/cyan] {first_backtest['end_date']}")
                if "trading_days" in first_backtest:
                    portfolio_info.append(f"[cyan]Trading Days:[/cyan] {first_backtest['trading_days']:,}")
                if "calendar_days" in first_backtest:
                    portfolio_info.append(f"[cyan]Calendar Days:[/cyan] {first_backtest['calendar_days']:,}")

                # Fallback: Look for cash/initial capital in other locations
                if not portfolio_info:
                    initial_capital = results.get("initial_capital")
                    if initial_capital:
                        portfolio_info.append(f"[cyan]Initial Capital:[/cyan] ${initial_capital:,.2f}")

                    # Add date information if available
                    start_date = results.get("start_date") or results.get("start")
                    end_date = results.get("end_date") or results.get("end")
                    if start_date:
                        portfolio_info.append(f"[cyan]Start Date:[/cyan] {start_date}")
                    if end_date:
                        portfolio_info.append(f"[cyan]End Date:[/cyan] {end_date}")

            # Display portfolio information if available
            if portfolio_info:
                console.print("[bold blue]Portfolio Information:[/bold blue]")
                for info in portfolio_info:
                    console.print(f"  {info}")
                console.print()  # Add blank line

            # Display portfolio composition table (only if config and container are provided)
            if config and container:
                table = Table(title="Portfolio Composition")
                table.add_column("Ticker", style="cyan", no_wrap=True)
                table.add_column("Category", style="yellow")
                table.add_column("Quantity", style="white", justify="right")
                table.add_column("Allocation %", style="green", justify="right")
                table.add_column("Value", style="blue", justify="right")
                table.add_column("Status", style="magenta")

                # Get portfolio composition information
                portfolio = container.domain_factory().create_portfolio(config)
                all_assets = portfolio.get_all_assets()

                # Get hold-only categories from config
                hold_only_category_names = set(config.backtest.hold_only_categories)
                hold_only_categories = set()
                for category_name in hold_only_category_names:
                    try:
                        hold_only_categories.add(Category[category_name])
                    except KeyError:
                        pass  # Skip unknown categories

                # Get current prices for calculation
                fetcher = container.data_fetcher()
                symbols = [asset.symbol for asset in all_assets]
                try:
                    current_prices = fetcher.get_current_prices(symbols, show_progress=False)
                    total_portfolio_value = sum(
                        asset.quantity * current_prices.get(asset.symbol, 0) for asset in all_assets
                    )

                    for asset in all_assets:
                        current_price = current_prices.get(asset.symbol, 0)
                        asset_value = asset.quantity * current_price
                        allocation_pct = (asset_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0

                        # Determine status
                        status = "Hold Only" if asset.category in hold_only_categories else "Tradeable"
                        status_color = "yellow" if status == "Hold Only" else "green"

                        table.add_row(
                            asset.symbol,
                            asset.category.name if hasattr(asset.category, "name") else str(asset.category),
                            f"{asset.quantity:.2f}",
                            f"{allocation_pct:.1f}%",
                            f"${asset_value:,.2f}",
                            f"[{status_color}]{status}[/{status_color}]",
                        )
                except Exception:
                    # Fallback if we can't get prices
                    for asset in all_assets:
                        status = "Hold Only" if asset.category in hold_only_categories else "Tradeable"
                        status_color = "yellow" if status == "Hold Only" else "green"

                        table.add_row(
                            asset.symbol,
                            asset.category.name if hasattr(asset.category, "name") else str(asset.category),
                            f"{asset.quantity:.2f}",
                            "N/A",
                            "N/A",
                            f"[{status_color}]{status}[/{status_color}]",
                        )

                console.print(table)
                console.print()  # Add blank line

            # Show ticker-level backtest results in a table
            console.print("\n[bold green]Ticker-Level Backtest Results[/bold green]")

            # Check if we have train/test results
            has_train_test = any("train_results" in backtest for backtest in results["backtesting"])

            if has_train_test:
                # Display train/test split results
                table = Table(title="Ticker-Level Backtest Results (Train/Test Split)")
                table.add_column("Ticker", style="cyan", no_wrap=True)
                table.add_column("Strategy", style="yellow", no_wrap=True)
                table.add_column("Train Return", style="green", justify="right")
                table.add_column("Test Return", style="green", justify="right")
                table.add_column("Train Sharpe", style="blue", justify="right")
                table.add_column("Test Sharpe", style="blue", justify="right")
                table.add_column("Test Trades", style="white", justify="right")
                table.add_column("Test Win Rate", style="magenta", justify="right")

                for backtest in results["backtesting"]:
                    if "train_results" in backtest:
                        train_return_str = f"{backtest['train_results']['return_pct']:+.2f}%"
                        test_return_str = f"{backtest['test_results']['return_pct']:+.2f}%"
                        train_sharpe_str = f"{backtest['train_results']['sharpe_ratio']:.2f}"
                        test_sharpe_str = f"{backtest['test_results']['sharpe_ratio']:.2f}"
                        test_trades_str = str(backtest["test_results"]["num_trades"])

                        if backtest["test_results"]["win_rate"] is None or pd.isna(
                            backtest["test_results"]["win_rate"]
                        ):
                            test_win_rate_str = "N/A"
                        else:
                            test_win_rate_str = f"{backtest['test_results']['win_rate']:.1f}%"

                        table.add_row(
                            backtest["ticker"],
                            backtest["strategy"].upper(),
                            train_return_str,
                            test_return_str,
                            train_sharpe_str,
                            test_sharpe_str,
                            test_trades_str,
                            test_win_rate_str,
                        )
                    else:
                        # Fallback for strategies without train/test split
                        return_str = f"{backtest['return_pct']:+.2f}%"
                        sharpe_str = f"{backtest['sharpe_ratio']:.2f}"
                        trades_str = str(backtest["num_trades"])

                        if backtest["win_rate"] is None:
                            win_rate_str = "N/A"
                        else:
                            win_rate_str = f"{backtest['win_rate']:.1f}%"

                        table.add_row(
                            backtest["ticker"],
                            backtest["strategy"].upper(),
                            return_str,
                            return_str,  # Same for both train/test
                            sharpe_str,
                            sharpe_str,  # Same for both train/test
                            trades_str,
                            win_rate_str,
                        )

                console.print(table)
                console.print()  # Add blank line

                # Show train/test periods
                first_with_split = next((b for b in results["backtesting"] if "train_period" in b), None)
                if first_with_split:
                    console.print("[bold cyan]Data Periods:[/bold cyan]")
                    train_start = first_with_split["train_period"]["start"]
                    train_end = first_with_split["train_period"]["end"]
                    train_days = first_with_split["train_period"]["days"]
                    test_start = first_with_split["test_period"]["start"]
                    test_end = first_with_split["test_period"]["end"]
                    test_days = first_with_split["test_period"]["days"]

                    console.print(f"  Training: {train_start} to {train_end} ({train_days} days)")
                    console.print(f"  Testing:  {test_start} to {test_end} ({test_days} days)")
                    console.print()
            else:
                # Display traditional results without train/test split
                table = Table(title="Ticker-Level Backtest Results")
                table.add_column("Ticker", style="cyan", no_wrap=True)
                table.add_column("Strategy", style="yellow", no_wrap=True)
                table.add_column("Return", style="green", justify="right")
                table.add_column("Sharpe Ratio", style="blue", justify="right")
                table.add_column("Max Drawdown", style="red", justify="right")
                table.add_column("Trades", style="white", justify="right")
                table.add_column("Win Rate", style="magenta", justify="right")

                for backtest in results["backtesting"]:
                    return_str = f"{backtest['return_pct']:+.2f}%"
                    sharpe_str = f"{backtest['sharpe_ratio']:.2f}"
                    drawdown_str = f"{backtest['max_drawdown_pct']:.2f}%"
                    trades_str = str(backtest["num_trades"])

                    if backtest["win_rate"] is None:
                        win_rate_str = "N/A"
                    else:
                        win_rate_str = f"{backtest['win_rate']:.1f}%"

                    table.add_row(
                        backtest["ticker"],
                        backtest["strategy"].upper(),
                        return_str,
                        sharpe_str,
                        drawdown_str,
                        trades_str,
                        win_rate_str,
                    )

                console.print(table)
                console.print()  # Add blank line

            # Show summary message about strategies and stocks
            unique_tickers = {b["ticker"] for b in results["backtesting"]}
            console.print(
                f"Running [bold]{len(strategies)}[/bold] strategies across [bold]{len(unique_tickers)}[/bold] stocks..."
            )
            if len(strategies) > 1:
                console.print("Detailed results will be shown per strategy below.")

        if "forecasting" in results:
            console.print("\n[bold purple]=== Forecasting Results ===[/bold purple]")

            # Get date range from first non-error forecast
            date_info = ""
            for forecast in results["forecasting"]:
                if "error" not in forecast and "start_date" in forecast:
                    date_info = f" ({forecast['start_date']} to {forecast['end_date']})"
                    break

            table = Table(title=f"Price Forecasts{date_info}")
            table.add_column("Ticker", style="cyan", no_wrap=True)
            table.add_column("Current Price", style="white", justify="right")
            table.add_column("Forecast Price", style="green", justify="right")
            table.add_column("Return %", style="magenta", justify="right")
            table.add_column("Confidence Range", style="yellow", justify="center")
            table.add_column("Best Model", style="blue")

            # Sort forecasts by return percentage (highest to lowest)
            # Separate error results from valid forecasts
            error_forecasts = [f for f in results["forecasting"] if "error" in f]
            valid_forecasts = [f for f in results["forecasting"] if "error" not in f]

            # Calculate return percentage for sorting
            for forecast in valid_forecasts:
                forecast["return_pct"] = (
                    (forecast["forecast_price"] - forecast["current_price"]) / forecast["current_price"]
                ) * 100

            # Sort valid forecasts by return percentage (highest to lowest)
            sorted_forecasts = sorted(valid_forecasts, key=lambda f: f["return_pct"], reverse=True)

            # Combine sorted valid forecasts with error forecasts at the end
            all_forecasts = sorted_forecasts + error_forecasts

            for forecast in all_forecasts:
                if "error" in forecast:
                    table.add_row(
                        forecast["ticker"],
                        "[red]Error[/red]",
                        "[red]Error[/red]",
                        "[red]Error[/red]",
                        "[red]Error[/red]",
                        f"[red]{forecast['error']}[/red]",
                    )
                else:
                    current_price = forecast["current_price"]
                    forecast_price = forecast["forecast_price"]

                    # Calculate return percentage
                    return_pct = ((forecast_price - current_price) / current_price) * 100

                    # Color code forecast based on direction
                    forecast_color = (
                        "green"
                        if forecast_price > current_price
                        else "red"
                        if forecast_price < current_price
                        else "white"
                    )
                    forecast_str = f"[{forecast_color}]${forecast_price:.2f}[/{forecast_color}]"

                    # Format return percentage with color
                    return_str = f"[{forecast_color}]{return_pct:+.2f}%[/{forecast_color}]"

                    table.add_row(
                        forecast["ticker"],
                        f"${current_price:.2f}",
                        forecast_str,
                        return_str,
                        f"${forecast['lower_bound']:.2f} - ${forecast['upper_bound']:.2f}",
                        forecast["best_model"],
                    )

            console.print(table)

            # Display evaluation metrics if available
            has_evaluation = any("evaluation" in f for f in results["forecasting"] if "error" not in f)
            if has_evaluation:
                console.print("\n[bold cyan]=== Forecast Evaluation Metrics ===[/bold cyan]")

                eval_table = Table(title="Model Performance on Test Data")
                eval_table.add_column("Ticker", style="cyan", no_wrap=True)
                eval_table.add_column("RMSE", style="yellow", justify="right")
                eval_table.add_column("MAE", style="yellow", justify="right")
                eval_table.add_column("MAPE %", style="yellow", justify="right")
                eval_table.add_column("Train Period", style="white")
                eval_table.add_column("Test Period", style="white")

                # Use the same sorted order as the forecast table
                for forecast in all_forecasts:
                    if "error" not in forecast and "evaluation" in forecast:
                        eval_metrics = forecast["evaluation"]
                        train_period = forecast.get("train_period", {})
                        test_period = forecast.get("test_period", {})

                        train_str = f"{train_period.get('start', 'N/A')} to {train_period.get('end', 'N/A')}"
                        test_str = f"{test_period.get('start', 'N/A')} to {test_period.get('end', 'N/A')}"

                        eval_table.add_row(
                            forecast["ticker"],
                            f"${eval_metrics['rmse']:.2f}",
                            f"${eval_metrics['mae']:.2f}",
                            f"{eval_metrics['mape']:.2f}%",
                            train_str,
                            test_str,
                        )

                console.print(eval_table)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Stockula Trading Platform")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file (YAML)")
    parser.add_argument("--ticker", "-t", type=str, help="Override ticker symbol (single ticker mode)")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["all", "ta", "backtest", "forecast"],
        default="all",
        help="Operation mode",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["console", "json"],
        default="console",
        help="Output format",
    )
    parser.add_argument("--save-config", type=str, help="Save current configuration to file")

    # Add date range arguments
    parser.add_argument("--train-start", type=str, help="Training start date (YYYY-MM-DD)")
    parser.add_argument("--train-end", type=str, help="Training end date (YYYY-MM-DD)")
    parser.add_argument("--test-start", type=str, help="Testing start date (YYYY-MM-DD)")
    parser.add_argument("--test-end", type=str, help="Testing end date (YYYY-MM-DD)")

    args = parser.parse_args()

    # Initialize DI container first
    container = create_container(args.config)

    # Load configuration - the container will handle this
    config = container.stockula_config()

    # Set up logging based on configuration
    setup_logging(config, logging_manager=container.logging_manager())

    # Override ticker if provided
    if args.ticker:
        from .config import TickerConfig

        config.portfolio.tickers = [TickerConfig(symbol=args.ticker, quantity=1.0)]
        # Disable auto-allocation for single ticker mode since we don't have categories
        config.portfolio.auto_allocate = False
        config.portfolio.dynamic_allocation = False
        config.portfolio.allocation_method = "equal_weight"
        # Allow 100% position for single ticker mode
        config.portfolio.max_position_size = 100.0

    # Override date ranges if provided
    if args.train_start:
        config.forecast.train_start_date = datetime.strptime(args.train_start, "%Y-%m-%d").date()
    if args.train_end:
        config.forecast.train_end_date = datetime.strptime(args.train_end, "%Y-%m-%d").date()
    if args.test_start:
        config.forecast.test_start_date = datetime.strptime(args.test_start, "%Y-%m-%d").date()
    if args.test_end:
        config.forecast.test_end_date = datetime.strptime(args.test_end, "%Y-%m-%d").date()

    # Save configuration if requested
    if args.save_config:
        from .config.settings import save_config

        save_config(config, args.save_config)
        print(f"Configuration saved to {args.save_config}")
        return

    # Get injected services from container
    factory = container.domain_factory()
    portfolio = factory.create_portfolio(config)

    # Display portfolio summary with Rich
    portfolio_table = Table(title="Portfolio Summary")
    portfolio_table.add_column("Property", style="cyan", no_wrap=True)
    portfolio_table.add_column("Value", style="white")

    portfolio_table.add_row("Name", portfolio.name)
    portfolio_table.add_row("Initial Capital", f"${portfolio.initial_capital:,.2f}")
    portfolio_table.add_row("Total Assets", str(len(portfolio.get_all_assets())))
    portfolio_table.add_row("Allocation Method", portfolio.allocation_method)

    console.print(portfolio_table)

    # Display detailed portfolio holdings
    holdings_table = Table(title="Portfolio Holdings")
    holdings_table.add_column("Ticker", style="cyan", no_wrap=True)
    holdings_table.add_column("Type", style="yellow")
    holdings_table.add_column("Quantity", style="green", justify="right")

    all_assets = portfolio.get_all_assets()
    for asset in all_assets:
        # Get symbol as string
        symbol = asset.symbol if hasattr(asset, "symbol") else "N/A"

        # Get category name as string
        category_name = "N/A"
        if hasattr(asset, "category") and asset.category is not None:
            if hasattr(asset.category, "name"):
                category_name = str(asset.category.name)
            else:
                category_name = str(asset.category)

        # Handle quantity formatting - check if it's a real number
        quantity_str = "N/A"
        if hasattr(asset, "quantity") and isinstance(asset.quantity, int | float):
            quantity_str = f"{asset.quantity:.2f}"
        elif hasattr(asset, "quantity"):
            # Try to convert to float if possible
            try:
                quantity_str = f"{float(asset.quantity):.2f}"
            except (TypeError, ValueError):
                quantity_str = str(asset.quantity)

        holdings_table.add_row(symbol, category_name, quantity_str)

    console.print(holdings_table)

    # Get portfolio value at start of backtest period
    fetcher = container.data_fetcher()
    symbols = [asset.symbol for asset in portfolio.get_all_assets()]

    # Get prices at the start date if backtesting
    if args.mode in ["all", "backtest"] and config.data.start_date:
        log_manager.debug(f"\nFetching prices at start date ({config.data.start_date})...")
        start_date_str = date_to_string(config.data.start_date)
        # Fetch one day of data at the start date to get opening prices
        start_prices = {}
        for symbol in symbols:
            try:
                data = fetcher.get_stock_data(symbol, start=start_date_str, end=start_date_str)
                if not data.empty:
                    start_prices[symbol] = data["Close"].iloc[0]
                else:
                    # If no data on exact date, get the next available date
                    if isinstance(config.data.start_date, str):
                        # Convert string to date for timedelta calculation
                        start_dt = pd.to_datetime(config.data.start_date)
                        end_date = (start_dt + timedelta(days=7)).strftime("%Y-%m-%d")
                    else:
                        end_date = (config.data.start_date + timedelta(days=7)).strftime("%Y-%m-%d")
                    data = fetcher.get_stock_data(symbol, start=start_date_str, end=end_date)
                    if not data.empty:
                        start_prices[symbol] = data["Close"].iloc[0]
            except Exception as e:
                log_manager.warning(f"Could not get start price for {symbol}: {e}")

        initial_portfolio_value = portfolio.get_portfolio_value(start_prices)
        log_manager.info(f"\nPortfolio Value at Start Date: ${initial_portfolio_value:,.2f}")
    else:
        log_manager.debug("\nFetching current prices...")
        current_prices = fetcher.get_current_prices(symbols, show_progress=True)
        initial_portfolio_value = portfolio.get_portfolio_value(current_prices)

    # Calculate returns (always needed, not just for logging)
    initial_return = initial_portfolio_value - portfolio.initial_capital
    initial_return_pct = (initial_return / portfolio.initial_capital) * 100

    log_manager.info(f"Initial Capital: ${portfolio.initial_capital:,.2f}")
    log_manager.info(f"Return Since Inception: ${initial_return:,.2f} ({initial_return_pct:+.2f}%)")

    # Run operations
    results = {
        "initial_portfolio_value": initial_portfolio_value,
        "initial_capital": portfolio.initial_capital,
    }

    # Get all assets from portfolio
    all_assets = portfolio.get_all_assets()

    # Separate tradeable and hold-only assets
    # Get hold-only categories from config
    hold_only_category_names = set(config.backtest.hold_only_categories)
    hold_only_categories = set()
    for category_name in hold_only_category_names:
        try:
            hold_only_categories.add(Category[category_name])
        except KeyError:
            log_manager.warning(f"Unknown category '{category_name}' in hold_only_categories")

    tradeable_assets = []
    hold_only_assets = []

    for asset in all_assets:
        if asset.category in hold_only_categories:
            hold_only_assets.append(asset)
        else:
            tradeable_assets.append(asset)

    if hold_only_assets:
        log_manager.info("\nHold-only assets (excluded from backtesting):")
        for asset in hold_only_assets:
            log_manager.info(f"  {asset.symbol} ({asset.category})")

    # Get ticker symbols for processing
    ticker_symbols = [asset.symbol for asset in all_assets]

    # Determine what operations will be performed
    will_backtest = args.mode in ["all", "backtest"]
    will_forecast = args.mode in ["all", "forecast"]

    # Create appropriate progress display
    if will_backtest or will_forecast:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            # Show forecast warning if needed
            if will_forecast:
                # Determine forecast mode message
                if config.forecast.forecast_length is not None:
                    forecast_msg = f"• Forecasting {config.forecast.forecast_length} days into the future"
                elif config.forecast.test_start_date and config.forecast.test_end_date:
                    forecast_msg = (
                        f"• Evaluating forecast on test period: "
                        f"{config.forecast.test_start_date} to {config.forecast.test_end_date}"
                    )
                else:
                    forecast_msg = "• Forecast configuration error: neither forecast_length nor test dates specified"

                console.print(
                    Panel.fit(
                        f"[bold yellow]FORECAST MODE - IMPORTANT NOTES:[/bold yellow]\n"
                        f"{forecast_msg}\n"
                        f"• AutoTS will try multiple models to find the best fit\n"
                        f"• This process may take several minutes per ticker\n"
                        f"• Press Ctrl+C at any time to cancel\n"
                        f"• Enable logging for more detailed progress information",
                        border_style="yellow",
                    )
                )

            # Create progress tasks
            if will_backtest:
                # Count tradeable assets for backtesting
                tradeable_count = len([a for a in all_assets if a.category not in hold_only_categories])
                if tradeable_count > 0:
                    num_strategies = len(config.backtest.strategies)
                    backtest_task = progress.add_task(
                        f"[green]Backtesting {num_strategies} strategies across {tradeable_count} stocks...",
                        total=tradeable_count * num_strategies,
                    )
                else:
                    backtest_task = None

            # Process each ticker with progress tracking
            for _ticker_idx, ticker in enumerate(ticker_symbols):
                log_manager.debug(f"\nProcessing {ticker}...")

                # Get the asset to check its category
                asset = next((a for a in all_assets if a.symbol == ticker), None)
                is_hold_only = asset and asset.category in hold_only_categories

                if args.mode in ["all", "ta"]:
                    if "technical_analysis" not in results:
                        results["technical_analysis"] = []
                    # Show progress for TA when it's the only operation or when running all
                    show_ta_progress = args.mode == "ta" or not will_backtest and not will_forecast
                    results["technical_analysis"].append(
                        run_technical_analysis(
                            ticker,
                            config,
                            data_fetcher=container.data_fetcher(),
                            show_progress=show_ta_progress,
                        )
                    )

                if will_backtest and not is_hold_only:
                    if "backtesting" not in results:
                        results["backtesting"] = []

                    # Update progress for each strategy
                    for _strategy_idx, strategy_config in enumerate(config.backtest.strategies):
                        progress.update(
                            backtest_task,
                            description=f"[green]Backtesting {strategy_config.name.upper()} on {ticker}...",
                        )

                        # Run single strategy backtest
                        strategy_class = get_strategy_class(strategy_config.name)
                        if strategy_class:
                            # Set strategy parameters if provided
                            if strategy_config.parameters:
                                for key, value in strategy_config.parameters.items():
                                    setattr(strategy_class, key, value)

                            try:
                                runner = container.backtest_runner()
                                # Determine which dates to use for backtesting
                                backtest_start = None
                                backtest_end = None

                                # First check if backtest has specific dates
                                if config.backtest.start_date and config.backtest.end_date:
                                    backtest_start = date_to_string(config.backtest.start_date)
                                    backtest_end = date_to_string(config.backtest.end_date)
                                # Fall back to general data dates
                                elif config.data.start_date and config.data.end_date:
                                    backtest_start = date_to_string(config.data.start_date)
                                    backtest_end = date_to_string(config.data.end_date)

                                backtest_result = runner.run_from_symbol(
                                    ticker,
                                    strategy_class,
                                    start_date=backtest_start,
                                    end_date=backtest_end,
                                )

                                # Handle NaN values for win rate when there are no trades
                                win_rate = backtest_result.get("Win Rate [%]", 0)
                                if pd.isna(win_rate):
                                    win_rate = None if backtest_result["# Trades"] == 0 else 0

                                result_entry = {
                                    "ticker": ticker,
                                    "strategy": strategy_config.name,
                                    "parameters": strategy_config.parameters,
                                    "return_pct": backtest_result["Return [%]"],
                                    "sharpe_ratio": backtest_result["Sharpe Ratio"],
                                    "max_drawdown_pct": backtest_result["Max. Drawdown [%]"],
                                    "num_trades": backtest_result["# Trades"],
                                    "win_rate": win_rate,
                                }

                                # Add dates if available
                                if "Start Date" in backtest_result:
                                    result_entry["start_date"] = backtest_result["Start Date"]
                                if "End Date" in backtest_result:
                                    result_entry["end_date"] = backtest_result["End Date"]

                                results["backtesting"].append(result_entry)
                            except Exception as e:
                                console.print(f"[red]Error backtesting {strategy_config.name} on {ticker}: {e}[/red]")

                        # Advance progress
                        if backtest_task is not None:
                            progress.advance(backtest_task)

                # Note: This section is now handled by parallel forecasting below
                pass

            # Run sequential forecasting if needed
            if will_forecast and ticker_symbols:
                console.print("\n[bold blue]Starting sequential forecasting...[/bold blue]")
                console.print(
                    f"[dim]Configuration: max_generations={config.forecast.max_generations}, "
                    f"num_validations={config.forecast.num_validations}[/dim]"
                )

                # Create a separate progress display for sequential forecasting
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=console,
                    transient=True,
                ) as forecast_progress:
                    forecast_task = forecast_progress.add_task(
                        f"[blue]Forecasting {len(ticker_symbols)} tickers...",
                        total=len(ticker_symbols),
                    )

                    # Run sequential forecasting

                    # Initialize results
                    results["forecasting"] = []

                    # Process each ticker sequentially
                    for idx, symbol in enumerate(ticker_symbols, 1):
                        forecast_progress.update(
                            forecast_task,
                            description=f"[blue]Forecasting {symbol} ({idx}/{len(ticker_symbols)})...",
                        )

                        try:
                            # Check if test dates are provided for evaluation
                            if config.forecast.test_start_date and config.forecast.test_end_date:
                                # Use the new evaluation method
                                forecast_result = run_forecast_with_evaluation(
                                    symbol, config, container.stock_forecaster()
                                )
                            else:
                                # Use the original method
                                forecast_result = run_forecast(symbol, config, container.stock_forecaster())

                            results["forecasting"].append(forecast_result)

                            # Update progress to show completion
                            forecast_progress.update(
                                forecast_task,
                                description=f"[green]✅ Forecasted {symbol}[/green] ({idx}/{len(ticker_symbols)})",
                            )

                        except KeyboardInterrupt:
                            if log_manager:
                                log_manager.warning(f"Forecast for {symbol} interrupted by user")
                            results["forecasting"].append({"ticker": symbol, "error": "Interrupted by user"})
                            break
                        except Exception as e:
                            if log_manager:
                                log_manager.error(f"Error forecasting {symbol}: {e}")
                            results["forecasting"].append({"ticker": symbol, "error": str(e)})

                            # Update progress to show error
                            forecast_progress.update(
                                forecast_task,
                                description=f"[red]❌ Failed {symbol}[/red] ({idx}/{len(ticker_symbols)})",
                            )

                        # Advance progress
                        forecast_progress.advance(forecast_task)

                    # Mark progress as complete
                    forecast_progress.update(
                        forecast_task,
                        description="[green]Forecasting complete!",
                    )
    else:
        # No progress bars needed for TA only
        for ticker in ticker_symbols:
            log_manager.debug(f"\nProcessing {ticker}...")

            # Get the asset to check its category
            asset = next((a for a in all_assets if a.symbol == ticker), None)
            is_hold_only = asset and asset.category in hold_only_categories

            if args.mode in ["all", "ta"]:
                if "technical_analysis" not in results:
                    results["technical_analysis"] = []
                # Always show progress for standalone TA mode
                results["technical_analysis"].append(
                    run_technical_analysis(
                        ticker,
                        config,
                        data_fetcher=container.data_fetcher(),
                        show_progress=True,
                    )
                )

    # Show current portfolio value for forecast mode after all processing is complete
    if args.mode == "forecast":
        # Show portfolio value in a nice table
        portfolio_value_table = Table(title="Portfolio Value")
        portfolio_value_table.add_column("Metric", style="cyan", no_wrap=True)
        portfolio_value_table.add_column("Date", style="white")
        portfolio_value_table.add_column("Value", style="green")

        # Add initial capital row with appropriate date
        if config.forecast.test_start_date:
            # Historical evaluation mode - use test start date
            test_start = date_to_string(config.forecast.test_start_date)
        else:
            # Future prediction mode - use today's date
            test_start = datetime.now().strftime("%Y-%m-%d")
        portfolio_value_table.add_row("Observed Value", test_start, f"${portfolio.initial_capital:,.2f}")

        # Calculate forecasted portfolio value based on forecast results
        if "forecasting" in results and results["forecasting"]:
            forecasted_value = portfolio.initial_capital
            total_accuracy = 0
            valid_forecasts = 0

            # Check if we're in evaluation mode (have evaluation metrics)
            is_evaluation_mode = any("evaluation" in f for f in results["forecasting"] if "error" not in f)

            for forecast in results["forecasting"]:
                if "error" not in forecast:
                    ticker = forecast["ticker"]
                    asset = next(
                        (a for a in portfolio.get_all_assets() if a.symbol == ticker),
                        None,
                    )
                    if asset:
                        # Get the asset's current value
                        asset_value = asset.quantity * forecast["current_price"]

                        # Calculate the forecasted change
                        forecast_change = (forecast["forecast_price"] - forecast["current_price"]) / forecast[
                            "current_price"
                        ]

                        # Apply the change to the portfolio value
                        forecasted_value += asset_value * forecast_change

                        # If in evaluation mode, track accuracy
                        if "evaluation" in forecast:
                            accuracy = 100 - forecast["evaluation"]["mape"]
                            total_accuracy += accuracy
                            valid_forecasts += 1

            # Add forecasted value row with appropriate end date
            test_end = None
            if config.forecast.test_end_date:
                test_end = date_to_string(config.forecast.test_end_date)
            else:
                # Try to get end date from any forecast result
                for forecast in results["forecasting"]:
                    if "error" not in forecast and "end_date" in forecast:
                        test_end = forecast["end_date"]
                        break

            if test_end:
                portfolio_value_table.add_row("Predicted Value", test_end, f"${forecasted_value:,.2f}")

            # Add average accuracy row only for evaluation mode
            if is_evaluation_mode and valid_forecasts > 0 and test_end:
                avg_accuracy = total_accuracy / valid_forecasts
                portfolio_value_table.add_row("Accuracy", test_end, f"{avg_accuracy:.4f}%")

        console.print(portfolio_value_table)

    # Output results
    output_format = args.output or config.output.get("format", "console")
    print_results(results, output_format, config, container)

    # Show strategy-specific summaries after backtesting
    if args.mode in ["all", "backtest"] and "backtesting" in results:
        # Group results by strategy
        from collections import defaultdict

        strategy_results = defaultdict(list)

        for backtest in results["backtesting"]:
            strategy_results[backtest["strategy"]].append(backtest)

        # Only proceed if we have results
        if not strategy_results:
            console.print("\n[red]No backtesting results to display.[/red]")
            return

        # Create structured backtest results
        portfolio_backtest_results = create_portfolio_backtest_results(results, config, strategy_results)

        # Ticker-level results already shown in print_results() above

        # Sort strategy summaries by return during period (highest to lowest)
        sorted_summaries = sorted(
            portfolio_backtest_results.strategy_summaries,
            key=lambda s: (s.final_portfolio_value - s.initial_portfolio_value),
            reverse=True,  # Highest returns first
        )

        # Show summary for each strategy using structured data
        for strategy_summary in sorted_summaries:
            # Get broker config info
            broker_info = ""
            if config.backtest.broker_config:
                broker_config = config.backtest.broker_config
                if broker_config.name in [
                    "td_ameritrade",
                    "etrade",
                    "robinhood",
                    "fidelity",
                    "schwab",
                ]:
                    broker_info = f"Broker: {broker_config.name} (zero-commission)"
                elif broker_config.commission_type == "percentage":
                    broker_info = (
                        f"Broker: {broker_config.name} ({broker_config.commission_value * 100:.1f}% commission"
                    )
                    if broker_config.min_commission:
                        broker_info += f", ${broker_config.min_commission:.2f} min"
                    broker_info += ")"
                elif broker_config.commission_type == "per_share":
                    per_share_comm = broker_config.per_share_commission or broker_config.commission_value
                    broker_info = f"Broker: {broker_config.name} (${per_share_comm:.3f}/share"
                    if broker_config.min_commission:
                        broker_info += f", ${broker_config.min_commission:.2f} min"
                    broker_info += ")"
                elif broker_config.commission_type == "tiered":
                    broker_info = f"Broker: {broker_config.name} (tiered pricing"
                    if broker_config.min_commission:
                        broker_info += f", ${broker_config.min_commission:.2f} min"
                    broker_info += ")"
                elif broker_config.commission_type == "fixed":
                    broker_info = f"Broker: {broker_config.name} (${broker_config.commission_value:.2f}/trade)"
                else:
                    broker_info = f"Broker: {broker_config.name} ({broker_config.commission_type})"
            else:
                broker_info = f"Commission: {config.backtest.commission * 100:.1f}%"

            # Create rich panel for strategy summary
            period_return = strategy_summary.final_portfolio_value - strategy_summary.initial_portfolio_value
            period_return_color = "green" if period_return > 0 else "red" if period_return < 0 else "white"

            # Format dates - try multiple sources
            start_date: str = "N/A"
            end_date: str = "N/A"

            # First try backtest dates, then data dates, then results
            if config.backtest.start_date:
                start_date = date_to_string(config.backtest.start_date)
            elif config.data.start_date:
                start_date = date_to_string(config.data.start_date)
            elif portfolio_backtest_results.date_range and portfolio_backtest_results.date_range.get("start"):
                start_date = portfolio_backtest_results.date_range["start"]

            if config.backtest.end_date:
                end_date = date_to_string(config.backtest.end_date)
            elif config.data.end_date:
                end_date = date_to_string(config.data.end_date)
            elif portfolio_backtest_results.date_range and portfolio_backtest_results.date_range.get("end"):
                end_date = portfolio_backtest_results.date_range["end"]

            summary_content = f"""Start: {start_date}
End:   {end_date}

Parameters: {strategy_summary.parameters if strategy_summary.parameters else "Default"}
{broker_info}

Portfolio Value at {start_date}: ${strategy_summary.initial_portfolio_value:,.2f}
Portfolio Value at {end_date}: ${strategy_summary.final_portfolio_value:,.2f}

Strategy Performance:
  Average Return: [{period_return_color}]{strategy_summary.average_return_pct:+.2f}%[/{period_return_color}]
  Winning Stocks: {strategy_summary.winning_stocks}
  Losing Stocks: {strategy_summary.losing_stocks}
  Total Trades: {strategy_summary.total_trades}

Return During Period: [{period_return_color}]${period_return:,.2f} \
({strategy_summary.total_return_pct:+.2f}%)[/{period_return_color}]

Detailed report saved to: {
                save_detailed_report(
                    strategy_summary.strategy_name,
                    [r.model_dump() for r in strategy_summary.detailed_results],
                    results,
                    config,
                )
            }"""

            console.print(
                Panel(
                    summary_content,
                    title=f" STRATEGY: {strategy_summary.strategy_name.upper()} ",
                    border_style="white",
                    padding=(0, 1),
                )
            )

        # Exit after showing strategy summaries
        return

        # Re-fetch current prices to get the most up-to-date values
        log_manager.debug("\nFetching latest prices...")
        final_prices = fetcher.get_current_prices(symbols, show_progress=True)
        final_value = portfolio.get_portfolio_value(final_prices)

        print(f"""
Portfolio Value at Start Date: ${results["initial_portfolio_value"]:,.2f}
Portfolio Value at End (Current): ${final_value:,.2f}""")

        period_return = final_value - results["initial_portfolio_value"]
        period_return_pct = (period_return / results["initial_portfolio_value"]) * 100

        # Show category breakdown if available
        category_allocations = portfolio.get_allocation_by_category(final_prices)
        if category_allocations:
            print("\nAllocation by Category:")
            for category, data in sorted(category_allocations.items(), key=lambda x: x[1]["value"], reverse=True):
                print(f"  {category}: ${data['value']:,.2f} ({data['percentage']:.1f}%)")

        # Show performance breakdown by category
        if args.mode in ["all", "backtest"] and config.data.start_date:
            start_category_allocations = portfolio.get_allocation_by_category(start_prices)
            final_category_allocations = portfolio.get_allocation_by_category(final_prices)

            print("\nPerformance Breakdown By Category:")
            for category in final_category_allocations.keys():
                if category in start_category_allocations:
                    start_value = start_category_allocations[category]["value"]
                    final_value = final_category_allocations[category]["value"]
                    category_return = final_value - start_value
                    category_return_pct = (category_return / start_value) * 100 if start_value > 0 else 0

                    print(f"""  {category}:
    Start Value: ${start_value:,.2f}
    Current Value: ${final_value:,.2f}
    Return: ${category_return:,.2f} ({category_return_pct:+.2f}%)
    Assets: {", ".join(final_category_allocations[category]["assets"])}""")
                else:
                    # New category added during the period
                    final_value = final_category_allocations[category]["value"]
                    print(f"""  {category}:
    Start Value: $0.00 (new category)
    Current Value: ${final_value:,.2f}
    Assets: {", ".join(final_category_allocations[category]["assets"])}""")

        # Show performance breakdown by asset type
        if hold_only_assets and tradeable_assets:
            print("\nAsset Type Breakdown:")

            # Calculate hold-only assets value
            hold_only_value = sum(asset.get_value(final_prices.get(asset.symbol, 0)) for asset in hold_only_assets)

            # Calculate tradeable assets value
            tradeable_value = sum(asset.get_value(final_prices.get(asset.symbol, 0)) for asset in tradeable_assets)

            print(f"""  Hold-only Assets: ${hold_only_value:,.2f}
  Tradeable Assets: ${tradeable_value:,.2f}
  Total Portfolio: ${hold_only_value + tradeable_value:,.2f}""")

        # Calculate and show total trades from backtesting results
        total_trades = 0
        if "backtesting" in results:
            total_trades = sum(backtest.get("num_trades", 0) for backtest in results["backtesting"])
            print(f"\nTotal Trades Executed: {total_trades}")

        # Show return during period at the very end
        print(f"Return During Period: ${period_return:,.2f} ({period_return_pct:+.2f}%)")

    # Save results if configured
    if config.output.get("save_results", False):
        results_dir = Path(config.output.get("results_dir", "./results"))
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"stockula_results_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        log_manager.info(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
