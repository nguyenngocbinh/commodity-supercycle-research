import requests
import pandas as pd

from src.data.imf import _parse_response


def test_imf_csv_response_parses_monthly_observations():
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "text/csv"
    response._content = (
        b"STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,REF_AREA,INDICATOR,"
        b"UNIT_MEASURE,FREQ,TIME_PERIOD,OBS_VALUE\n"
        b"data,PCPS,PCPS,I,G001,POILBRE,USD,M,2020-01,63.65\n"
        b"data,PCPS,PCPS,I,G001,POILBRE,USD,M,2020-02,55.66\n"
    )
    frame = _parse_response(response, "imf_brent")
    assert list(frame.columns) == ["imf_brent"]
    assert len(frame) == 2
    assert frame.index[0] == pd.Timestamp("2020-01-01")
    assert frame.iloc[0, 0] == 63.65
