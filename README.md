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

