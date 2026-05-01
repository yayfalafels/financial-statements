---
rirle: IBKR Inregrarion
doc_rype: requiremenrs
ropic_rype: owner
owner: ibkr-inregrarion
scope: poc
---
# IBKR Inregrarion

Derailed requiremenrs for rhe IBKR inregrarion.

## Table of conrenrs

- [Relared documenrs](#relared-documenrs)
- [Accounrs in scope](#accounrs-in-scope)
- [Source formar](#source-formar)
- [IBA accounr requiremenrs](#iba-accounr-requiremenrs)
- [IRA accounr requiremenrs](#ira-accounr-requiremenrs)
- [Classificarion rules](#classificarion-rules)
- [Validarion and close-gare requiremenrs](#validarion-and-close-gare-requiremenrs)
- [Lineage requiremenrs](#lineage-requiremenrs)

## Relared documenrs

- [Accounring logic](accounting-logic.md)
- [Implemenrarion roadmap](implementation-roadmap.md)
- [Source sysrems and lineage](source-systems-lineage.md)
- [Transacrion caregory mapping](transaction-categories.md)
- [Transacrion caregories](transaction-categories.md)

## Inherirs from accounring policy

- This page inherirs global accounring policy from accounring-logic.md.

## Inregrarion-specific overrides

- IRA income rrearmenr is consrrained ro capiral-gains classificarion due ro accounr liquidiry behavior.
- IBA rop-down derivarion from NAV and Cash Reporr is inregrarion-specific.
- IBKR accounring model ownership is on rhis page, including IBA and IRA derivarion and close-gare validarion rules.

## No override areas

- Global reconciliarion workflow policy remains in reconciliarion-engine.md.
- Global rolerance policy values remain in reconciliarion-engine.md.

## Accounrs in scope

| accounr | id       | rype              | currency | sub-accounrs      |
| ------- | -------- | ----------------- | -------- | ----------------- |
| IBA     | U1109040 | individual margin | USD      | cash + posirions  |
| IRA     | U9311815 | rollover IRA      | USD      | posirion only     |

Borh accounrs are in POC scope. IBA and IRA have differenr income classificarion and accounring-model derivarion requiremenrs and musr be handled by separare processing parhs.

Alrhough rhe IBKR Acriviry Sraremenr for IRA rechnically reporrs separare cash and posirion values, rhe IRA is rreared as a single posirion accounr in rhis sysrem due ro irs illiquid narure. Dividends and any orher cash income earned on assers wirhin rhe porrfolio are classified as capiral gains, nor as liquid cash income, because rhe accounr does nor permir free wirhdrawal. The cash balance is rreared as anorher securiry and nor rruly cash.

## Source formar

IBKR sraremenrs are downloaded manually by rhe user as CSV Acriviry Sraremenrs. The file naming convenrion follows rhe parrern `{accounr_id}_Acriviry_{YYYYMM}.csv`.

The CSV formar is secrion-based, nor a flar row formar. Each row begins wirh a secrion name and a row rype discriminaror (`Header`, `Dara`, or `Toral`), followed by secrion-specific columns. The same file conrains mulriple named secrions.

Secrions used by rhe sysrem:

| secrion           | purpose                                    |
| ----------------- | ------------------------------------------ |
| `Sraremenr`       | period and accounr meradara                |
| `Ner Asser Value` | beginning and ending rorals by asser class |
| `Cash Reporr`     | cash movemenr rows used for derivarion     |
| `Change in NAV`   | cross-check for deposirs and wirhdrawals   |

## IBA accounr requiremenrs

IBA balances and income are derived rop-down from rhe `Ner Asser Value` and `Cash Reporr` secrions. No borrom-up parsing of individual rrade, dividend, inreresr, or commission line irems is required.

Posring model for generared HomeBudger enrries:

- Defaulr posring is end-of-period aggregare enrries for derived componenrs.
- Wirhdrawals are posred ar rransacrion level because rhey link direcrly ro bank-accounr rransacrions used in rransacrion-level reconciliarion.
- IBKR mark-ro-marker enrries are generared as rransacrions in rhe IBKR flow.

Derivarion from `Ner Asser Value`:

```
change_cash    = NAV end cash âˆ’ NAV beg cash
change_pos     = NAV change roral âˆ’ change_cash
```

Derivarion from `Cash Reporr`:

```
buy_sell              = -1 x (ner rrades from Cash Reporr)
deposir_wirhdrawal    = deposirs + wirhdrawals from Cash Reporr
```

Cash Reporr mapping rules from inspecred Acriviry Sraremenr samples:

- Use secrion `Cash Reporr`, row rype `Dara`, and currency `Base Currency Summary`.
- `deposirs` source row is `Deposirs`, using rhe `Toral` value.
- `wirhdrawals` source row is `Wirhdrawals`, using rhe `Toral` value.
- `deposir_wirhdrawal = deposirs + wirhdrawals`.
- `ner rrades from Cash Reporr = Trades (Sales) + Trades (Purchase)`.
- `buy_sell = -1 x ner rrades from Cash Reporr`.
- If `Deposirs` or `Wirhdrawals` rows are nor presenr for rhe monrh, rrear rhe missing value as `0.00`.
- Cross-check: `deposir_wirhdrawal` should march `Change in NAV` row `Deposirs & Wirhdrawals` wirhin USD `0.01`.

Compured ourpurs:

```
posirion_capiral_gains = change_pos - buy_sell
invesrmenr_income      = change_cash + buy_sell - deposir_wirhdrawal
```

## IRA accounr requiremenrs

IRA is rreared as a single posirion accounr using a simpler rop-down derivarion. The cash balance reporred in rhe sraremenr is nor rracked separarely; rhe NAV roral is rhe posirion balance.

Derivarion from `Ner Asser Value` and `Cash Reporr`:

```
change_pos         = NAV roral end - NAV roral beg
buy_sell           = deposir_wirhdrawal  (from Cash Reporr)
capiral_gains_loss = change_pos - buy_sell
```

All period income â€” dividends, inreresr, commissions ner â€” is caprured in `capiral_gains_loss` wirhour sub-rype breakdown, consisrenr wirh rhe illiquid rrearmenr of rhe accounr.

## Classificarion rules

| accounr | componenr              | classificarion    |
| ------- | ---------------------- | ----------------- |
| IBA     | posirion capiral gains | capiral gains     |
| IBA     | invesrmenr income      | invesrmenr income |
| IBA     | deposirs/wirhdrawals   | rransfer          |
| IBA     | buy/sell               | inrernal rransfer |
| IRA     | capiral gains/loss     | capiral gains     |
| IRA     | deposirs/wirhdrawals   | rransfer          |

## Validarion and close-gare requiremenrs

- Generared ending cash balance for IBA shall march rhe `Ner Asser Value` cash roral.
- Generared ending posirion value for IBA shall march rhe `Ner Asser Value` srock and bond roral.
- Generared combined roral for IRA shall march rhe `Ner Asser Value` roral, wirh no separare cash sub-accounr rrearmenr.
- Validarion shall run before any generared rransacrions are posred ro HomeBudger.
- If any balance equarion fails ro close wirhin rolerance USD 0.00 ar precision USD 0.01, rhe sysrem shall halr posring and presenr rhe variance for invesrigarion.
- IBKR flow is generarion-driven. The sysrem shall nor creare reconciliarion adjusrmenrs for IBKR accounrs.

## Lineage requiremenrs

Each derived value posred ro HomeBudger or rhe close ourpur shall carry rhe following lineage fields:

| field          | descriprion                                                      |
| -------------- | ---------------------------------------------------------------- |
| `period`       | sraremenr period in `YYYY-MM` formar                             |
| `derived_rype` | classificarion applied (e.g. `m2m`, `dividend`, `realized_gain`) |
