import copy, importlib.util, json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evaluate',R/'scripts/evaluate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REPORT=json.loads((R/'data/recorded-results.json').read_text());CASES={c['id']:c for c in REPORT['cases']}

class EvidenceTests(unittest.TestCase):
    def test_all_fixtures_match_recorded_hashes(self):
        for c in CASES.values():m.verify_case(c)
    def test_all_vectors_and_predictions_are_valid(self):
        for c in CASES.values():m.validate_response(c['output'],c['payload']['options'])
    def test_context_pair_changes_only_state(self):
        a,b=CASES['context-arrival'],CASES['context-inspection']
        self.assertEqual(a['sha256'],b['sha256'])
        for key in ['question','options','modality']:self.assertEqual(a['payload'][key],b['payload'][key])
        self.assertNotEqual(a['payload']['state'],b['payload']['state'])
    def test_image_controls_keep_prompt_fixed(self):
        for name in ['closed','restricted']:
            self.assertEqual(CASES['context-arrival']['payload'],CASES['context-arrival-'+name]['payload'])
            self.assertNotEqual(CASES['context-arrival']['sha256'],CASES['context-arrival-'+name]['sha256'])
    def test_response_validation_rejects_missing_option(self):
        c=copy.deepcopy(CASES['open']);c['output']['probabilities'].pop(c['payload']['options'][0])
        with self.assertRaises(ValueError):m.validate_response(c['output'],c['payload']['options'])
    def test_response_validation_rejects_nonfinite_values(self):
        c=copy.deepcopy(CASES['open']);c['output']['probabilities'][c['payload']['options'][0]]=float('nan')
        with self.assertRaises(ValueError):m.validate_response(c['output'],c['payload']['options'])
    def test_response_validation_rejects_wrong_prediction(self):
        c=copy.deepcopy(CASES['open']);c['output']['prediction']='unlisted answer'
        with self.assertRaises(ValueError):m.validate_response(c['output'],c['payload']['options'])
    def test_response_validation_rejects_unnormalized_scores(self):
        c=copy.deepcopy(CASES['open']);c['output']['probabilities'][c['payload']['options'][0]]=.9
        with self.assertRaises(ValueError):m.validate_response(c['output'],c['payload']['options'])

if __name__=='__main__':unittest.main()
