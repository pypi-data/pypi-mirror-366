import json
from typing import List

from ks3.responseResult import ResponseMetadata

from ks3.exception import KS3ClientError

class BucketDecompressPolicy:
    def __init__(self, rules: List['Rule'] = None, *args, **kwargs):
        self.rules = []
        for rule in rules:
            self.add_rule(rule)

        self.response_metadata = ResponseMetadata(**kwargs)

    def get_rules(self) -> List['Rule']:
        return self.rules

    def set_rules(self, rules: List['Rule']):
        for rule in rules:
            self.add_rule(rule)

    def add_rule(self, rule: 'Rule'):
        rule.validate()
        self.rules.append(rule)

    def to_json(self) -> str:
        # 转json时 不要带response_metadata，具体实现如下
        try:
            return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if k != 'response_metadata'})
        except Exception as e:
            raise KS3ClientError("failed to serialize decompressPolicy to json text", e)

    @staticmethod
    def from_json(json_text: str) -> 'BucketDecompressPolicy':
        try:
            data = json.loads(json_text)
            rules = [Rule(**rule) for rule in data.get('rules', [])]
            return BucketDecompressPolicy(rules)
        except Exception as e:
            raise KS3ClientError("failed to deserialize decompressPolicy from json text", e)

class OverwritePolicy:
    SKIP_IF_EXISTS = 0
    OVERWRITE_IF_EXISTS = 1

class PathPrefixPolicy:
    ADD_FILENAME = 0
    JUST_PATH_PREFIX = 1

class Rule:
    MAXIMUM_ALLOWED_ID_LENGTH = 256

    def __init__(self, id: str = None, events: str = None, prefix: str = None, suffix: List[str] = None,
                 overwrite: int = OverwritePolicy.SKIP_IF_EXISTS, callback: str = None, callback_format: str = None,
                 path_prefix: str = None, path_prefix_replaced: int = PathPrefixPolicy.ADD_FILENAME,
                 policy_type: str = "decompress"):
        self.id = id
        self.events = events
        self.prefix = prefix
        self.suffix = suffix if suffix is not None else []
        self.overwrite = overwrite
        self.callback = callback
        self.callback_format = callback_format
        self.path_prefix = path_prefix
        self.path_prefix_replaced = path_prefix_replaced
        self.policy_type = policy_type

    def validate(self):
        self.validate_rule_id()
        self.validate_events()
        self.validate_callback()
        self.validate_path_prefix()
        self.validate_policy_type()

    def validate_rule_id(self):
        if not self.id:
            raise KS3ClientError("missing rule id")
        if len(self.id) > self.MAXIMUM_ALLOWED_ID_LENGTH:
            raise KS3ClientError(f"rule id length must be between 1 and {self.MAXIMUM_ALLOWED_ID_LENGTH}")

    def validate_events(self):
        if not self.events:
            raise KS3ClientError("missing events")

    def validate_callback(self):
        # 如果callback不为空，则必须要有callback_format
        if self.callback:
            self.validate_callback_format()

    def validate_callback_format(self):
        if not self.callback_format:
            raise KS3ClientError("missing callback_format")

    def validate_path_prefix(self):
        if self.path_prefix and not self.path_prefix.endswith("/"):
            raise KS3ClientError("pathPrefix must end with '/' if not empty")

    def validate_policy_type(self):
        if not self.policy_type:
            raise KS3ClientError("missing policyType")

    def __repr__(self):
        return f"Rule(id={self.id}, events={self.events}, prefix={self.prefix}, suffix={self.suffix}, " \
               f"overwrite={self.overwrite}, callback={self.callback}, callback_format={self.callback_format}, " \
               f"path_prefix={self.path_prefix}, path_prefix_replaced={self.path_prefix_replaced}, " \
               f"policy_type={self.policy_type})"

# 示例用法
if __name__ == "__main__":
    rule = Rule(id="rule1", events="ObjectCreated:*", prefix="prefix1", suffix=[".zip"], path_prefix="path/")
    rule.validate()
    policy = bucketDecompressPolicy()
    policy.add_rule(rule)
    json_text = policy.to_json()
    print(json_text)
    new_policy = bucketDecompressPolicy.from_json(json_text)
    print(new_policy.get_rules())
