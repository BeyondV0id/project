# Dataset research — Indian food recognition and nutritional estimation

**Status:** research note, 8 November 2026  
**Scope:** datasets that can support the documented architecture, not a claim that every
dataset below is suitable for training or redistribution.

## Executive conclusion

There is no verified public dataset found in this review that simultaneously provides
Indian mixed-meal photographs, component masks, cooked/raw state, weighed component
masses, ingredients, Telugu/Hindi aliases, and independently measured nutrients. The
project should therefore keep its separation of concerns:

1. **Nutrition foundation:** a versioned, cited transcription of IFCT 2017, supplemented
   by a frozen USDA FoodData Central subset.
2. **Perception:** external image/segmentation datasets may be used for exploratory
   pretraining or sanity checks, but they are not Indian meal ground truth.
3. **Portion and end-to-end evaluation:** the proposed team-collected, weighed Indian
   meal dataset (`gold_v1`) is necessary. It is not an existing public dataset and must
   not be described as one.

This matches the architecture invariant that the VLM produces identities/regions only;
nutrient values and arithmetic come from the local SQLite knowledge base.

## Verified external datasets and sources

| Dataset/source | What is verified | Access, licence and size | Fit and limitations |
|---|---|---|---|
| **IFCT 2017 — Indian Food Composition Tables** | Published Indian composition tables by T. Longvah, R. Ananthan, K. Bhaskarachary and K. Venkaiah. The FAO/INFOODS Asia directory links the publication and its download site. It is the intended Indian ingredient source, with nutrient values by food and preparation/state where reported. | PDF/download via [FAO/INFOODS India entry](https://www.fao.org/infoods/infoods/tables-and-databases/asia/en/) → “Indian Food Composition Tables (2017)” → [ifct2017.com](http://www.ifct2017.com/). This review did not find an explicit open-data licence. Treat the book/PDF as copyrighted; transcribe only the required rows, preserve page/table references, and do not redistribute the scan. | **Best source for RAG and nutrition validation in the Indian context.** It is not an image dataset, has no bounding boxes or meal photos, and does not provide a universal recipe/portion model. The project’s “528 foods/~150 nutrients” is an implementation target from its design docs; confirm the exact count against the acquired edition before publishing it as a fact. |
| **USDA FoodData Central (FDC)** | Official USDA database with Foundation Foods, FNDDS, SR Legacy, Branded and other types; the API exposes search/details endpoints. | [Data documentation](https://fdc.nal.usda.gov/data-documentation/), [API guide](https://fdc.nal.usda.gov/api-guide/). Data are public domain/CC0; API key required, default limit documented as 1,000 requests/hour/IP. Download or cache a curated non-branded snapshot rather than depending on live calls. | **Best fallback/coverage source and cross-check.** It has nutrient and some portion data but weak representation of regional Indian recipes; FNDDS is US survey food, SR Legacy is historical, and branded values are not suitable as a universal ground truth. Keep source type, FDC ID, date and units. |
| **Nutrition5k** | The CVPR/arXiv paper reports about 5,000 real-world dishes with RGB/video, depth, component weights and high-accuracy calorie/macronutrient annotations. | [Paper and dataset description](https://arxiv.org/abs/2103.03375) (paper is CC BY 4.0; dataset access/terms must be checked at the linked release before use). The paper is the authoritative source for the labels and modalities. | **Useful for portion/nutrition pipeline sanity checks and an external comparison only.** It is cafeteria food, not Indian-focused; its capture setup and label distribution create domain shift. It does not replace `gold_v1`, and should not be mixed into Indian test metrics without a separate dataset report. |
| **FoodSeg103** | Ingredient-level semantic segmentation benchmark: 7,118 images, 103 food categories, pixel-wise masks; the dataset card describes 4,983 training and 2,135 validation images, curated from Recipe1M and human-refined. | [Dataset card/mirror](https://huggingface.co/datasets/EduardoPacheco/FoodSeg103), which identifies Apache-2.0 and links the originating paper as arXiv:2105.05409. Use the cited release and retain its licence/attribution files. | **Useful for segmentation/component-perception pretraining or a non-Indian sanity check.** It has no weighed masses, cooked/raw state or nutrient labels and is not a regional-Indian meal benchmark; it cannot validate this project’s component F1 on Indian plates. |
| **Food-101** | 101,000 images in 101 dish classes: 750 train and 250 manually reviewed test images per class; training images intentionally contain noise. | [ETH Zürich dataset page](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) and [Hugging Face mirror](https://huggingface.co/datasets/ethz/food101). The original page provides a 5 GB download and citation; check the current distribution terms before redistribution. | **Identity-classification smoke test only.** It has dish labels, no masks, masses, states, ingredients or nutrients, and is not an Indian mixed-meal benchmark. It must not be used to claim component F1 or calorie accuracy. |
| **Kaggle Indian Food Images Dataset (Sourav Banerjee)** | The dataset card states **4,000 images across 80 Indian food classes**, sourced from Google Images. Kaggle exposes a versioned ZIP (card version 5, approximately 372 MB) and requires Kaggle access/download. | [Dataset card](https://www.kaggle.com/datasets/iamsouravbanerjee/indian-food-images-dataset). The card says licence “Other (specified in description)” and does not provide a clear reusable image licence; source images are third-party web images. | **Exploratory Indian dish classification only, conditional on institutional permission.** It may supply class-name breadth, but labels are image-level, with no portions, states, masks, ingredients, Telugu/Hindi annotations or nutrition. Do not put it in a redistributable release or use it as gold evaluation unless image rights and provenance are audited. |
| **FAO/INFOODS directory and Asian tables** | FAO/INFOODS is a directory of regional food-composition tables, not one harmonized downloadable Indian dataset. Its India section lists IFCT 2017 and older *Nutritive Value of Indian Foods* and recipe/composition references. | [FAO/INFOODS tables directory](https://www.fao.org/infoods/infoods/tables-and-databases/en/) and [Asia directory](https://www.fao.org/infoods/infoods/tables-and-databases/asia/en/). Availability and rights vary by listed publication. | **Good discovery/citation source and historical alternative.** Older tables can help fill gaps or audit plausibility, but should not silently override IFCT values; record source and edition per row. |

### Datasets not found as verified public solutions

Searches did not substantiate a public, permissively licensed dataset with all of:
Indian regional meal images, component segmentation, cooked/raw labels, Telugu/Hindi
names, weighed portions and nutrient ground truth. “Indian food dataset” Kaggle
collections often aggregate Google/web images and provide only class folders. Recipe
websites and nutrition blogs are not composition datasets and should not be scraped into
the authoritative KB. A candidate is not accepted merely because a repository or paper
mentions a dataset; the project must record a working URL, version, licence and schema.

## Requirement-by-requirement assessment

| Requirement | Existing coverage | Project decision |
|---|---|---|
| Regional Indian dish identity | Partial: Kaggle Indian image set; dish names must be inspected from the released class list | Use only as optional exploratory data; create a reviewed alias table for English/Telugu/Hindi spellings |
| Telugu/Hindi names | Not verified as labels in the public image sets above | Team-authored aliases with provenance; aliases are retrieval metadata, not nutrient evidence |
| Cooked/raw/fried/gravy state | IFCT/FDC may distinguish preparation/state in records; image datasets do not provide reliable state labels | Required `physical_state` field in the local KB; annotate state in team images |
| Ingredients and recipes | IFCT/FDC are ingredient-level; Nutrition5k is not a recipe corpus; Kaggle image labels are not ingredients | Team recipe table for composite dishes, derived only from cited ingredient rows |
| Portions/masses | Nutrition5k has component weights but is non-Indian; the Indian image sets do not | Weigh every evaluation component; use the same session to calibrate density/heap factors |
| Calories/macros | IFCT/FDC provide composition values; Nutrition5k provides dish annotations | Calculate in Python from per-100 g rows; never use VLM- or web-stated calories as truth |

## Recommended use in this project

### (a) Knowledge base / RAG

Use **IFCT 2017 as the preferred Indian ingredient index**, with source code/page,
preparation state, units and transcription provenance. Add a **frozen, curated USDA
FDC snapshot** for missing foods and cross-checking; prefer Foundation/SR Legacy and
selected FNDDS records, and exclude branded records by default. Store both sources,
never merge conflicting nutrient values. Build the planned `foods` index from these
rows and the planned `dishes` index from transparent, team-authored recipes whose
ingredient fractions point back to IFCT/FDC records. The alias table may include
Telugu/Hindi/common spellings, but aliases must not create nutrient values.

### (b) Image perception and evaluation

Use the **Kaggle Indian set only for exploratory class breadth** after a licence audit.
Use **Food-101** as a generic identity smoke test if its distribution terms permit it.
Use **Nutrition5k** only as an external nutrition/portion comparison. Do not report
these datasets as Indian mixed-meal component benchmarks. The actual component
recognition test must be the held-out meal split of `gold_v1`, with meal-level (not
image-level) separation.

### (c) Portion estimation

No public Indian dataset found here is adequate. Use `gold_v1`: plate diameter or a
known object as an image anchor, component mass measured on a kitchen scale, capture
angle/lighting metadata, and repeated views of the same meal. Nutrition5k can validate
the mechanics of a mass/nutrition evaluation harness, but its domain gap must be
reported and its data must not calibrate Indian density factors.

### (d) Nutrition validation

Use **IFCT 2017 × weighed mass** as the primary reference, with explicit kJ-to-kcal
conversion and `NULL` for unreported nutrients. Use the frozen USDA snapshot for
covered foods and a source-level disagreement audit. For each composite dish, compute
the reference from the recorded ingredient recipe and masses; do not compare against
an app, recipe blog or VLM answer. Nutrition5k is a secondary external comparison,
not the Indian validation set.

## Proposed/team-created data (not existing datasets)

The architecture’s `gold_v1` plan is a **new team dataset**: 150 images from 60
distinct meals, 25 single-item and 35 mixed plates, 3–4 views per meal, component
bounding boxes, canonical food IDs, preparation state, plate/anchor metadata, and
scale-measured masses. It should include Telugu/Hindi names as aliases where speakers
confirm them, not as guessed translations. Ground-truth calories/macros are generated
offline from the versioned IFCT/FDC rows. Split by meal (60/20/20), not by photograph,
to prevent the same plate appearing in train and test.

Also proposed, not public: the `dish_recipes.csv` composite table, `portion_model.csv`
density/heap factors, and `aliases.csv`. Every record should carry `source_ref`,
`kb_version`, preparation state and an annotation/provenance note. Team-captured
images require consent, anonymisation and a redistribution decision; keep them local
if participant permissions do not allow publication.

## Practical acquisition and audit checklist

Before adding any external data, record dataset name/version, URL, download date,
checksum, licence text, image/label count, class list, annotation schema and known
duplicates. For Kaggle/web-image data, retain only a private research copy unless
rights are clear. For IFCT, perform the planned double transcription and third-person
resolution, retaining page numbers. For FDC, pin the release date and cache API
responses. For `gold_v1`, publish the annotation protocol, weighing precision,
annotator agreement, exclusions and meal-level split.

## Primary citations

1. Longvah, Ananthan, Bhaskarachary & Venkaiah, *Indian Food Composition Tables
   (2017)* — [FAO/INFOODS Asia directory entry](https://www.fao.org/infoods/infoods/tables-and-databases/asia/en/).
2. USDA ARS, *FoodData Central* — [data documentation](https://fdc.nal.usda.gov/data-documentation/)
   and [API guide](https://fdc.nal.usda.gov/api-guide/).
3. Thames et al., “Nutrition5k: Towards Automatic Nutritional Understanding of Generic
   Food,” CVPR 2021 — [arXiv:2103.03375](https://arxiv.org/abs/2103.03375).
4. Bossard, Guillaumin & Van Gool, “Food-101 — Mining Discriminative Components with
   Random Forests,” ECCV 2014 — [ETH Zürich dataset page](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/).
5. Banerjee, *Indian Food Images Dataset* — [Kaggle dataset card](https://www.kaggle.com/datasets/iamsouravbanerjee/indian-food-images-dataset).
6. FoodSeg103, “A Dataset for Food Ingredient Segmentation” — [dataset card and
   paper metadata](https://huggingface.co/datasets/EduardoPacheco/FoodSeg103).
