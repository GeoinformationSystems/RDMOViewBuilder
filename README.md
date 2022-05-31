# RDMOViewBuilder

RDMOViewBuilder offers a small tool to build a view to be imported in RDMO. The view takes a catalog xml file as input,
e.g. generated with the [RDMOCatalogBuilder](https://github.com/GeoinformationSystems/RDMOCatalogBuilder).

## Usage

To use RDMOViewBuilder type the following:

```python
import BuildView

BuildView.control_create_view("infiles/qa_questions.xml", en="outfiles/qa_questions_view_template_en.xml")
```

This produces an example view for the catalog in infiles/qa_questions.xml. The title gets `<h1>`, a section `<h2>`, a
questionset `<h3>`. The questions are written in bold letters, help texts italic. Collections in questionsets as well as
collections in questions are taken into account.

RDMOViewBuilder creates a view draft including each question from the given catalog. For specific purposes, the view
can be adapted to the user's needs. This is best done via interface in RDMO management.

## Structure

The project comprises the module BuildView.py with all necessary code. The input and output file arguments can be either
directly written into main method or used like shown in usage above.

## Output Files

RDMOViewBuilder produces view drafts as xml. If desired, multiple languages can be given. As the RDMO views only
comprise one language, multiple view files must be generated.

### Example Files

This project includes several example files:

- `infiles/example1_questions.xml`: this catalog gives an example with different types of answers including options
- `infiles/example2_questions.xml`: this catalog includes questionsets with collections
- `infiles/qa_questions.xml`: this is the quality assurance catalog
  from [RDMOCatalogBuilder](https://github.com/GeoinformationSystems/RDMOCatalogBuilder)
- `outfiles/example1_view_template_de.xml`: view template to be imported into RDMO from example1_questions.xml in German
- `outfiles/example1_view_template_en.xml`: view template to be imported into RDMO from example1_questions.xml in
  English
- `outfiles/qa_questions_view_template_en.xml`: view template to be imported into RDMO from qa_questions.xml
- `outfiles/qa_curation_view_template_en.xml`: view template manually revised in RDMO and exported from there;
  qa_questions_view_template_en.xml was used to create a specified curation view

## Known Limits/Bugs

## License

The RDMOViewBuilder is licensed under Apache-2.0. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

## Contact

Michael Wagner ([michael.wagner@tu-dresden.de](mailto:michael.wagner@tu-dresden.de))