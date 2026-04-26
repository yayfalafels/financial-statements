---
title: Category and Account Model Translation
doc_type: design
scope: poc
---
# Category and Account Model Translation

## Table of contents

- [Purpose](#purpose)
- [Source reference inventory](#source-reference-inventory)
- [Stage 1 — cat_map: HomeBudget category to GL code](#stage-1--cat_map-homebudget-category-to-gl-code)
- [Stage 2 — fin_exp_cat_map: GL code to financial statement category](#stage-2--fin_exp_cat_map-gl-code-to-financial-statement-category)
- [Stage 2 — accounts: account classification](#stage-2--accounts-account-classification)
- [End-to-end translation to new model](#end-to-end-translation-to-new-model)
- [Gap analysis](#gap-analysis)

## Purpose

This document captures the one-time translation of the legacy two-stage category and account classification pipeline into the new category and account model vocabulary. It is the design-time evidence base for implementing the category management module and account registry. Design and implementation do not need to refer back to primary sources after this document is complete.

The legacy pipeline has three relevant primary sources:

- `cat_map` region in `gsheet/homebudget-workbook.json` — stage 1, HomeBudget category to GL code
- `fin_expense_cat_map` region in `gsheet/financial-statements.json` — stage 2, GL code to financial statement category
- `accounts` region in `gsheet/financial-statements.json` — stage 2, account classification

The new model vocabulary and canonical field names are defined in `docs/requirements/transaction-categories.md` and `docs/requirements/account-classification.md`.

## Source reference inventory

| id | source                   | config file                      | region              | rows | cols |
| -- | ------------------------ | -------------------------------- | ------------------- | ---- | ---- |
| 01 | HomeBudget workbook      | gsheet/homebudget-workbook.json  | cat_map             | 181  | 10   |
| 02 | Financial statements wkb | gsheet/financial-statements.json | fin_expense_cat_map | 33   | 5    |
| 03 | Financial statements wkb | gsheet/financial-statements.json | accounts            | 29   | 7    |

Inspection artifacts:

- cat_map: `.dev/.artifacts/stage2_sources_inspection.json`
- fin_expense_cat_map: `.dev/.artifacts/stage2_sources_inspection.json`
- accounts: `.dev/.artifacts/stage2_sources_inspection.json`

Inspection commands:

```powershell
env\Scripts\python.exe .dev\scripts\python\inspect_cat_map.py
env\Scripts\python.exe .dev\scripts\python\inspect_stage2_sources.py
```

## Stage 1 — cat_map: HomeBudget category to GL code

### Schema

The `cat_map` region has 181 rows and 10 columns.

| id | column         | description                                                              |
| -- | -------------- | ------------------------------------------------------------------------ |
| 01 | hb_budget_cat  | composite key: HB account + HB category + HB subcategory                |
| 02 | budget         | legacy budget center (HB account context for the mapping row)            |
| 03 | cat_id         | legacy category numeric identifier                                       |
| 04 | category       | HomeBudget parent category name                                          |
| 05 | subcategory    | HomeBudget subcategory name                                              |
| 06 | fa_cat_id      | legacy GL category numeric identifier                                    |
| 07 | fa_budget      | legacy GL budget group (01 TWH personal, 02 household, 05 TWH taxes)     |
| 08 | fa_category    | GL category code — primary mapping output                                |
| 09 | fa_subcategory | GL subcategory code — secondary mapping output when fa_category is blank |
| 10 | account        | destination account for cost-center transfer routing                     |

The mapping key is `hb_budget_cat`, which combines budget center, HB category, and subcategory context. For most category-subcategory combinations there is one mapping row. Some combinations have multiple rows where the mapping differs by account context.

### HomeBudget category to GL code rules

The 15 distinct HomeBudget parent categories and their GL category assignments are as follows.

**Food (Basic)**

| id | hb subcategory    | fa_category  | fa_subcategory | note                                           |
| -- | ----------------- | ------------ | -------------- | ---------------------------------------------- |
| 01 | Cheap restaurant  | 01 food      |                |                                                |
| 02 | Food Court        | 01 food      |                |                                                |
| 03 | Groceries         | 01 food      |                |                                                |
| 04 | meal prep         | 01 food      |                |                                                |

**Health and Wellness**

| id | hb subcategory          | fa_category      | fa_subcategory | note                                           |
| -- | ----------------------- | ---------------- | -------------- | ---------------------------------------------- |
| 01 | Grooming                | 03 healthcare OOP |               |                                                |
| 02 | Haircut                 | 03 healthcare OOP |               |                                                |
| 03 | Health insurance        | 04 insurance     |                |                                                |
| 04 | Medical expenses        | 03 healthcare OOP |               |                                                |
| 05 | Medical supplies        | 03 healthcare OOP |               |                                                |
| 06 | Fitness                 | 09 discretionary |                | classified discretionary, not COLE healthcare  |
| 07 | Massage                 | 09 discretionary |                | classified discretionary, not COLE healthcare  |
| 08 | Medical - sexual health | 09 discretionary |                | legacy; some rows mapped to 11 sexual health   |

**Household**

| id | hb subcategory      | fa_category      | fa_subcategory | note                      |
| -- | ------------------- | ---------------- | -------------- | ------------------------- |
| 01 | Maintenance         | 09 maintenance   |                |                           |
| 02 | Pet and Plants      | 14 pets and plants |              |                           |
| 03 | Sundries            | 08 sundries      |                | some rows have empty fa_category (see gaps) |
| 04 | Cleaning service    | 09 discretionary |                |                           |
| 05 | Durable goods       | 09 discretionary |                |                           |
| 06 | Furniture & decorations | 09 discretionary |           |                           |

**Personal Discretionary**

| id | hb subcategory         | fa_category      | fa_subcategory | note                       |
| -- | ---------------------- | ---------------- | -------------- | -------------------------- |
| 01 | Clothing               | 06 clothing      |                |                            |
| 02 | Shoes                  | 06 clothing      |                | grouped with clothing      |
| 03 | Books                  | 09 discretionary |                |                            |
| 04 | Cloud data             | 09 discretionary |                |                            |
| 05 | Donations              | 09 discretionary |                |                            |
| 06 | Education              | 09 discretionary |                |                            |
| 07 | IT                     | 09 discretionary |                |                            |
| 08 | Jewelry and Accessories | 09 discretionary |               |                            |

**Professional Services**

| id | hb subcategory     | fa_category      | fa_subcategory | note                        |
| -- | ------------------ | ---------------- | -------------- | --------------------------- |
| 01 | Post               | 07 post          |                |                             |
| 02 | Agent              | 09 discretionary |                |                             |
| 03 | Banking            | 09 discretionary |                |                             |
| 04 | Counseling         | 09 discretionary |                |                             |
| 05 | Currency conversion | 09 discretionary |               |                             |
| 06 | Legal              | 09 discretionary |                |                             |

**Project**

| id | hb subcategory                | fa_category  | fa_subcategory | note                                     |
| -- | ----------------------------- | ------------ | -------------- | ---------------------------------------- |
| 01 | AI ML, AWS lifehacks, DS qual | 10 project   |                |                                          |
| 02 | Gatech OMS masters            | 10 project   |                |                                          |
| 03 | MCFPipe, PR REP, Echelon AI   | 10 project   |                |                                          |
| 04 | carbon offset/outreach        | 09 discretionary |           |                                          |
| 05 | Paris Trip 2023, Trip US 2024 | 09 discretionary |           | trips classified as discretionary        |

**Rent**

| id | hb subcategory | fa_category      | fa_subcategory | note                                         |
| -- | -------------- | ---------------- | -------------- | -------------------------------------------- |
| 01 | Rent           | 01 rental        |                |                                              |

**Social & Entertainment**

All subcategories map to `09 discretionary`. No Social & Entertainment subcategory maps to a COLE expense line.

| id | hb subcategory          | fa_category       | note                            |
| -- | ----------------------- | ----------------- | ------------------------------- |
| 01 | Alcohol                 | 09 discretionary  |                                 |
| 02 | Date night dinner       | 09 discretionary  |                                 |
| 03 | Dating                  | 09 discretionary  |                                 |
| 04 | Drinks - nonalcoholic   | 09 discretionary  |                                 |
| 05 | Events and others       | 09 discretionary  |                                 |
| 06 | Family                  | 09 discretionary  |                                 |
| 07 | Friends                 | 09 discretionary  |                                 |
| 08 | Gifts                   | 09 discretionary  |                                 |

**Taxes and Fines**

| id | hb subcategory         | fa_category         | note                                              |
| -- | ---------------------- | ------------------- | ------------------------------------------------- |
| 01 | Taxes - income         | 02 income tax SGP   | not an expense line; maps to tax income reduction |
| 02 | Taxes - other          | 02 income tax SGP   |                                                   |
| 03 | Gov subsidy            | 02 income tax SGP   | subsidy as negative tax                           |
| 04 | Fines                  | 09 discretionary    |                                                   |
| 05 | unauthorized transaction | 09 discretionary  |                                                   |

**Transport**

| id | hb subcategory            | fa_category       | note                                               |
| -- | ------------------------- | ----------------- | -------------------------------------------------- |
| 01 | MRT                       | 02 local transport |                                                   |
| 02 | Bike                      | 09 discretionary  |                                                   |
| 03 | Taxi - bulky Items        | 09 discretionary  | most taxi subcategories are discretionary          |
| 04 | Taxi - isolated location  | 09 discretionary  |                                                    |
| 05 | Taxi - late night         | 09 discretionary  |                                                    |
| 06 | Taxi - miss bus           | 09 discretionary  |                                                    |
| 07 | Taxi - rain               | 09 discretionary  |                                                    |
| 08 | Taxi - time constraint    | 09 discretionary  |                                                    |
| 09 | Taxi - work               | 09 discretionary  |                                                   |

Only MRT maps to the COLE `transport` line. All taxi subcategories are classified as discretionary.

**Travel**

| id | hb subcategory | fa_category      | note                   |
| -- | -------------- | ---------------- | ---------------------- |
| 01 | Lodging        | 09 discretionary |                        |

**Utilities**

| id | hb subcategory | fa_category    | note |
| -- | -------------- | -------------- | ---- |
| 01 | Electricity    | 07 electricity |      |
| 02 | Gas            | 05 gas         |      |
| 03 | Internet/TV    | 03 internet    |      |
| 04 | Mobile         | 05 mobile      |      |
| 05 | PUB other      | 06 utilities misc |   |
| 06 | Water          | 04 water       |      |

All Utilities subcategories map to COLE GL codes.

**Balancing, Reimbursable, helva**

These are administrative or deprecated categories. Helva was a legacy budget center that is no longer in use. All rows map to `09 discretionary`. They are not included in any COLE or rental expense line.

### Legacy budget groups

The `fa_budget` field assigns each mapping row to one of four legacy budget groups.

| id | fa_budget         | description                                    |
| -- | ----------------- | ---------------------------------------------- |
| 01 | 01 TWH personal   | personal spending center transactions          |
| 02 | 05 TWH taxes      | income tax and government subsidy transactions |
| 03 | 06 external       | external account routing (non-personal)        |

These groups are a legacy artifact and are retired in the new model. The `02 household` budget group is deprecated along with the common and helva budget centers — only `01 TWH personal` produced data after that deprecation. The `category_group_key` in the new model is determined at stage 2 by the `fin_stm_category` and COLE flag, not by `fa_budget`.

## Stage 2 — fin_exp_cat_map: GL code to financial statement category

### Schema

The `fin_expense_cat_map` region has 33 rows and 5 columns.

| id | column           | description                                                                       |
| -- | ---------------- | --------------------------------------------------------------------------------- |
| 01 | fin_stm_category | financial statement expense line label — corresponds to `gl_code` in new model   |
| 02 | COLE             | 1 if COLE expense, 0 if not COLE — determines category_group_key                 |
| 03 | fa_category      | GL category code from stage 1 (populated when matching at category level)        |
| 04 | fa_subcategory   | GL subcategory code from stage 1 (populated when matching at subcategory level)  |
| 05 | custom logic     | override or multi-match note; non-empty for exception rows                       |

The join from `hb_gl` to `fin_exp_cat_map` uses either `fa_category` or `fa_subcategory` as the lookup key, matching whichever field is populated for that row. One `fin_stm_category` may correspond to multiple `fa_category`/`fa_subcategory` values — see multi-row aggregation below.

### Full fin_exp_cat_map table

| id | fin_stm_category    | COLE | fa_category       | fa_subcategory                           | custom logic                                         |
| -- | ------------------- | ---- | ----------------- | ---------------------------------------- | ---------------------------------------------------- |
| 01 | food                | 1    | 01 food           |                                          |                                                      |
| 02 | transport           | 1    | 02 local transport | 01 taxi                                 |                                                      |
| 03 | healthcare OOP      | 1    | 03 healthcare OOP |                                          |                                                      |
| 04 | insurance           | 1    | 04 insurance      |                                          |                                                      |
| 05 | mobile              | 1    | 05 mobile         |                                          |                                                      |
| 06 | clothing personal items | 1 | 06 clothing      |                                          |                                                      |
| 07 | post                | 1    | 07 post           |                                          |                                                      |
| 08 | fitness             | 0    |                   | 14 fitness                               |                                                      |
| 09 | non alcoholic drinks | 0   |                   | 02 non alcoholic drinks                  |                                                      |
| 10 | alcohol             | 0    |                   | 03 alcohol                               |                                                      |
| 11 | socializing         | 0    |                   | 13 socializing                           |                                                      |
| 12 | socializing         | 0    |                   | 12 dating                                |                                                      |
| 13 | IT software         | 0    |                   | 04 IT services                           |                                                      |
| 14 | IT hardware         | 0    |                   | 05 electronic devices                    |                                                      |
| 15 | books               | 0    |                   | 07 books and education                   |                                                      |
| 16 | travel              | 0    |                   | 09 travel                                |                                                      |
| 17 | misc discretionary  | 0    | 12 discretionary  |                                          | deprecated — common/helva budget only; produces no matches in single cost center model |
| 18 | misc discretionary  | 0    | 9 discretionary   |                                          |                                                      |
| 19 | higher education    | 0    |                   | 12 project: DS qualifications            |                                                      |
| 20 | higher education    | 0    |                   | 18 project: GT online masters analytics  |                                                      |
| 21 | projects            | 0    | 10 project        |                                          |                                                      |
| 22 | rental              | 0    | 01 rental         |                                          |                                                      |
| 23 | Singtel internet    | 1    | 03 internet       |                                          |                                                      |
| 24 | PUB water/gas       | 1    | 04 water          |                                          |                                                      |
| 25 | PUB water/gas       | 1    | 05 gas            |                                          |                                                      |
| 26 | PUB water/gas       | 1    | 06 utilities misc |                                          |                                                      |
| 27 | electricity         | 1    | 07 electricity    |                                          |                                                      |
| 28 | sundries            | 1    | 08 sundries       |                                          |                                                      |
| 29 | maintenance         | 1    | 09 maintenance    |                                          |                                                      |
| 30 | pets and plants     | 0    | 14 pets and plants |                                         |                                                      |
| 31 | durables            | 0    |                   | 01 durables                              |                                                      |
| 32 | cleaning service    | 0    |                   | 02 cleaning services                     |                                                      |
| 33 | family gifts        | 0    |                   | 10 family gifts                          |                                                      |

### Category group derivation from COLE flag

The COLE flag drives the `category_group_key` assignment in the new model:

- `COLE = 1` → `cole_expenses`
- `COLE = 0` and `fin_stm_category = 'rental'` → `rental_expenses`
- `COLE = 0` and `fin_stm_category != 'rental'` → `discretionary_expenses`

### Multi-row aggregation cases

Three `fin_stm_category` values aggregate from multiple `fa_category`/`fa_subcategory` source values.

**socializing** — aggregates two legacy GL subcategory codes:

- `13 socializing` — general socializing with friends and events
- `12 dating` — date-related social spending

**PUB water/gas** — aggregates three legacy GL category codes:

- `04 water` — water bill
- `05 gas` — gas bill
- `06 utilities misc` — PUB catch-all for other utility charges

**misc discretionary** — `9 discretionary` is the active GL category code in the single-cost-center model. The `12 discretionary` code was the common/household discretionary catch-all and is deprecated — it produces no matches after helva and common budget retirement. Custom logic: matches if `fa_category` is `9 discretionary` and the transaction has not already been captured by a more specific subcategory line item.

**higher education** — aggregates two legacy GL subcategory codes tied to named projects:

- `12 project: DS qualifications`
- `18 project: GT online masters analytics`

These project subcategory codes encode specific academic programs. In the new model, all higher education spending aggregates to the `higher_education` expense line regardless of the specific program name.

## Stage 2 — accounts: account classification

### Schema

The `accounts` region has 29 rows and 7 columns.

| id | column      | description                                                             |
| -- | ----------- | ----------------------------------------------------------------------- |
| 01 | id          | account identifier used in the financial statements workbook            |
| 02 | type        | asset subcategory — determines balance sheet placement                  |
| 03 | owner       | account owner code (TWH = primary holder, COM = common/shared)         |
| 04 | name        | short account tag                                                       |
| 05 | currency    | account reporting currency                                              |
| 06 | HB account  | matching account name in HomeBudget                                     |
| 07 | stm account | matching account key in statements.db; blank if not in statement path  |

### Full accounts table

| id | account_id              | type            | owner | name             | currency | HB account         | stm account         |
| -- | ----------------------- | --------------- | ----- | ---------------- | -------- | ------------------ | ------------------- |
| 01 | TWH CASH SGD            | wallet cash     | TWH   | CASH             | SGD      | Cash TWH SGD       |                     |
| 02 | TWH CASH USD            | wallet cash     | TWH   | CASH             | USD      | Cash TWH USD       |                     |
| 03 | TWH AMAZON USD          | wallet cash     | TWH   | AMAZON           | USD      | TWH Amazon         |                     |
| 04 | TWH EZLINK SGD          | wallet cash     | TWH   | EZLINK           | SGD      | TWH EZLink         |                     |
| 05 | TWH EZCASH SGD          | wallet cash     | TWH   | EZCASH           | SGD      | EZCash             |                     |
| 06 | TWH EZ MC SGD           | wallet cash     | TWH   | EZ MC            | SGD      | EZ MasterCard      |                     |
| 07 | COM UOB SGD             | bank account    | COM   | UOB              | SGD      | Common UOB         | Common UOB          |
| 08 | TWH DBS MULTI SGD       | bank account    | TWH   | DBS MULTI        | SGD      | TWH DBS Multi SGD  | TWH DBS Multi SGD   |
| 09 | TWH CITI USD            | bank account    | TWH   | CITI             | USD      | TWH CITI           | TWH CITI            |
| 10 | TWH WF USD              | bank account    | TWH   | WF               | USD      | WF USD             |                     |
| 11 | TWH HELVA UOB SGD       | bank account    | TWH   | HELVA UOB        | SGD      | helva UOB          |                     |
| 12 | TWH BOA VISA USD        | credit card     | TWH   | BOA VISA         | USD      | TWH Visa USD       | TWH Visa USD        |
| 13 | TWH DBS VISA SGD        | credit card     | TWH   | DBS VISA         | SGD      | TWH DBS Visa SGD   | TWH DBS Visa SGD    |
| 14 | TWH UOB ONE SGD         | credit card     | TWH   | UOB ONE          | SGD      | TWH UOB One SGD    | TWH UOB One SGD     |
| 15 | TWH IB CASH USD         | savings account | TWH   | IB CASH          | USD      | TWH IB USD         |                     |
| 16 | TWH LC CASH USD         | savings account | TWH   | LC CASH          | USD      | LC CASH USD        | deprecated 2026+    |
| 17 | TWH CPF MS SGD          | retirement      | TWH   | CPF MS           | SGD      | CPF MA             |                     |
| 18 | TWH COINBASE USD        | savings account | TWH   | COINBASE         | USD      | TWH USD Coinbase   | deprecated 2026+    |
| 19 | TWH CDP SGD             | investment      | TWH   | CDP              | SGD      | CDP POSITION SGD   |                     |
| 20 | TWH IB POSITION USD     | investment      | TWH   | IB POSITION      | USD      | IB POSITION USD    |                     |
| 21 | TWH LC POSITION USD     | investment      | TWH   | LC POSITION      | USD      | LC NOTES USD       |                     |
| 22 | TWH SILVER BULLION USD  | investment      | TWH   | SILVER BULLION   | USD      | Silver Bullions    |                     |
| 23 | TWH SEED USD            | investment      | TWH   | SEED             | USD      | SeedInvest         |                     |
| 24 | TWH IB IRA USD          | retirement      | TWH   | IB IRA           | USD      | IB IRA USD         |                     |
| 25 | TWH CPF OA SGD          | retirement      | TWH   | CPF OA           | SGD      | CPF OA             |                     |
| 26 | TWH CPF SA SGD          | retirement      | TWH   | CPF SA           | SGD      | CPF SA             |                     |
| 27 | TWH 30 CC HASHEMIS SGD  | other credit    | TWH   | 30 CC HASHEMIS   | SGD      | 30 CC Hashemis     |                     |
| 28 | TWH IRS USD             | other credit    | TWH   | IRS              | USD      | IRS                |                     |

### Asset type classification summary

| id | type            | count | balance sheet section   | notes                                          |
| -- | --------------- | ----- | ----------------------- | ---------------------------------------------- |
| 01 | wallet cash     | 6     | cash and bank accounts  | physical cash, stored value, e-money wallets   |
| 02 | bank account    | 3     | cash and bank accounts  | COM UOB and HELVA UOB deprecated               |
| 03 | credit card     | 3     | credit                  | all have stm account (statement digital twin)  |
| 04 | savings account | 1     | cash and bank accounts  | IB CASH; LC CASH and COINBASE deprecated 2026+  |
| 05 | investment      | 5     | liquid investments      | position accounts only                         |
| 06 | retirement      | 4     | illiquid and retirement | IB IRA, CPF OA, CPF SA, CPF MS                 |
| 07 | other credit    | 2     | credit                  | WPC deprecated; TWH 30 CC Hashemis, TWH IRS    |

### Statement digital twin accounts

Six accounts have a `stm account` value, meaning they are processed through `statements.db` and appear in the `stm_txns` region of the financial statements workbook.

| id | account_id        | stm account         | type        |
| -- | ----------------- | ------------------- | ----------- |
| 01 | TWH DBS MULTI SGD | TWH DBS Multi SGD   | bank account |
| 02 | TWH CITI USD      | TWH CITI            | bank account |
| 03 | TWH BOA VISA USD  | TWH Visa USD        | credit card  |
| 04 | TWH DBS VISA SGD  | TWH DBS Visa SGD    | credit card  |
| 05 | TWH UOB ONE SGD   | TWH UOB One SGD     | credit card  |

The requirements prompt identifies four POC bank accounts in the statement digital twin path. The accounts table shows five accounts with `stm account` values — the four POC bank accounts plus TWH DBS VISA SGD. COM UOB SGD had a `stm account` value in the legacy pipeline but is excluded as a deprecated common-budget account.

## End-to-end translation to new model

### Expense category translation

`fin_stm_category` labels translate to `gl_code` by converting to lowercase snake_case. The non-trivial label changes are: `clothing personal items` → `clothing`, `healthcare OOP` → `healthcare_oop`, `misc discretionary` → `discretionary_misc`, `non alcoholic drinks` → `non_alcoholic_drinks`, `Singtel internet` → `singtel_internet`, `PUB water/gas` → `pub_water_gas`, `IT software` → `it_software`, `IT hardware` → `it_hardware`.

The `category_group_key` is assigned by group as follows.

**rental_expenses (1):** rental

**cole_expenses (12):** food, transport, healthcare_oop, insurance, mobile, clothing, post, singtel_internet, pub_water_gas, electricity, sundries, maintenance

**discretionary_expenses (15):** fitness, non_alcoholic_drinks, alcohol, socializing, it_software, it_hardware, books, travel, higher_education, projects, discretionary_misc, pets_and_plants, durables, cleaning_service, family_gifts

### Account type name alignment

All seven account type names in the legacy `accounts` region (`wallet cash`, `bank account`, `credit card`, `savings account`, `investment`, `retirement`, `other credit`) are identical to the new model vocabulary defined in `docs/requirements/account-classification.md`. No renaming is required.

### Legacy budget group retirement

The `fa_budget` field (`01 TWH personal`, `02 household`, `05 TWH taxes`, `06 external`) is a legacy grouping from the two-stage pipeline. In the new model this grouping is replaced entirely by `category_group_key`, which is derived from the COLE flag and `fin_stm_category` as described above. The `fa_budget` field does not carry forward as a data model field in the new implementation.

## Gap analysis

### GL codes with no fin_stm_category mapping

The following `fa_category` values appear in `cat_map` but have no matching row in `fin_exp_cat_map`:

| id | fa_category        | source HB categories                        | disposition                                    | decision |
| -- | ------------------ | ------------------------------------------- | ---------------------------------------------- | -------- |
| 01 | 02 income tax SGP  | Taxes and Fines (income, other, gov subsidy) | Income-side; handled in income category model |  drop    |
| 02 | 09 discretionary   | multiple HB categories                      | Caught by misc_discretionary in new model      | resolved with `TWH - Personal` |
| 03 | 11 sexual health   | Health and Wellness - sexual health         | Legacy label; aggregates to misc_discretionary | exist for `TWH - Personal` |
| 04 | 13 project         | Project - HDB2020, move 30 CC               | Deprecated — common budget only; no longer produced after budget retirement | deprecated with common budget |

Items 01 through 04 have a clear disposition and do not represent unresolved gaps. The income tax GL code routes through the income category model, not the expense category model. Legacy discretionary codes (`09 disc`, `11`, `13`) are absorbed into `discretionary_misc` via the `misc discretionary` catch-all rule in `fin_exp_cat_map`.

### cat_map rows with empty fa_category and fa_subcategory

One row pattern exists in `Household/Sundries` where both `fa_category` and `fa_subcategory` are empty. This appears to be an unmapped or stale mapping row. All other Household/Sundries rows correctly map to `08 sundries`. The new implementation should raise a validation error only if an unmapped category appears on transactions within the current or prior in-scope year. Empty mapping rows tied to the deprecated common or helva budget centers are out of scope and do not trigger an exception.

### COM UOB SGD and TWH HELVA UOB SGD scope

`COM UOB SGD` and `TWH HELVA UOB SGD` are both owned by the common and helva budget centers respectively, which are deprecated. Neither account is in scope for the new model. They should be excluded from the account registry implementation.

### WPC POSITION SGD scope

`WPC POSITION SGD` is deprecated. It should be excluded from the account registry implementation.

### CPF MS (Medisave) type classification

`TWH CPF MS SGD` was classified as `savings account` in the legacy accounts table. It has hybrid characteristics — illiquid like a retirement account but usable for medical expense payments. It is reclassified to `retirement` in the new model for consistency with the other CPF accounts.