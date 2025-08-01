from pathlib import Path
from reducto import Reducto

client = Reducto()
# Replace with your file path
upload = client.upload(file=Path("just_words_founding_product_engineer.pdf"))

schema = {
  "type": "object",
  "properties": {
    "companyName": {
      "type": "string",
      "description": "Name of the company offering the job."
    },
    "jobTitle": {
      "type": "string",
      "description": "Title of the job position."
    },
    "jobRequirements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "requirement": {
            "type": "string",
            "description": "A single job requirement."
          }
        },
        "required": [
          "requirement"
        ]
      },
      "description": "List of job requirements."
    }
  },
  "required": [
    "companyName",
    "jobTitle",
    "jobRequirements"
  ]
}
system_prompt = "Be precise, thorough, and accurate."
generate_citations = True
include_images = False

result = client.extract.run(
    document_url=upload,
	schema=schema,
	system_prompt=system_prompt,
	generate_citations=generate_citations,
	include_images=include_images
)