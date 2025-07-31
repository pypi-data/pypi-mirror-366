# coffy/nosql/nosql_tests.py
# author: nsarathy

from coffy.nosql import db
import json
import os
import tempfile
import unittest


class TestCollectionManager(unittest.TestCase):

    def setUp(self):
        self.col = db(collection_name="test_collection")
        self.col.clear()
        self.col.add_many(
            [
                {"name": "Alice", "age": 30, "tags": ["x", "y"]},
                {"name": "Bob", "age": 25, "tags": ["y", "z"]},
                {"name": "Carol", "age": 40, "nested": {"score": 100}},
            ]
        )

    def test_add_and_all_docs(self):
        result = self.col.all_docs()
        self.assertEqual(len(result), 3)

    def test_add_list(self):
        self.col.add({"name": "Dave", "age": 35, "tags": ["x", "z"]})
        result = self.col.all_docs()
        self.assertEqual(len(result), 4)

    def test_where_eq(self):
        q = self.col.where("name").eq("Alice")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["age"], 30)

    def test_where_gt_and_lt(self):
        gt_q = self.col.where("age").gt(26)
        lt_q = self.col.where("age").lt(40)
        self.assertEqual(gt_q.count(), 2)
        self.assertEqual(lt_q.count(), 2)

    def test_exists(self):
        q = self.col.where("nested").exists()
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_in_and_nin(self):
        q1 = self.col.where("name").in_(["Alice", "Bob"])
        q2 = self.col.where("name").nin(["Carol"])
        self.assertEqual(q1.count(), 2)
        self.assertEqual(q2.count(), 2)

    def test_matches(self):
        q = self.col.where("name").matches("^A")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_nested_field_access(self):
        q = self.col.where("nested.score").eq(100)
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_logic_and_or_not(self):
        q = self.col.match_all(
            lambda q: q.where("age").gte(25), lambda q: q.where("age").lt(40)
        )
        self.assertEqual(q.count(), 2)

        q = self.col.match_any(
            lambda q: q.where("name").eq("Alice"), lambda q: q.where("name").eq("Bob")
        )
        self.assertEqual(q.count(), 2)

        q = self.col.not_any(
            lambda q: q.where("name").eq("Bob"), lambda q: q.where("age").eq(40)
        )
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_run_with_projection(self):
        q = self.col.where("age").gte(25)
        result = q.run(fields=["name"])
        self.assertEqual(len(result), 3)
        for doc in result:
            self.assertEqual(list(doc.keys()), ["name"])

    def test_update_and_delete_and_replace(self):
        self.col.where("name").eq("Alice").update({"updated": True})
        updated = self.col.where("updated").eq(True).first()
        self.assertEqual(updated["name"], "Alice")

        self.col.where("name").eq("Bob").delete()
        self.assertEqual(self.col.where("name").eq("Bob").count(), 0)

        self.col.where("name").eq("Carol").replace({"name": "New", "age": 99})
        new_doc = self.col.where("name").eq("New").first()
        self.assertEqual(new_doc["age"], 99)

    def test_aggregates(self):
        self.assertEqual(self.col.sum("age"), 95)
        self.assertEqual(self.col.avg("age"), 95 / 3)
        self.assertEqual(self.col.min("age"), 25)
        self.assertEqual(self.col.max("age"), 40)

    def test_merge(self):
        q = self.col.where("name").eq("Alice")
        merged = q.merge(lambda d: {"new": d["age"] + 10}).run()
        self.assertEqual(merged[0]["new"], 40)

    def test_lookup_and_merge_pipeline(self):
        users = db("users")
        orders = db("orders")
        users.clear()
        orders.clear()
        users.add_many([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        orders.add_many(
            [
                {"order_id": 101, "user_id": 1, "total": 50},
                {"order_id": 102, "user_id": 1, "total": 70},
                {"order_id": 103, "user_id": 2, "total": 20},
            ]
        )

        # Only simulate one-to-one (latest order per user) manually
        latest_by_user = {
            103: {"user_id": 2, "total": 20},
            102: {"user_id": 1, "total": 70},
        }
        db("latest_orders").clear()
        db("latest_orders").add_many(list(latest_by_user.values()))

        result = (
            users.lookup(
                "latest_orders",
                local_key="id",
                foreign_key="user_id",
                as_field="latest",
                many=False,
            )
            .merge(lambda d: {"latest_total": d.get("latest", {}).get("total", 0)})
            .run()
            .as_list()
        )
        totals = {d["name"]: d["latest_total"] for d in result}
        self.assertEqual(totals["Alice"], 70)
        self.assertEqual(totals["Bob"], 20)

    def test_doclist_to_json(self):
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        result = self.col.where("name").eq("Alice").run(fields=["name", "age"])
        result.to_json(path)

        with open(path) as f:
            data = json.load(f)
        self.assertEqual(data[0]["name"], "Alice")
        os.remove(path)

    def test_import_collection(self):
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        with open(path, "w", encoding="utf-8") as f:
            json.dump([{"name": "Imported", "age": 99}], f)

        self.col.import_(path)
        self.assertEqual(len(self.col.all()), 1)
        self.assertEqual(self.col.first()["name"], "Imported")
        os.remove(path)

    def test_import_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.col.import_("nonexistent.json")

    def test_replace_multiple_with_empty_doc(self):
        result = self.col.where("age").gte(25).replace({})
        self.assertEqual(result["replaced"], 3)
        all_docs = self.col.all()
        self.assertTrue(all(isinstance(d, dict) and not d for d in all_docs))

    def test_limit_only(self):
        result = self.col.where("age").gte(0).limit(2).run(fields=["name"])
        self.assertEqual(len(result), 2)

    def test_offset_only(self):
        result = self.col.where("age").gte(0).offset(1).run(fields=["name"])
        self.assertEqual(len(result), 2)

    def test_limit_and_offset(self):
        result = self.col.where("age").gte(0).offset(1).limit(1).run(fields=["name"])
        self.assertEqual(len(result), 1)

    def test_offset_out_of_range(self):
        result = self.col.where("age").gte(0).offset(100).run()
        self.assertEqual(len(result), 0)

    def test_limit_zero(self):
        result = self.col.where("age").gte(0).limit(0).run()
        self.assertEqual(len(result), 0)

    def test_lookup_many_orders_and_merge_total(self):
        users = db("multi_users")
        orders = db("multi_orders")
        users.clear()
        orders.clear()

        users.add_many(
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Carol"},
            ]
        )
        orders.add_many(
            [
                {"order_id": 101, "user_id": 1, "total": 10},
                {"order_id": 102, "user_id": 1, "total": 15},
                {"order_id": 103, "user_id": 2, "total": 20},
                {"order_id": 104, "user_id": 2, "total": 30},
                {"order_id": 105, "user_id": 2, "total": 25},
                # Carol has no orders
            ]
        )

        result = (
            users.lookup("multi_orders", "id", "user_id", "orders", many=True)
            .merge(lambda u: {"total_spent": sum(o["total"] for o in u["orders"])})
            .run()
            .as_list()
        )

        totals = {u["name"]: u["total_spent"] for u in result}
        self.assertEqual(totals["Alice"], 25)  # 10 + 15
        self.assertEqual(totals["Bob"], 75)  # 20 + 30 + 25
        self.assertEqual(totals["Carol"], 0)  # no orders

    def test_chained_query_with_logic_aggregate_and_find(self):
        users = db("logic_users")
        orders = db("logic_orders")
        users.clear()
        orders.clear()

        users.add_many(
            [
                {"id": 1, "name": "Neel", "vip": True, "age": 30},
                {"id": 2, "name": "Bea", "vip": False, "age": 25},
                {"id": 3, "name": "Tanaya", "vip": True, "age": 22},
            ]
        )
        orders.add_many(
            [
                {"order_id": 1, "user_id": 1, "total": 100},
                {"order_id": 2, "user_id": 1, "total": 50},
                {"order_id": 3, "user_id": 2, "total": 30},
                {"order_id": 4, "user_id": 3, "total": 25},
                {"order_id": 5, "user_id": 3, "total": 10},
            ]
        )

        result = (
            users.match_any(
                lambda q: q.where("vip").eq(True), lambda q: q.where("age").gt(23)
            )
            .lookup("logic_orders", "id", "user_id", "orders", many=True)
            .merge(
                lambda u: {"total_spent": sum(o["total"] for o in u.get("orders", []))}
            )
            .run(fields=["name", "vip", "total_spent"])
            .as_list()
        )

        names = [r["name"] for r in result]
        totals = {r["name"]: r["total_spent"] for r in result}
        self.assertIn("Neel", names)
        self.assertIn("Bea", names)
        self.assertIn("Tanaya", names)

        self.assertEqual(totals["Neel"], 150)
        self.assertEqual(totals["Bea"], 30)
        self.assertEqual(totals["Tanaya"], 35)

        for r in result:
            self.assertIn("vip", r)
            self.assertIn("total_spent", r)
        self.assertNotIn("age", r)  # `find()` excludes age


unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestCollectionManager)
)
