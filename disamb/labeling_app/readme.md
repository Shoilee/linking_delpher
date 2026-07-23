# Labeling app

To run the labeling app, use the following command:

`stramlit run path/to/app.py`

You can upload a csv file with at least the columns:
- `name`
- `name_id`
- `candidate`

It is also possible to upload an already (partially) annotated file. This is usefull if you want to review an annotated file, or just want to continue annotating.

After uploading, the first name_id group will be shown, with a column `is_match`, containing a checkbox in front of each name-candidate row. A column `annotated` will also be added, indiciating if a block is annotated or not. You can later use this to filter out blocks you skipped or did not annotate (yet).

If you click on 'next & save' or 'previous & save', the annotation will be saved, and the `annotated` column for this group will be set to `True`. To exclude an already annotated block, click on the 'skip example' button. Under the title 'Labeling Block: n / N', the text after 'Block status:' indicates if a block is annotated or not.

Clicking on 'save labeled file' will download the annotated file (in csv), with the same filename as the input file, with the suffix '_labeled' and a timestamp.