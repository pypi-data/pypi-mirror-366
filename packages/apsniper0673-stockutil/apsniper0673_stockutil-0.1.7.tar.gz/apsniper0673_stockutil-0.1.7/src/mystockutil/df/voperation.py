import pandas as pd
from pandas import Series
import numpy as np
from typing import List

"""
데이터프레임의 벡터화된 연산들을 정의한 모듈입니다.
df는 '일자'와 '종목코드'의 MultiIndex를 가지고 있는 경우를 Default로 가정합니다."""

def count(df:pd.DataFrame, reset:Series, reset_value:int=1, counting:Series=None, group_by:bool=True, groups:List[str]=['종목코드'])->pd.Series:
    """
    reset이 True일 때, 카운트는 reset_value로 초기화
    False일 때, 카운트에 counting을 더함"""
    df = df.copy()
    if group_by and groups == ['종목코드']:
        if counting is None:
            # df와 동일한 길이의 1로 이루어진 Series를 만듭니다.
            counting = Series(1, index=df.index)
        return _count_default(df=df, reset=reset, reset_value=reset_value, counting=counting)
    else:
        raise NotImplementedError("Not implemented yet.")
def _count_default(df:pd.DataFrame, reset:Series, reset_value:int, counting:Series)->pd.Series:
    """
    종목코드별로 카운트를 계산합니다."""
    df['counting'] = counting
    df['reset'] = reset
    df['카운트그룹'] = df.groupby('종목코드')['reset'].cumsum() # 카운트그룹은 0부터 시작함
    df['카운트'] = df.groupby(['종목코드', '카운트그룹'])['counting'].cumsum()
    return df['카운트']

def switch(df:pd.DataFrame, on:Series, off:Series, default_bool:bool=False, direction:bool=True, group_by:bool=True, groups:List[str]=['종목코드'])->pd.Series:
    """
    switch가 on인 경우에는 True값을 off가 될 때까지 유지
    제일 초기값은 False가 Default
    direction이 True면 ffll, False면 bfill
    """
    df = df.copy()
    if group_by and groups == ['종목코드']:
        return _switch_default(df=df, on=on, off=off, default_bool=default_bool, direction=direction)
    else:
        raise NotImplementedError("Not implemented yet.")

def _switch_default(df:pd.DataFrame, on:Series, off:Series, default_bool:bool, direction:bool)->pd.Series:
    """
    종목코드별로 스위치를 계산합니다."""
    df['on'] = on
    df['off'] = off
    df['switch'] = np.nan
    df['switch'] = df['switch'].mask(df['on'], True)
    df['switch'] = df['switch'].mask(df['off'], False)
    if direction:
        df['switch'] = df.groupby('종목코드')['switch'].ffill()
    else:
        df['switch'] = df.groupby('종목코드')['switch'].bfill()
    df['switch'] = df['switch'].fillna(default_bool)
    return df['switch'].astype(bool)