
class NumericInspector:

    def __init__(self, column_name):
        self.column_name = column_name

    def column_max_is_between(self, lower_bound, upper_bound):
        query = (
            f"SELECT\n"
            f"    CASE WHEN MAX({self.column_name})>= {lower_bound}\n"
            f"          AND MAX({self.column_name})<= {upper_bound}\n"
            f"           THEN 1 ELSE 0\n"
            f"    END AS result\n"
            f"\n"
            f"FROM ...;\n"
        )
        return query