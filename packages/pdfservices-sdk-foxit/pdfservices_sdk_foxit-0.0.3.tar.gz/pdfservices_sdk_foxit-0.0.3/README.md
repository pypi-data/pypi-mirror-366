# Foxit PDF Services SDK

This SDK lets developers more easily use the Foxit APIs, including [PDF Services](https://developer-api.foxit.com/pdf-services/) and [Document Generation](https://developer-api.foxit.com/document-generation/). You will need a [free set of credentials](https://app.developer-api.foxit.com/pricing) in order to call the APIs.

## Usage

Copy your credentials to the environment and then instantiate the SDK. Here's a sample:

```python
import pdf_service_sdk
import os 

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

sdk = pdf_service_sdk.PDFServiceSDK( client_id=CLIENT_ID,
                                     client_secret=CLIENT_SECRET)
```

Generally speaking, moist methods handle upload and download for you, checking the task and so forth so you don't need it. For example:

```python
sdk.word_to_pdf(input_path="../../inputfiles/input.docx",output_path="../../output/output_from_sdk.pdf")
print("Conversion completed successfully. Check the output file at ../../output/output_from_sdk.pdf")

# Handle it simpler
sdk.conversion(input_path="../../inputfiles/input.docx",output_path="../../output/output_from_sdk_v2.pdf")
print("Conversion (second version) completed successfully. Check the output file at ../../output/output_from_sdk_v2.pdf")
```

## Methods Supported

* conversion(input_path, output_path) - general conversion method
* excel_to_pdf, html_to_pdf, image_to_pdf, pdf_to_excel, pdf_to_html, pdf_to_image, pdf_to_powerpoint, pdf_to_text, pdf_to_word, powerpoint_to_word, text_to_pdf, word_to_pdf - all take an input_path and output_path argument
* url_to_pdf(url, output_path) - convert a URL to pdf
* extract(input_path, output_path, type (one of TEXT, IMAGE, PAGE), page_range) - extracts either text, images (zip), or pages (new pdf)
* download(doc_id, output_path) - given a document id and path, will stream the data down
* upload(path) - upload a document and return a path
* compress(input_path,output_path,compressionLevel) - compresses a PDF, default level is LOW
* linearize(input_path,output_path) - linearizes a PDF
* flatten(input_path,output_path) - flattens a PDF
* combine(input_path[], output_path, config) - combines an array of file paths
* split(input_path, output_path, page_count) - splits a PDF into page_count files, returns a zip
* compare(input_path, second_path, config, output_path) - compares two PDFs. You can leave off output_path and get the JSON directly, but if you ask for a PDF result, ensure you pass it.
* docgen(input_path, output_path, data) - Runs document generation on an input Word file and returns a dynamic PDF or Word file based on `data`

## To Do: 

* remove-password, protect, manipulate
* Make output path optional and just return the doc id
* Make checking a task public and a utility pollTask to handle repeating (this and the previous two methods would let devs chain calls)
* Modify extract so you can leave off output_path when working with JSON

## History 

| Date | Change |
|------|-----------|
| 7/31/2025 | Added docgen, support for passing in docgen credentials |
| 7/30/2025 | Added split and compare |
| 7/23/2025 | Just updated the doc to reflect combine being added. |
