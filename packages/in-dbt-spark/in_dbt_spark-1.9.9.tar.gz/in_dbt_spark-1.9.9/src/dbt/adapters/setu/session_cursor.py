import os
import time
from typing import Optional
import re

import dbt_common.exceptions
from dbt.adapters.setu.client import SetuClient
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.setu.constants import VALID_STATEMENT_KINDS
from dbt.adapters.setu.models import StatementKind, Output, StatementState, Statement
from dbt.adapters.setu.utils import (
    polling_intervals,
    waiting_for_output,
    get_data_from_json_output,
)

logger = AdapterLogger("Spark")


class SetuStatementCursor:
    """
    Manage SETU statement and high-level interactions with it.
    :param client: setu client for managing statements
    :param session_id: setu session ID
    """

    def __init__(self, client: SetuClient, session_id: str):
        self.session_id: str = session_id
        self.client: SetuClient = client
        self.statement: Optional[Statement] = None

    def description(self):
        self.fetchall()
        json_output = self.statement.output.json
        columns = json_output["schema"]["fields"]

        # Old behavior but with an added index field["type"]
        return [[column["name"], column["type"]] for column in columns]

    def execute(self, code: str) -> Output:
        statement_kind: StatementKind = self.get_statement_kind(code)
        logger.info(f"statement_kind = {statement_kind} ")
        formatted_code: str = self.get_formatted_code(code)
        logger.info(f"formatted_code = {formatted_code} ")
        if statement_kind not in VALID_STATEMENT_KINDS:
            raise ValueError(
                f"{statement_kind} is not a valid statement kind for a SETU server of "
                f"(should be one of {VALID_STATEMENT_KINDS})"
            )
        self.statement = self.client.create_statement(
            self.session_id, formatted_code, statement_kind
        )
        intervals = polling_intervals([1, 2, 3, 5], 10)
        while waiting_for_output(self.statement):
            logger.info(
                " Setu statement progress {} : {}".format(
                    self.statement.statement_id, self.statement.progress
                )
            )
            time.sleep(next(intervals))
            self.statement = self.client.get_statement(
                self.statement.session_id, self.statement.statement_id
            )
        if self.statement.output is None:
            logger.error(f" Setu Statement {self.statement.statement_id} had no output ")
            raise dbt_common.exceptions.DbtRuntimeError(
                f"Setu Statement {self.statement.statement_id} had no output"
            )
        logger.info(
            "Setu Statement {} state is : {}".format(
                self.statement.statement_id, self.statement.state
            )
        )
        try:
            self.statement.output.raise_for_status()
        except dbt_common.exceptions.DbtRuntimeError as e:
            error_message = str(e)
            # Use regex to check for the specific non-fatal error message
            if (re.search(r"User .* is in too many groups already and cannot be added to more", error_message)
                    or re.search(r"User .* does not exist in Grid LDAP", error_message)):
                logger.warning(
                    f"Non-fatal error during Setu Statement {self.statement.statement_id} execution: {error_message}"
                    " This error is being treated as non-fatal as per requirements."
                )
                return self.statement.output
            else:
                raise e
        except Exception as e:
            raise dbt_common.exceptions.DbtRuntimeError(
                f"An unexpected error occurred during Setu Statement {self.statement.statement_id} status check: {e}"
            )
        if not self.statement.output.execution_success:
            logger.error(
                "Setu Statement {} output Error : {}".format(
                    self.statement.statement_id, self.statement.output
                )
            )
            raise dbt_common.exceptions.DbtRuntimeError(
                f"Error during Setu Statement {self.statement.statement_id} execution : {self.statement.output.error}"
            )
        return self.statement.output

    def close(self):
        if self.statement is not None and self.statement.state in [
            StatementState.WAITING,
            StatementState.RUNNING,
        ]:
            try:
                logger.info("closing Setu Statement id : {} ".format(self.statement.statement_id))
                self.client.cancel_statement(
                    self.statement.session_id, self.statement.statement_id
                )
                logger.info("Setu Statement closed")
            except Exception as e:
                logger.exception("Setu Statement already closed ", e)

    def fetchall(self):
        if self.statement is not None and self.statement.state in [
            StatementState.WAITING,
            StatementState.RUNNING,
        ]:
            intervals = polling_intervals([1, 2, 3, 5], 10)
            while waiting_for_output(self.statement):
                logger.info(
                    " Setu statement {} progress : {}".format(
                        self.statement.statement_id, self.statement.progress
                    )
                )
                time.sleep(next(intervals))
                self.statement = self.client.get_statement(
                    self.statement.session_id, self.statement.statement_id
                )
            if self.statement.output is None:
                logger.error(f"Setu Statement {self.statement.statement_id} had no output")
                raise dbt_common.exceptions.DbtRuntimeError(
                    f"Setu Statement {self.statement.statement_id} had no output"
                )
            self.statement.output.raise_for_status()
            if self.statement.output.json is None:
                logger.error(f"Setu statement {self.statement.statement_id} had no JSON output")
                raise dbt_common.exceptions.DbtRuntimeError(
                    f"Setu statement {self.statement.statement_id} had no JSON output"
                )
            return get_data_from_json_output(self.statement.output.json)
        elif self.statement is not None:
            self.statement.output.raise_for_status()
            return get_data_from_json_output(self.statement.output.json)
        else:
            raise dbt_common.exceptions.DbtRuntimeError(
                "Setu statement response : {} ".format(self.statement)
            )

    def get_formatted_code(self, code: str) -> str:
        code_lines = []
        for line in code.splitlines():
            line = line.strip()
            # Ignore depends_on statements in model files
            if not line or line.startswith("-- depends_on:"):
                continue
            """
            StatementKind inference logic (sql/scala/pyspark)
            If Macro sql contains $$spark$$ in the beginning of the line, then spark
            Else If Macro sql contains $$pyspark$$ in the beginning of the line, then pyspark
            Else sql
            """
            if line.startswith("$$" + StatementKind.SPARK.value + "$$"):
                line = line.replace("$$" + StatementKind.SPARK.value + "$$", " ", 1)
            elif line.startswith("$$" + StatementKind.PYSPARK.value + "$$"):
                line = line.replace("$$" + StatementKind.PYSPARK.value + "$$", " ", 1)
            code_lines.append(" " + line)
        formatted_code = os.linesep.join([s for s in code_lines if s.strip()])
        return formatted_code

    def get_statement_kind(self, code: str) -> StatementKind:
        for line in code.splitlines():
            line = line.strip()
            # Ignore depends_on statements in model files
            if not line or line.startswith("-- depends_on:"):
                continue
            """
            StatementKind inference logic (sql/scala/pyspark)
            If Macro sql contains $$spark$$ in the beginning of the line, then spark
            Else If Macro sql contains $$pyspark$$ in the beginning of the line, then pyspark
            Else sql
            """
            if line.startswith("$$" + StatementKind.SPARK.value + "$$"):
                return StatementKind.SPARK
            elif line.startswith("$$" + StatementKind.PYSPARK.value + "$$"):
                return StatementKind.PYSPARK
            else:
                return StatementKind.SQL
        return StatementKind.SQL
