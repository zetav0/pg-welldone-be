from enum import Enum


class StageOption(str, Enum):
    QA = "qa"
    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    TEST = "test"

    def is_local_or_test_env(self):
        return self in [self.TEST, self.LOCAL]


class DatabaseOption(str, Enum):
    POSTGRES = "postgres"
    SQLITE = "sqlite"
