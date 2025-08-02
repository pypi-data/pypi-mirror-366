"""
This module exposes a local runtime environment for RelyComply risk rating functions that
emulates the environment of the RelyComply cloud.
"""

import pprint
from dataclasses import dataclass
from datetime import datetime, timezone
import json

import tabulate
from relycomply_client.rc import rc


def print_header(header):
    print()
    print(header)
    print("=" * len(header))


@dataclass
class Score:
    """
    The return value of a a score_customer function.
    """

    name: str  # The name of the score
    label: str  # A human readable label for the score
    value: float  # The numeric value of the score
    maximum: float  # The maximum value the score can take
    minimum: float = 0  # The minimum value the score can take
    category: str = None  # The category of the score (high,medium,low)
    components: list["Score"] = None  # A list of sub scores that make up this score


class CustomerFacade:
    """
    This is a convenience wrapper around the customer API packet.
    """

    def __init__(self, customer_packet):
        self.__dict__.update(customer_packet)

    def customer_data(self, key, multiple_values=False):
        """
        Given a customer data key return the associated value.

        If multiple_values is True, return a list of all values associated with the key.
        """
        results = [datum["value"] for datum in self.data if datum["key"] == key]

        if not multiple_values:
            if len(results) > 1:
                raise ValueError(f"Multiple values found for key {key}")
            elif len(results) == 0:
                raise ValueError(f"No values found for key {key}")
            return results[0]

        return results

    def indicator(self, key):
        """
        Given a customer indicator key return whether the customer has the indicator.
        """
        indicators = self.indicators

        now = datetime.now(timezone.utc)
        for indicator in indicators:
            name = indicator["indicator"]["name"]
            valid_from = datetime.fromisoformat(indicator["validFrom"])
            valid_until = (
                None
                if indicator["validUntil"] is None
                else datetime.fromisoformat(indicator["validUntil"])
            )

            if (
                name == key
                and valid_from < now
                and (valid_until is None or valid_until > now)
            ):
                return True

        return False


class GraphQLLookupTableQuery:
    """
    This creates a callable that uses the graphQL API to query lookup tables associated with a risk rating.
    This emulates the same behaviour as the RelyComply risk rating engine.

    it is exposed to the score customers function as a lookup function with the following signature:

    table_name:         string of the lookup table name
    value_column: the   column to return value or values from. This is what you are looking up.
    multiple_values:    If true, return a list of values. If false, return a single value.
    **filters:          key value pairs of filters to apply to the lookup table. The key here corresponds
                        to the column name you wish to filter. The value can either be a scalar or a list of scalars.
                        If a single value is given it will filter rows where only that value is matched. If a list
                        is given it will filter rows where any of teh given values are present.

    Example usage in a score_customer function:

    ```python
    def score_customer(parameters, customer, lookup, Score):
        ...
        jurisdiction_scores = lookup(
            "jurisdiction_scores",
            client_type=customer.customer_data("client_type"),
            country=[customer.nationality, customer.residence]
            value_column="score",
            multiple_values=True
        )

        jurisdiction_score = max(jurisdiction_scores)
        ...

    ```
    """

    def __init__(self, risk_rating, quiet):
        self.risk_rating = risk_rating
        self.quiet = quiet

    def __call__(self, table_name, *, value_column, multiple_values=False, **filters):
        if not self.quiet:
            print_header(f"Lookup on {table_name}")

        list_filters = [
            dict(
                column=key,
                values=[str(value) for value in values]
                if isinstance(values, list)
                else [str(values)],
            )
            for key, values in filters.items()
        ]

        matching_lookups = [
            lookup
            for lookup in self.risk_rating["lookups"]
            if lookup["table"]["name"] == table_name
        ]
        if not matching_lookups:
            raise ValueError(
                f"Lookup table {table_name} not found in the lookups associated with this risk rating config"
            )
        if len(matching_lookups) > 1:
            raise ValueError(
                f"Multiple lookup tables found with name {table_name} in the lookups associated with this risk rating config"
            )
        version = matching_lookups[0]["versionNumber"]

        variables = dict(
            table=table_name,
            version=str(version),
            filters=list_filters,
            valueColumn=value_column,
        )

        if not self.quiet:
            pprint.pprint(variables)
            print()

        response = rc.gql.graphql(
            graphql_query="""
                query (
                    $table: LookupTableReference!, 
                    $version: String!, 
                    $filters: [LookupTableQueryFilterInput]!, 
                    $valueColumn: String!
                ) {
                    queryLookupTable(table: $table, version: $version, filters: $filters, valueColumn: $valueColumn) {
                        count
                        rows
                        schema {
                            columns {
                                name
                                dtype
                            }
                        }
                        valuesString
                        valuesNumber
                    }
                }
            """,
            variables=variables,
        )

        results = response["queryLookupTable"]
        if not self.quiet:
            print(
                tabulate.tabulate(
                    [json.loads(row).values() for row in results["rows"]],
                    headers=[column["name"] for column in results["schema"]["columns"]],
                )
            )

        if results["count"] == 0:
            raise ValueError("No values found")
        if not multiple_values and results["count"] > 1:
            raise ValueError("Multiple values found")

        values = results["valuesNumber"] or results["valuesString"]

        if multiple_values:
            return values
        else:
            return values[0]


def print_score(score):
    def map_score(s):
        return [s.name, s.label, s.value, s.minimum, s.maximum, s.category]

    print(
        tabulate.tabulate(
            [map_score(score), *map(map_score, score.components)],
            headers=["Name", "Label", "Value", "Minimum", "Maximum", "Category"],
        )
    )


def run_risk_rating(
    scoring_function,
    customer_identifier,
    risk_rating_config_id,
    customer_data_overrides,
    indicator_overrides,
):
    """
    Given a scoring function and a customer identifier and risk rating config id, run the scoring function.

    This will build an execution environment that works in the same way as the risk rating engine
    on the RelyComply cloud. It allows for simple local debugging and testing of risk rating configurations.

    Usage

    ```python
    from relycomply_client.risk_rating_runtime import run_risk_rating
    from my_risK_rating_module import score_customer

    run_risk_rating(scoring_function, "<customer_identifier>", "<risk_rating_id_or_name>")

    ```
    """
    customer_packet = rc.gql.customers(identifier=str(customer_identifier), _only=True)
    pprint.pp(customer_packet)

    print_header("Overridden Customer Data")
    pprint.pp(customer_data_overrides)
    data = customer_packet["data"]
    for k, v in customer_data_overrides.items():
        data.append({"key": k, "value": v})
    customer_packet["data"] = data

    print_header("Overridden Customer Indicators")
    pprint.pp(indicator_overrides)
    indicators = customer_packet["indicators"]
    for val in indicator_overrides:
        indicators.append(
            {
                "indicator": {"name": val},
                "validFrom": datetime.now(timezone.utc).isoformat(),
                "validUntil": None,
            }
        )
    customer_packet["indicators"] = indicators

    risk_rating = rc.gql.riskRatingConfigs(id=risk_rating_config_id, _only=True)
    if not quiet:
        print_header("Risk rating config")
        pprint.pp(risk_rating)

    parameters = {
        parameter["key"]: parameter["value"] for parameter in risk_rating["parameters"]
    }
    if not quiet:
        print_header("Parameters")
        pprint.pp(parameters)

    lookup = GraphQLLookupTableQuery(risk_rating, quiet=quiet)
    customer = CustomerFacade(customer_packet)
    score = scoring_function(
        parameters=parameters, customer=customer, lookup=lookup, Score=Score
    )

    print_header("Final scores")
    print_score(score)

    return score
