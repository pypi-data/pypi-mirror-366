import unittest
from pathlib import Path
from dbmanager.helpers.search import _query_lsh, load_db_lsh

class TestLSHQuery(unittest.TestCase):
    @unittest.skipUnless(
        Path("/Users/mp/DjangoExperimental/Thoth/data/dev_databases/california_schools/preprocessed/california_schools_lsh.pkl").exists(),
        "LSH data files not found"
    )
    def test_query_lsh_non_interactive(self):
        """Non-interactive test using known california_schools dataset"""
        db_directory_path = "/Users/mp/DjangoExperimental/Thoth/data/dev_databases/california_schools"
        db_id = "california_schools"
        keyword = "meals"
        signature_size = 30
        n_gram = 9
        top_n = 5

        try:
            lsh, minhashes = load_db_lsh(db_directory_path, db_id=db_id)
        except FileNotFoundError:
            self.fail(
                f"LSH data not found in '{db_directory_path}'. "
                "Please ensure the path is correct and the data exists."
            )

        print(f"\n--- Running LSH Query Test ---")
        print(f"Database Path: '{db_directory_path}'")
        print(f"Keyword: '{keyword}'")
        print(f"Signature Size: {signature_size}")
        print(f"N-gram: {n_gram}")
        print(f"Top N: {top_n}")
        print("--------------------------------\n")

        # Query the LSH
        results = _query_lsh(
            lsh,
            minhashes,
            keyword,
            signature_size=signature_size,
            n_gram=n_gram,
            top_n=top_n,
        )

        # Print the results
        print("--- Query Results ---")
        if not results:
            print("No results found.")
        else:
            for table, columns in results.items():
                print(f"Table: {table}")
                for col, values in columns.items():
                    print(f"  Column: {col}")
                    for val in values:
                        print(f"    - {val}")
        print("---------------------\n")

        # This is an interactive test, so we don't assert anything specific.
        # The goal is to observe the output.
        self.assertIsNotNone(results, "The result should not be None")

if __name__ == "__main__":
    unittest.main()
