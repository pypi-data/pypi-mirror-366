# 簡易文字列パターン操作 [sndwch]

import sys

# 所定の文字列で挟まれた部分を全て取得 [sndwch]
def get(
	target,	# 操作対象の文字列
	pre,	# 操作箇所を示すパターン (前方)
	post,	# 操作箇所を示すパターン (後方)
	outer = False,	# False: preとpostを含まない, True: 含む
):
	ls = target.split(pre)
	ret_ls = []
	for e in ls[1:]:
		if post not in e: continue
		one_res = e.split(post)[0]
		if outer is True: one_res = pre + one_res + post
		ret_ls.append(one_res)
	return ret_ls

# 所定の文字列で挟まれた部分を全て置き換え [sndwch]
def rep(
	target,	# 操作対象の文字列
	pre, post,	# 操作箇所を示すパターン (前方, 後方)
	f,	# 操作関数
	outer = False,	# False: 引数・返値にpreとpostを含まない, True: 返値のみpreとpostを含む
):
	ls = target.split(pre)
	ret_ls = [ls[0]]
	for part in ls[1:]:
		# postがないときは素通し
		if post not in part:
			ret_ls.append(pre + part)
			continue
		# postがある場合
		ls2 = part.split(post)
		if outer is True:
			one_res = f(ls2[0])
		else:
			one_res = pre + f(ls2[0]) + post
		rest = post.join(ls2[1:])
		ret_ls.append(one_res + rest)
	# できあがったものをつなげて返す
	return "".join(ret_ls)
