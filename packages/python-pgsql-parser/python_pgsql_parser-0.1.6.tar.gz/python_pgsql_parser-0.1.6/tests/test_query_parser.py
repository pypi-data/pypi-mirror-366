from pgsql_parser import SimpleSqlQueryParser
import json


def test_basic_select():
    """Tests a simple SELECT statement with AS alias."""
    query = "SELECT id, name AS full_name, age FROM users"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {"users": "users"}
    expected_elements = [
        {"column": "id", "alias": None, "table": "users"},
        {"column": "name", "alias": "full_name", "table": "users"},
        {"column": "age", "alias": None, "table": "users"},
    ]

    assert parser.get_select_elements() == expected_elements


def test_select_no_alias():
    """Tests a SELECT statement without any aliases."""
    query = "SELECT product_id, price FROM products"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "products"
    assert parser.get_all_tables_in_scope() == {"products": "products"}
    expected_elements = [
        {"column": "product_id", "alias": None, "table": "products"},
        {"column": "price", "alias": None, "table": "products"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_select_with_function():
    """Tests a SELECT statement with an aggregate function and an alias."""
    query = "SELECT COUNT(*) AS total_count FROM orders"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "orders"
    assert parser.get_all_tables_in_scope() == {"orders": "orders"}
    expected_elements = [
        {"column": "COUNT(*)", "alias": "total_count", "table": "orders"}
    ]
    assert parser.get_select_elements() == expected_elements


def test_select_with_table_alias_and_dot_notation():
    """Tests a SELECT statement with a table alias and dot notation for columns."""
    query = "SELECT u.id, u.email FROM users u"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {"u": "users"}
    expected_elements = [
        {"column": "id", "alias": None, "table": "users"},
        {"column": "email", "alias": None, "table": "users"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_select_with_multiple_functions_and_aliases():
    """Tests a SELECT with multiple functions and aliases."""
    query = "SELECT order_id, SUM(quantity) AS total_quantity, MAX(order_date) AS latest_order FROM order_items"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "order_items"
    assert parser.get_all_tables_in_scope() == {"order_items": "order_items"}
    expected_elements = [
        {"column": "order_id", "alias": None, "table": "order_items"},
        {"column": "SUM(quantity)", "alias": "total_quantity", "table": "order_items"},
        {"column": "MAX(order_date)", "alias": "latest_order", "table": "order_items"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_select_with_implicit_alias():
    """Tests a SELECT with an implicit alias."""
    query = "SELECT first_name, last_name, email user_email FROM employees"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "employees"
    assert parser.get_all_tables_in_scope() == {"employees": "employees"}
    expected_elements = [
        {"column": "first_name", "alias": None, "table": "employees"},
        {"column": "last_name", "alias": None, "table": "employees"},
        {"column": "email", "alias": "user_email", "table": "employees"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_select_star():
    """Tests a SELECT * query."""
    query = "SELECT * FROM inventory"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "inventory"
    assert parser.get_all_tables_in_scope() == {"inventory": "inventory"}
    expected_elements = [{"column": "*", "alias": None, "table": "inventory"}]
    assert parser.get_select_elements() == expected_elements


def test_inner_join():
    """Tests a query with an INNER JOIN."""
    query = "SELECT u.id, u.name, o.order_date FROM users u INNER JOIN orders o ON u.id = o.user_id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {"u": "users", "o": "orders"}
    expected_elements = [
        {"column": "id", "alias": None, "table": "users"},
        {"column": "name", "alias": None, "table": "users"},
        {"column": "order_date", "alias": None, "table": "orders"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_left_join():
    """Tests a query with a LEFT JOIN."""
    query = "SELECT p.product_name, c.category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "products"
    assert parser.get_all_tables_in_scope() == {"p": "products", "c": "categories"}
    expected_elements = [
        {"column": "product_name", "alias": None, "table": "products"},
        {"column": "category_name", "alias": None, "table": "categories"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_join_without_as():
    """Tests a query with a JOIN where table aliases don't use AS."""
    query = "SELECT a.author_name, b.title FROM authors a JOIN books b ON a.id = b.author_id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "authors"
    assert parser.get_all_tables_in_scope() == {"a": "authors", "b": "books"}
    expected_elements = [
        {"column": "author_name", "alias": None, "table": "authors"},
        {"column": "title", "alias": None, "table": "books"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_join_no_table_aliases():
    """Tests a query with a JOIN but no table aliases."""
    query = "SELECT users.username, roles.role_name FROM users JOIN roles ON users.role_id = roles.id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {"users": "users", "roles": "roles"}
    expected_elements = [
        {"column": "username", "alias": None, "table": "users"},
        {"column": "role_name", "alias": None, "table": "roles"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_full_outer_join():
    """Tests a query with a FULL OUTER JOIN."""
    query = "SELECT t1.col1, t2.col2 FROM table1 t1 FULL OUTER JOIN table2 t2 ON t1.id = t2.id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "table1"
    assert parser.get_all_tables_in_scope() == {"t1": "table1", "t2": "table2"}
    expected_elements = [
        {"column": "col1", "alias": None, "table": "table1"},
        {"column": "col2", "alias": None, "table": "table2"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_cross_join():
    """Tests a query with a CROSS JOIN."""
    query = "SELECT a.col_a, b.col_b FROM table_a a CROSS JOIN table_b b"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "table_a"
    assert parser.get_all_tables_in_scope() == {"a": "table_a", "b": "table_b"}
    expected_elements = [
        {"column": "col_a", "alias": None, "table": "table_a"},
        {"column": "col_b", "alias": None, "table": "table_b"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_query_with_where_clause():
    """Tests a query with a WHERE clause to ensure it's ignored for parsing."""
    query = "SELECT id, name FROM users WHERE age > 30"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {"users": "users"}
    expected_elements = [
        {"column": "id", "alias": None, "table": "users"},
        {"column": "name", "alias": None, "table": "users"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_query_with_group_by():
    """Tests a query with GROUP BY clause."""
    query = "SELECT c.customer_id, COUNT(o.order_id) AS num_orders FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "customers"
    assert parser.get_all_tables_in_scope() == {"c": "customers", "o": "orders"}
    expected_elements = [
        {"column": "customer_id", "alias": None, "table": "customers"},
        {"column": "COUNT(o.order_id)", "alias": "num_orders", "table": "orders"},
    ]

    assert parser.get_select_elements() == expected_elements


def test_query_with_literal_values():
    """Tests a query selecting literal values."""
    query = "SELECT 'literal_string_value' AS text_col, 123 AS num_col, 45.67 AS float_col FROM dual"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "dual"
    assert parser.get_all_tables_in_scope() == {"dual": "dual"}
    expected_elements = [
        {"column": "'literal_string_value'", "alias": "text_col", "table": "dual"},
        {"column": "123", "alias": "num_col", "table": "dual"},
        {"column": "45.67", "alias": "float_col", "table": "dual"},
    ]
    assert parser.get_select_elements() == expected_elements


def test_query_with_complex_function_and_alias():
    """Tests a query with a complex function and an alias."""
    query = "SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM customers"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "customers"
    assert parser.get_all_tables_in_scope() == {"customers": "customers"}
    expected_elements = [
        {
            "column": "CONCAT(first_name,' ',last_name)",
            "alias": "full_name",
            "table": "customers",
        }
    ]
    print(json.dumps(parser.get_select_elements(), indent=2))
    assert parser.get_select_elements() == expected_elements


def test_query_with_no_from_clause():
    """Tests a query without a FROM clause (e.g., SELECT 1)."""
    query = "SELECT 1 AS result"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() is None
    assert parser.get_all_tables_in_scope() == {}
    expected_elements = [{"column": "1", "alias": "result", "table": None}]
    assert parser.get_select_elements() == expected_elements


def test_query_with_subquery_in_from():
    """
    Tests a query with a subquery in the FROM clause.
    Note: The current parser treats the subquery's alias as the table name.
    """
    query = "SELECT id FROM (SELECT id, name FROM temp_table) AS subquery_alias"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "subquery_alias"
    assert parser.get_all_tables_in_scope() == {"subquery_alias": "subquery_alias"}
    expected_elements = [{"column": "id", "alias": None, "table": "subquery_alias"}]
    assert parser.get_select_elements() == expected_elements


def test_empty_query():
    """Tests an empty query string."""
    query = ""
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() is None
    assert parser.get_all_tables_in_scope() == {}
    assert parser.get_select_elements() == []


def test_only_select_keyword():
    """Tests a query with only SELECT keyword."""
    query = "SELECT"
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() is None
    assert parser.get_all_tables_in_scope() == {}
    assert parser.get_select_elements() == []


def test_multiple_joins_and_aliases():
    """Tests a query with multiple joins and various aliases."""
    query = """
    SELECT
        u.user_id,
        u.username AS user_name,
        o.order_id,
        oi.product_id,
        p.product_name,
        c.category_name AS cat_name
    FROM
        users u
    INNER JOIN
        orders o ON u.user_id = o.user_id
    LEFT JOIN
        order_items oi ON o.order_id = oi.order_id
    JOIN
        products p ON oi.product_id = p.product_id
    LEFT JOIN
        categories c ON p.category_id = c.category_id
    WHERE
        u.registration_date > '2023-01-01'
    ORDER BY
        o.order_date DESC
    """
    parser = SimpleSqlQueryParser(query)
    assert parser.get_table_name() == "users"
    assert parser.get_all_tables_in_scope() == {
        "u": "users",
        "o": "orders",
        "oi": "order_items",
        "p": "products",
        "c": "categories",
    }
    expected_elements = [
        {"column": "user_id", "alias": None, "table": "users"},
        {"column": "username", "alias": "user_name", "table": "users"},
        {"column": "order_id", "alias": None, "table": "orders"},
        {"column": "product_id", "alias": None, "table": "order_items"},
        {"column": "product_name", "alias": None, "table": "products"},
        {"column": "category_name", "alias": "cat_name", "table": "categories"},
    ]
    assert parser.get_select_elements() == expected_elements
