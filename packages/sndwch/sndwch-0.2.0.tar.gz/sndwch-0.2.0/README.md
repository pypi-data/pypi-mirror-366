English description follows Japanese.

---

## 概要
- 正規表現よりも簡単な書き方で文字列のパターン的操作ができるツール

## 特徴
- 所定文字列で挟むことによって操作箇所を示す、正規表現よりも敢えて自由度が限定された「Sandwitch Method」に基づく
- この限定により、パターンマッチで頻出の「"」などの記号のエスケープが不要になる
- 文字列操作で頻出の最短一致がデフォルトになっている

## 使い方
```python
import sndwch

# 所定の文字列で挟まれた部分を全て取得 [sndwch]
results = sndwch.get("a = {col='orange', col='green'}", "col='", "'")
print(results)	# -> ["orange", "green"]

# 所定の文字列で挟まれた部分を全て置き換え [sndwch]
result = sndwch.rep(
	"a = {col='orange', col='green'}",	# 操作対象の文字列
	"col='", "'",	# 操作箇所を示すパターン (前方, 後方)
	lambda s: s.upper(),	# 操作関数
	outer = False,	# False: 引数・返値にpreとpostを含まない, True: 返値のみpreとpostを含む
)
print(result)	# -> "a = {col='ORANGE', col='GREEN'}"
```

---

## Overview
- A tool that allows pattern-based string manipulation with a simpler syntax than regular expressions.

## Features
- Based on the deliberately restricted "Sandwich Method," where target segments are indicated by enclosing them with specified strings, offering less flexibility than regular expressions on purpose.
- This restriction eliminates the need to escape frequently occurring symbols (like `"`) in pattern matching.
- Shortest match (non-greedy matching) is the default behavior, which is common in string manipulation tasks.

## Usage
```python
import sndwch

# Retrieve all substrings enclosed by specified strings [sndwch]
results = sndwch.get("a = {col='orange', col='green'}", "col='", "'")
print(results)	# -> ["orange", "green"]

# Replace all substrings enclosed by specified strings [sndwch]
result = sndwch.rep(
	"a = {col='orange', col='green'}",	# Target string
	"col='", "'",	# Pattern indicating the target area (prefix, suffix)
	lambda s: s.upper(),	# Function to apply
	outer = False,	# False: pre and post are excluded in args & return value, True: included only in return value
)
print(result)	# -> "a = {col='ORANGE', col='GREEN'}"
```
