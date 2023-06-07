import datetime as dt
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query

# Mocked trade data
mocked_trades = [
    {
        "trade_id": "1",
        "instrument_id": "TSLA",
        "instrument_name": "Tesla",
        "trade_date_time": dt.datetime(2022, 1, 1, 10, 30),
        "trade_details": {
            "buySellIndicator": "BUY",
            "price": 100.0,
            "quantity": 10
        },
        "trader": "John Doe"
    },
    
]


class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None,
                                       description="The asset class of the instrument traded.")
     counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with.")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded.")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails",
                                        description="The details of the trade, i.e. price, quantity")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")


# Initialize the FastAPI application
app = FastAPI()


@app.get("/trades", response_model=List[Trade])
def list_trades(page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    start_index = (page - 1) * size
    end_index = start_index + size
    return mocked_trades[start_index:end_index]


@app.get("/trades/{trade_id}", response_model=Trade)
def get_trade_by_id(trade_id: str):
    for trade in mocked_trades:
        if trade["trade_id"] == trade_id:
            return trade
    return {"message": "Trade not found"}

@app.get("/trades/search", response_model=List[Trade])
def search_trades(
        search: Optional[str] = Query(None, description="Search query"),
        counterparty: Optional[str] = Query(None, description="Counterparty"),
        instrumentName: Optional[str] = Query(None, alias="instrumentName", description="Instrument Name"),
        instrumentId: Optional[str] = Query(None, alias="instrumentId", description="Instrument ID"),
        trader: Optional[str] = Query(None, description="Trader")
):

    results = []
    trader: Optional[str] = Field(description="The name of the Trader")

    for trade in mocked_trades:
        if (
                (search and search.lower() in str(trade).lower()) or
                (counterparty and trade.get("counterparty") == counterparty) or
                (instrumentId and trade["instrument_id"] == instrumentId) or
                (instrumentName and trade["instrument_name"] == instrumentName) or
                (trader and trade["trader"] == trader)
        ):
            results.append(trade)
    return results


@app.get("/trades/filter", response_model=List[Trade])
def filter_trades(
        assetClass: Optional[str] = Query(None, description="Asset class of the trade"),
        start: Optional[dt.datetime] = Query(None, description="Minimum date for tradeDateTime"),
        end: Optional[dt.datetime] = Query(None, description="Maximum date for tradeDateTime"),
        minPrice: Optional[float] = Query(None, description="Minimum value for tradeDetails.price"),
        maxPrice: Optional[float] = Query(None, description="Maximum value for tradeDetails.price"),
        tradeType: Optional[str] = Query(None, description="BUY or SELL trade type")
):
    results = []
    for trade in mocked_trades:
        if (
                (assetClass and trade.get("asset_class") == assetClass) or
                (start and trade["trade_date_time"] >= start) or
                (end and trade["trade_date_time"] <= end) or
                (minPrice and trade["trade_details"]["price"] >= minPrice) or
                (maxPrice and trade["trade_details"]["price"] <= maxPrice) or
                (tradeType and trade["trade_details"]["buySellIndicator"] == tradeType)
        ):
            results.append(trade)
    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
