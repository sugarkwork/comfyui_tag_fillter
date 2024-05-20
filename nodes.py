import os
import json


tag_category = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))


class TagMerger:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags1": ("STRING", {"default": ""}),
                "tags2": ("STRING", {"default": ""}),
                "under_score": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str, tags2:str, under_score=True):
        tags1 = [tag.strip().replace(" ", "_").lower() for tag in tags1.replace(".",",").replace("\n",",").split(",")]
        tags2 = [tag.strip().replace(" ", "_").lower() for tag in tags2.replace(".",",").replace("\n",",").split(",")]

        tags = tags1 + list(set(tags2) - set(tags1))

        # exclude none daata
        tags = [tag for tag in tags if tag]

        if not under_score:
            tags = [tag.replace("_", " ") for tag in tags]

        return (", ".join(tags),)


class TagRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "exclude_tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, exclude_tags:str=""):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags2 = [tag.replace(" ", "_").lower().strip() for tag in tags]

        exclude_tags = [tag.strip() for tag in exclude_tags.replace("\n",",").split(",")]
        exclude_tags2 = [tag.replace(" ", "_").lower().strip() for tag in exclude_tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 not in exclude_tags2:
                result.append(tags[i])
        
        return (", ".join(result),)


class TagReplace:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "replace_tags": ("STRING", {"default": ""}),
                "match": ("FLOAT", {"default": 0.3}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def _get_categories(self, tag: str) -> set:
        """タグのカテゴリーを取得する"""
        return set(tag_category.get(tag, []))

    def _category_match_percentage(self, categories1: set, categories2: set) -> float:
        """2つのカテゴリセット間の一致度(%)を計算する"""
        if not categories1 or not categories2:
            return 0
        intersection = categories1.intersection(categories2)
        union = categories1.union(categories2)
        return len(intersection) / len(union)

    def tag(self, tags:str, replace_tags:str="", match:float=0.3):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in tags]

        replace_tags = [tag.strip() for tag in replace_tags.replace("\n",",").split(",")]
        replace_tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in replace_tags]
        replace_tags_used = {tag:False for tag in replace_tags_normalized}

        result = []
        for i, tag in enumerate(tags_normalized):
            tag_categories = self._get_categories(tag)
            best_match_tag = None
            best_match_tag_id = None
            best_match_percentage = 0

            for k, replace_tag in enumerate(replace_tags_normalized):
                replace_categories = self._get_categories(replace_tag)
                match_percentage = self._category_match_percentage(tag_categories, replace_categories)

                if match_percentage and match_percentage > best_match_percentage:
                    best_match_percentage = match_percentage
                    best_match_tag = replace_tag
                    replace_tags_used[replace_tag] = True
                    best_match_tag_id = k

            
            if best_match_tag and best_match_percentage >= match:
                result.append(replace_tags[best_match_tag_id])
            else:
                result.append(tags[i])

        # replace_tags の中から、tags に存在しないタグを追加
        extra_tags = [replace_tag for replace_tag, used in replace_tags_used.items() if not used]
        result.extend(extra_tags)
        
        return (", ".join(result),)
    

class TagFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "pose": ("BOOLEAN", {"default": True}),
                "gesture": ("BOOLEAN", {"default": True}),
                "action": ("BOOLEAN", {"default": True}),
                "emotion": ("BOOLEAN", {"default": True}),
                "expression": ("BOOLEAN", {"default": True}),
                "camera": ("BOOLEAN", {"default": True}),
                "angle": ("BOOLEAN", {"default": True}),
                "sensitive": ("BOOLEAN", {"default": True}),
                "liquid": ("BOOLEAN", {"default": True}),
                "include_categories": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags, pose=True, gesture=True, action=True, emotion=True, expression=True, camera=True, angle=True, sensitive=True, liquid=True, include_categories="", exclude_categories=""):

        targets = []
        exclude_targets = []
        if pose:
            targets.append("pose")
        if gesture:
            targets.append("gesture")
        if action:
            targets.append("action")
        if emotion:
            targets.append("emotion")
        if expression:
            targets.append("expression")
        if camera:
            targets.append("camera")
        if angle:
            targets.append("angle")
        if sensitive:
            targets.append("sensitive")
        if liquid:
            targets.append("liquid")
        
        include_categories = include_categories.strip()
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]

        if exclude_categories:
            exclude_targets = [category.strip() for category in exclude_categories.replace("\n",",").split(",")]
            targets = [target for target in targets if target not in exclude_targets]
        
        print("targets", targets)

        tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])

                for category in category_list:
                    if category in exclude_targets:
                        break
                else:
                    for category in category_list:
                        if '*' in include_categories or ( category in targets and tags[i] not in result ):
                            result.append(tags[i])
                            break

        return (", ".join(result),)

NODE_CLASS_MAPPINGS = {
    "TagMerger": TagMerger,
    "TagFilter": TagFilter,
    "TagReplace": TagReplace,
    "TagRemover": TagRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagMerger": "TagMerger",
    "TagFilter": "TagFilter",
    "TagReplace": "TagReplace",
    "TagRemover": "TagRemover"
}
