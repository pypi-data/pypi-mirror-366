import unittest 
import json
import sys
import os 

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src/pdfservices_sdk_foxit'))
sys.path.append(target_dir)
from pdf_service_sdk import PDFServiceSDK 
class TestPDFServiceSDK(unittest.TestCase):

	def setUp(self):
		self.sdk = PDFServiceSDK(os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'), docgen_client_id=os.environ.get('DG_CLIENT_ID'),docgen_client_secret=os.environ.get('DG_CLIENT_SECRET'))
		self.thisdir = os.path.dirname(os.path.abspath(__file__))
		
	def test_upload(self):
		result = self.sdk.upload(f'{self.thisdir}/input/input.docx')
		self.assertIsNotNone(result)

	def test_word_to_pdf(self):
		self.sdk.word_to_pdf(f'{self.thisdir}/input/input.docx', f'{self.thisdir}/output/output.pdf')
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output.pdf'))		

	def test_combine(self):
		inputs = [f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/input/second.pdf']
		self.sdk.combine(inputs, f'{self.thisdir}/output/output_combined.pdf')
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output_combined.pdf'))		

	"""
	Currently there isn't a way to confirm the option *worked*, but I want to ensure 
	it doesn't throw at least.
	"""
	def test_combine_with_options(self):
		inputs = [f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/input/second.pdf']
		config = {
			"addBookmark":False
		}
		self.sdk.combine(inputs, f'{self.thisdir}/output/output_combined_nobookmarks.pdf',config)
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/output_combined_nobookmarks.pdf'))		

	def test_split_pdf(self):
		self.sdk.split(f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/output/splitoutput.zip', 2)
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/splitoutput.zip'))

	def test_compare(self):
		res = self.sdk.compare(f'{self.thisdir}/input/input.pdf', f'{self.thisdir}/input/second.pdf', {
			"compareType":"ALL",
			"resultType":"JSON"
			})
		
		try:
			json.loads(res)
			is_valid_json = True
		except ValueError:
			is_valid_json = False

		self.assertTrue(is_valid_json)

	def test_docgen(self):
		data = {
			"name":"Raymond Camden",
			"food":"sushi",
			"favoriteMovie":"Star Wars",
			"cats":[
				{"name":"Mittens", "gender":"female", "age":3},
				{"name":"Crackers", "gender":"male", "age":10},
			]
		}

		self.sdk.docgen(f'{self.thisdir}/input/docgen_sample.docx', f'{self.thisdir}/output/dg_output.pdf', data)
		self.assertTrue(os.path.exists(f'{self.thisdir}/output/dg_output.pdf'))


if __name__ == '__main__':
	unittest.main()