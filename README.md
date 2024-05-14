# comfyui_tag_filter

WD14Tagger などが出力したタグを、特定のカテゴリに分けて、カテゴリごとにフィルタリングして返す ComfyUI のカスタムノードです。

# TagFilter

特定のカテゴリに属するタグだけを抽出します。
smile や grin などは、expression というカテゴリです。
色のついているものは color カテゴリです。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/cde288d8-2d23-4989-9d1f-3b5ff3845c72)

include_categories は、含めたいカテゴリ名をカンマ区切りで指定します。

include_categories に expression と入力すると、上のチェックボックスをクリックしたのと同じ結果になります。

exclude_categories は逆に取り除きたいカテゴリを指定できます。服のタグだけ取りたいが色の指定は不要な場合に、include_categories に cloth と入れて、exclude_categories に color と打ちます。

# TagRemover

プロンプトの中から指定されたタグを削除したい時に使います。
TagFilter と合わせて使うと、表情のタグだけ消す、色（color）タグだけ消す、といった事が出来ます。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/694aadc3-8968-4153-bd52-8809aec47df6)

# TagReplace

同じカテゴリのタグを置き換えます。

例えば long hair というタグが含まれるプロンプトを入力し、置き換えるタグに twintails を指定すると、long hair を twintails に置き換える事が出来ます。

どれぐらい近いタグを置き換えるかを、0.0 ～ 1.0 で指定します。1.0 を指定するとカテゴリとして完全一致した場合にのみタグが置換されます。0.3 ぐらいがちょうどいいです。うまく置換されない場合は値を下げてください。

![image](https://github.com/sugarkwork/comfyui_tag_fillter/assets/98699377/c492c518-0531-4735-8a73-3a29ae0b9a1b)

