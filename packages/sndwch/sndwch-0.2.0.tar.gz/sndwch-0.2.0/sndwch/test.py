# 簡易文字列パターン操作 [sndwch]
# 【動作確認 / 使用例】

import sys
import ezpip
sndwch = ezpip.load_develop("sndwch", "../", develop_flag = True)

# 所定の文字列で挟まれた部分を全て取得 [sndwch]
results = sndwch.get("a = {col='orange', col='green'}", "col='", "'")
print(results)

# 所定の文字列で挟まれた部分を全て置き換え [sndwch]
result = sndwch.rep(
	"a = {col='orange', col='green'}",	# 操作対象の文字列
	"col='", "'",	# 操作箇所を示すパターン (前方, 後方)
	lambda s: s.upper(),	# 操作関数
	outer = True,	# False: 引数・返値にpreとpostを含まない, True: 返値のみpreとpostを含む
)
print(result)
