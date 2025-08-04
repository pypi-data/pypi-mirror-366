from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseNonSystemModel(BaseModel):
    """
    Base model for non-system entities

    This objects can be created, updated or deleted by API user
    """

    model_config = ConfigDict(serialize_by_alias=True)


class BaseSystemModel(BaseModel):
    """
    Base model for system entities

    This objects cannot be created, updated or deleted by API user
    """

    model_config = ConfigDict(serialize_by_alias=True)

    id_: int = Field(alias="id")
    changed: datetime


class Instrument(BaseSystemModel):
    title: str
    short_title: str = Field(
        alias="shortTitle", description="Three-symbol code of currency"
    )
    symbol: str = Field(description="Symbol of currency")
    rate: float = Field(description="Rate of currency with respect to ruble")


class Company(BaseSystemModel):
    title: str
    full_title: str = Field(alias="fullTitle")
    www: str = Field(description="Website of company")
    country: str = Field(description="Country of company")


class User(BaseSystemModel):
    login: str | None = Field(None, description="Login of user")
    currency_id: int = Field(
        alias="currency", description="ID of currency, FK for Instrument"
    )
    parent: int | None = Field(None, description="ID of parent user, FK for User")


class Account(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of account")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    title: str = Field(description="Title of account")
    type: str = Field(description="Type of account")
    instrument: int = Field(description="ID of instrument, FK for Instrument")
    company: int = Field(description="ID of company, FK for Company")
    sync_id: list[str] = Field(alias="syncID", description="Sync IDs")
    balance: float = Field(description="Balance of account")
    start_balance: float = Field(alias="startBalance", description="Start balance")
    in_balance: bool = Field(alias="inBalance", description="Include in balance")
    enable_correction: bool = Field(
        alias="enableCorrection", description="Enable correction"
    )
    enable_sms: bool = Field(alias="enableSMS", description="Enable SMS")
    archive: bool = Field(description="Archive flag")
    private: bool = Field(description="Private flag")
    capitalization: bool = Field(description="Capitalization flag")
    percent: float = Field(description="Percent rate")
    start_date: str = Field(alias="startDate", description="Start date")
    end_date_offset: int = Field(alias="endDateOffset", description="End date offset")
    payoff_step: int = Field(alias="payoffStep", description="Payoff step")
    payoff_interval: int = Field(alias="payoffInterval", description="Payoff interval")
    color: int = Field(description="Color of account")
    icon: str = Field(description="Icon of account")
    savings: bool = Field(description="Savings flag")


class Tag(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of tag")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    title: str = Field(description="Title of tag")
    parent: str | None = Field(None, description="ID of parent tag, FK for Tag")
    icon: str = Field(description="Icon of tag")
    picture: str = Field(description="Picture of tag")
    color: int = Field(description="Color of tag")
    show_income: bool = Field(alias="showIncome", description="Show income")
    show_outcome: bool = Field(alias="showOutcome", description="Show outcome")
    budget_income: bool = Field(alias="budgetIncome", description="Budget income")
    budget_outcome: bool = Field(alias="budgetOutcome", description="Budget outcome")
    required: bool = Field(description="Required flag")
    capitalization: bool = Field(description="Capitalization flag")
    percent: float = Field(description="Percent rate")
    start_date: str = Field(alias="startDate", description="Start date")
    end_date_offset: int = Field(alias="endDateOffset", description="End date offset")
    payoff_step: int = Field(alias="payoffStep", description="Payoff step")
    payoff_interval: int = Field(alias="payoffInterval", description="Payoff interval")


class Merchant(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of merchant")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    title: str = Field(description="Title of merchant")


class Reminder(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of reminder")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    income_instrument: int = Field(
        alias="incomeInstrument",
        description="ID of income instrument, FK for Instrument",
    )
    income_account: str = Field(
        alias="incomeAccount", description="ID of income account, FK for Account"
    )
    income: float = Field(description="Income amount")
    outcome_instrument: int = Field(
        alias="outcomeInstrument",
        description="ID of outcome instrument, FK for Instrument",
    )
    outcome_account: str = Field(
        alias="outcomeAccount", description="ID of outcome account, FK for Account"
    )
    outcome: float = Field(description="Outcome amount")
    tag: list[str] | None = Field(None, description="List of tag IDs, FK for Tag")
    merchant: str | None = Field(None, description="ID of merchant, FK for Merchant")
    payee: str | None = Field(None, description="Payee name")
    comment: str | None = Field(None, description="Comment")
    interval: int | None = Field(None, description="Interval in days")
    step: int | None = Field(None, description="Step")
    points: list[int] | None = Field(None, description="Points")
    start_date: str = Field(alias="startDate", description="Start date")
    end_date: str | None = Field(None, alias="endDate", description="End date")
    notify: bool = Field(description="Notify flag")


class ReminderMarker(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of reminder marker")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    income_instrument: int = Field(
        alias="incomeInstrument",
        description="ID of income instrument, FK for Instrument",
    )
    income_account: str = Field(
        alias="incomeAccount", description="ID of income account, FK for Account"
    )
    income: float = Field(description="Income amount")
    outcome_instrument: int = Field(
        alias="outcomeInstrument",
        description="ID of outcome instrument, FK for Instrument",
    )
    outcome_account: str = Field(
        alias="outcomeAccount", description="ID of outcome account, FK for Account"
    )
    outcome: float = Field(description="Outcome amount")
    tag: list[str] | None = Field(None, description="List of tag IDs, FK for Tag")
    merchant: str | None = Field(None, description="ID of merchant, FK for Merchant")
    payee: str | None = Field(None, description="Payee name")
    comment: str | None = Field(None, description="Comment")
    date: str = Field(description="Date")
    reminder: str = Field(description="ID of reminder, FK for Reminder")
    state: str = Field(description="State of reminder marker")
    notify: bool = Field(description="Notify flag")


class Transaction(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of transaction")
    changed: datetime
    created: datetime = Field(description="Creation timestamp")
    user: int = Field(description="ID of user, FK for User")
    deleted: bool = Field(False, description="Deleted flag")
    income_instrument: int = Field(
        alias="incomeInstrument",
        description="ID of income instrument, FK for Instrument",
    )
    income_account: str = Field(
        alias="incomeAccount", description="ID of income account, FK for Account"
    )
    income: float = Field(description="Income amount")
    outcome_instrument: int = Field(
        alias="outcomeInstrument",
        description="ID of outcome instrument, FK for Instrument",
    )
    outcome_account: str = Field(
        alias="outcomeAccount", description="ID of outcome account, FK for Account"
    )
    outcome: float = Field(description="Outcome amount")
    tag: list[str] | None = Field(None, description="List of tag IDs, FK for Tag")
    merchant: str | None = Field(None, description="ID of merchant, FK for Merchant")
    payee: str | None = Field(None, description="Payee name")
    original_payee: str | None = Field(
        None, alias="originalPayee", description="Original payee name"
    )
    comment: str | None = Field(None, description="Comment")
    date: str = Field(description="Date of transaction")
    mcc: int | None = Field(None, description="Merchant Category Code")
    reminder_marker: str | None = Field(
        None,
        alias="reminderMarker",
        description="ID of reminder marker, FK for ReminderMarker",
    )
    op_income: float | None = Field(
        None, alias="opIncome", description="Operation income"
    )
    op_income_instrument: int | None = Field(
        None,
        alias="opIncomeInstrument",
        description="ID of operation income instrument, FK for Instrument",
    )
    op_outcome: float | None = Field(
        None, alias="opOutcome", description="Operation outcome"
    )
    op_outcome_instrument: int | None = Field(
        None,
        alias="opOutcomeInstrument",
        description="ID of operation outcome instrument, FK for Instrument",
    )
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")


class Budget(BaseNonSystemModel):
    id_: str = Field(alias="id", description="UUID of budget")
    changed: datetime
    user: int = Field(description="ID of user, FK for User")
    tag: list[str] | None = Field(None, description="List of tag IDs, FK for Tag")
    date: str = Field(description="Date")
    income: float = Field(description="Income amount")
    income_lock: bool = Field(alias="incomeLock", description="Income lock flag")
    outcome: float = Field(description="Outcome amount")
    outcome_lock: bool = Field(alias="outcomeLock", description="Outcome lock flag")


class DiffObject(BaseModel):
    """
    Diff object for API synchronization
    """

    model_config = ConfigDict(serialize_by_alias=True)

    server_timestamp: int = Field(
        alias="serverTimestamp", description="Server timestamp"
    )
    current_client_timestamp: int = Field(
        alias="currentClientTimestamp",
        description="Current client timestamp",
    )
    instrument: list[Instrument] | None = Field(None, description="List of instruments")
    company: list[Company] | None = Field(None, description="List of companies")
    user: list[User] | None = Field(None, description="List of users")
    account: list[Account] | None = Field(None, description="List of accounts")
    tag: list[Tag] | None = Field(None, description="List of tags")
    merchant: list[Merchant] | None = Field(None, description="List of merchants")
    reminder: list[Reminder] | None = Field(None, description="List of reminders")
    reminder_marker: list[ReminderMarker] | None = Field(
        None, alias="reminderMarker", description="List of reminder markers"
    )
    transaction: list[Transaction] | None = Field(
        None, description="List of transactions"
    )
    budget: list[Budget] | None = Field(None, description="List of budgets")
    deletion: list[dict] | None = Field(None, description="List of deletions")


class Deletion(BaseModel):
    """
    Deletion object for API synchronization
    """

    id_: str = Field(alias="id", description="ID of deleted object")
    object: str = Field(description="Type of deleted object")
    user: int = Field(description="ID of user")
    stamp: int = Field(description="Timestamp of deletion")
