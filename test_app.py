import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import facts_from_text, build_guidance, make_complaint

class NyayaAITests(unittest.TestCase):
    def test_refund_amount(self):
        f = facts_from_text("I paid ₹3,499 and my refund is pending")
        self.assertEqual(f["issue_type"], "refund")
        self.assertEqual(f["amount_inr"], "3499")
    def test_non_delivery(self):
        self.assertEqual(facts_from_text("My order was not delivered")["issue_type"], "non_delivery")
    def test_defective(self):
        self.assertEqual(facts_from_text("The product is damaged")["issue_type"], "defective")
    def test_guidance_has_nch(self):
        g = build_guidance("refund", "ShopApp", "", "", "invoice, payment proof", "Refund pending")
        self.assertTrue(any("1915" in x for x in g["next_steps"]))
    def test_complaint_uses_user_facts(self):
        d = make_complaint("Asha", "Kochi, Kerala", "ShopApp", "OD123", "refund", "3499", "2026-11-02", "Refund pending", "Full refund")
        self.assertIn("OD123", d)
        self.assertIn("Full refund", d)

if __name__ == "__main__": unittest.main()
