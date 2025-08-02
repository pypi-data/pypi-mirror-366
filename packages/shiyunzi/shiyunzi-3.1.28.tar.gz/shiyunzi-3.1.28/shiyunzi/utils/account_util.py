from shiyunzi.utils.models import RunwayAccount
from contextlib import contextmanager

@contextmanager 
def available_runway_endpoint() -> RunwayAccount:
    runway_account = None
    try:
        # 查询独享账号
        runway_account = (RunwayAccount.select().where(
            RunwayAccount.status == 0,
            RunwayAccount.type == "exclusive", 
            RunwayAccount.used < 2
        ).get_or_none())

        # 如果没有可用的独享账号,则查询共享账号
        if runway_account is None:
            runway_account = (RunwayAccount.select().where(
                RunwayAccount.status == 0,
                RunwayAccount.type == "shared",
                RunwayAccount.used < 2
            ).get_or_none())

        if runway_account is not None:
            runway_account.used += 1
            runway_account.save()
            yield runway_account
        else:
            yield None
    finally:
        if runway_account is not None:
            runway_account = RunwayAccount.select().where(RunwayAccount.id == runway_account.id).get()
            runway_account.used -= 1
            runway_account.save()