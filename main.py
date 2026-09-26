import argparse
from analyzer import CrossoverAnalyzer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?")
    parser.add_argument("start", nargs="?", help="YYYY-MM-DD")
    parser.add_argument("end", nargs="?", help="YYYY-MM-DD")
    parser.add_argument("--short", type=int, default=20)
    parser.add_argument("--long", type=int, default=50)
    parser.add_argument("--save", help="save the chart to a file instead of showing it")
    args = parser.parse_args()

    # if nothing was passed in just ask for it
    ticker = args.ticker or input("Ticker: ").strip()
    start = args.start or input("Start date (YYYY-MM-DD): ").strip()
    end = args.end or input("End date (YYYY-MM-DD): ").strip()

    analyzer = CrossoverAnalyzer(ticker, args.short, args.long)
    analyzer.load_prices(start, end)
    crosses = analyzer.find_crossovers()

    print(f"\n{analyzer.ticker}: {len(crosses)} crossovers\n")
    for date, row in crosses.iterrows():
        kind = "BULLISH" if row["Signal"] == 1 else "BEARISH"
        print(f"  {date.date()}  {kind:8}  close = ${row['Close']:.2f}")

    analyzer.plot(save_path=args.save)


if __name__ == "__main__":
    main()
