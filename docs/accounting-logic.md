# Accounting logic

- [Related documents](#related-documents)
- [Personal expenses](#personal-expenses)
- [Personal Income](#personal-income)
- [Investment](#investment)
- [Mark-to-market (M2M)](#mark-to-market-m2m)
- [Forex](#forex)
	- [M2M forex on balances](#m2m-forex-on-balances)
	- [Forex on transactions](#forex-on-transactions)
- [Unique transaction and de-duplication logic](#unique-transaction-and-de-duplication-logic)
- [Reconciliation](#reconciliation)
	- [Reconciliation date](#reconciliation-date)
	- [Reconciliation methods](#reconciliation-methods)
	- [Reconciliation methods by account type](#reconciliation-methods-by-account-type)

Custom accounting logic guides how expenses and income are categorized, tracked, and reported in the home budget system. It defines the rules and principles for recording financial transactions, ensuring consistency and accuracy in financial reporting.

## Related documents

- [Accounts Reconcile](../reference/hb-reconcile/docs/reconcile.md): defines the reconciliation methods for bank and credit card accounts applied to the hb-reconcile local app.

## Personal expenses

For example, the use of "TWH - Personal" as a cost center

- this account balance closes to zero at the end of each month. it is the consolidated cost center for all personal expenses. Actual debits and credits to real wallets and accounts (payment method) are relfected as transfers into or out of this cost center.  So when you book an expense, you need to create two transactions: 

1. transfer from the real wallet ie "Cash TWH SGD" -> "TWH - Personal"
2. the actual expense booked in "TWH - Personal". This way you can easily track all personal expenses by looking at the transactions in TWH - Personal.

## Personal Income

All personal income is booked from the account "TWH DBS Multi SGD", and any additional miscellaneous income into other accounts such as cash or rebates on credit cards are booked in the same double-entry way with the transfer into "TWH DBS Multi SGD". This way you can easily track all personal income by looking at the transactions in TWH DBS Multi SGD.

## Investment

investment expenses are treated differently.  Investment do not track expenses and income separately, but rather net PL and it is classified into M2M for capital gains, Dividend, Interest and Profit and Loss for all other net income.  You can inspect the existing investment accounts such as the two IBA accounts for positions "IB POSITION USD" and cash "TWH IB USD". 

## Mark-to-market (M2M)

Mark-to-market (M2M) is an accounting method for valuing an assets or liability. It is based on using the value based on its market price at the reference date, usually the end of the accounting period. M2M profit and losses are only accounting adjustments to reflect the change in value of an asset or liability, and do not represent actual cash inflows or outflows until the asset is sold or the liability is settled. M2M adjustments are used to provide a more accurate picture of the financial position of an individual or business, especially for assets that can fluctuate in value such as investments. 

M2M gains/loss can be applied indivisibly to an entire account or position, such as a real estate valuation, or using unit price * quantity.

**indivisible M2M: Example real estate**: 

previous valuation on 2018-05-15 = $520,000
current valuation on 2026-02-28 = $870,000

M2M (gain) = $870,000 - $520,000 = $350,000

real estate ending balance = prior balance + M2M = $520,000 + $350,000 = $870,000

**unit price M2M: Example APPL stock**: 

previous market price end of previous period 2026-01-30 = $259.48
closing market price at end of current period 2026-02-27 = $264.18
number of shares = 400

M2M (gain) per share = ($264.18 - $259.48) = $4.70
M2M (gain) total = $4.70 * 400 shares = $1,880

closing balance = number of shares * closing price = 400 shares * $264.18 = $105,672
closing balance = number of shares * opening price + M2M per share * number of shares = 400 shares * $259.48 + $4.70 * 400 shares = $103,792 + $1,880 = $105,672

**unit price M2M with sale/purchase: Example USO ETF**: 

sales and purchases are considered transfers and do not affect net worth, while the M2M gain/loss is the adjustment to reflect the change in value of the position, so they are accounted for separately.

opening position 2026-02-01 = 1,000 shares @ $72.00 = $72,000
purchase during period = +200 shares @ $74.00 = $14,800 (transfer)
sale during period = -300 shares @ $75.00 = $22,500 (transfer)
closing market price 2026-02-27 = $73.50

FIFO on sale = 300 shares from opening lot @ $72.00
realized gain on sale = 300 * ($75.00 - $72.00) = $900

closing shares = 700 shares @ $72.00 + 200 shares @ $74.00 = 900 shares
unrealized M2M = 700 * ($73.50 - $72.00) + 200 * ($73.50 - $74.00) = $1,050 - $100 = $950

closing balance = 900 * $73.50 = $66,150
closing balance = opening balance + purchases - sales proceeds + realized gain + unrealized M2M = $72,000 + $14,800 - $22,500 + $900 + $950 = $66,150

## Forex

Forex effects are treated as a separate expense. There are two types of forex expenses

1. M2M forex on balances
2. Forex on transactions

### M2M forex on balances

M2M forex on balance is the unrealized gain or loss on the existing balance of an account due to changes in exchange rates. It is calculated as the difference between the value of the balance at the end of the period and the value of the balance at the beginning of the period, using the exchange rates at those respective times.

>M2M forex on balances = currency balance * (rate(end of period) - rate(beginning of period))

>transactions in currency * rate(beg of period) + M2M forex on balances = currency balance (end of period) * rate(end of period) - currency balance (beg of period) * rate(beg of period)

### Forex on transactions

An additional forex expense is booked to account for the delayed effect of credit card Visa forex processing fees, using the HB expense category "Professional Services:Currency Conversion".

1. Book the expense into personal cost center using the market exchange rate into SGD
2. Create the transfer from the real wallet to the cost center using the actual posted statement charge in SGD.
3. Create a reconciliation entry to mark the difference between the actual statement charge and the booked charge using spot exchange rate, with the payee following the Payee as the expense and category "Professional Services:Currency Conversion". This way you can easily track all forex expenses by looking at the transactions in TWH - Personal with category "Professional Services:Currency Conversion".

## Unique transaction and de-duplication logic

Transaction uniqueness is determined by a combination of the following attributes:

unique combination: account, transaction date, amount, description

This definition is sufficient to address any potential duplicates in the system, as it is highly unlikely for two distinct transactions to share the same account, date, amount, and description. 

In the rare exception when two transactions share the same account, date, amount, and description from the statement source, then when importing these into the system, either to the statement digital twin, or in the HomeBudget database, simply append a sequential id `-01, -02, etc..` in the description field.

## Accounting periods

Accounting periods are defined by calendar month, with beginning of the month the first day of calendar month, and end of month the last calendar day of the month

## Reconciliation

Reconciliation is the process of ensuring that the financial records in the HomeBudget system accurately reflect the actual financial transactions and balances. This involves comparing the recorded transactions and balances against external sources such as bank statements, credit card statements, and other financial documents to identify any discrepancies or gaps. The reconciliation methods differ by the available data source and account type.  

The simplest reconciliation method is at the account level to compare the ledger ending balance for the period against the statement ending balance for the same period, and then apply an adjustment transaction to "reconcile" or force the two to match. This is the method applied for physical wallet cash since there is no other practical means to trace back and close the gap.

### Reconciliation date

A reconciliation date can be at any day in the month. For reconciliation of bank statements, there will be three groups of transactions. For the pending transactions that are before reconciliation date, treat them as occuring after the reconcilaion date, and add a note in the description field of the actual transaction date "13 Mar", "25 Jan", etc... later after two reconcilation periods have passed, the dates for these transactions can be updated to the actual transaction date. 

| id | category  | statement | homebudget | date    | action                                        |
| -- | --------- | --------- | ---------- | ------- | --------------------------------------------- |
| 01 | captured  | X         | X          | before  | reconcile HB amount to match statement        |
| 02 | pending   |           | X          | before  | move txns to after the reconciliation date    |  
| 03 | forecast  |           | X          | after   | leave as-is, not in scope for reconciliation  |  

### Reconciliation methods

**Account level reconciliation with adjustment transaction example**

ledger beginning balance: $1240
ledger sum of transactions: -$295
ledger ending balance: $945
cash count: $922
reconciliation gap: $23

closing balance = cash count
closing balance = opening balance + sum of transactions + reconciliation adjustment
closing balance = $1240 - $295 - $23 = $922

**Transaction level reconciliation**

The reconciliation method for bank and credit accounts is more complex and involves tracing back the transactions to identify the source of the gap, which can be due to missing transactions, mis-categorized transactions, or errors in the recorded amounts. The reconciliation process for bank and credit accounts is an iterative process of gap detection and closure, where the goal is to identify and explain any gaps between the ledger balance and the statement balance, and then apply adjustments or corrections to close those gaps.

The transaction level reconciliation recognizes the statements as the source-of-truth, and applies adjustments to the ledger either with additions, removals or updates to transactions to close the gap. A core logic of the transaction level reconciliation is to identify the unique transactions that can be matched between the ledger and the statement, and then focus on the unmatched transactions to identify the source of the gap. The unique transaction logic is based on a combination of transaction date, amount, and description, with some tolerance for minor discrepancies in amounts or dates.

### Reconciliation methods by account type

- **physical wallet cash notes `TWH Cash SGD`**: reconciled with a physical cash count, plus the HB digital twin ledger. Cash transactions are captured through the retained Google Form -> Google Sheets raw source and ingested via the cash-expense adapter.
- **high volume bank accounts and credit cards:** reconciled with downloaded bank statements on a transaction level, usually in CSV/Excel format. These files are 01) ingested into a SQLite database as the statement digital twin, and then 02) reconciled with HomeBudget account ledgers. There are reconciliation process at both steps 01 and 02. For details on step 02) see `Accounts Reconcile` doc.
- **low volume bank accounts:** directly reconciled with home budget ledger without the intermediate step of the statement digital twin, using the same downloaded bank statements. The reconciliation process is similar to step 02 above.
- **digital wallets (ie Amazon wallet):** record current balance from login to account, and reconcile with the HB ledger. if there is a gap then user investigates and creates manual transactions to close the gap. since there is no statement download, there is no statement digital twin or reconciliation process 01.
- **investment account IBKR IBA:** reconciled with downloaded statements from IBKR, then parsed and processed using app-native adapters (legacy interim solution used custom workbook logic) to classify transactions into capital gains, dividends, interest, and mark-to-market (M2M) forex, net deposit/withdrawals, which are only from the IBKR cash account, and net trades which are booked as transfers between the IBKR cash and position accounts. The balance equation verified with the statement ending balance for both cash and position (reconciled). Then transactions are booked into HB ledger.
- **investment account IBKR IRA:** simpler process than IBKR IBA since there are no cash transactions, only position with capital gains. All income is treated as capital gains due to the illiquid nature of the account, even though technically it is a mix of interest + capital gains + etc.. Reconcile process is to downloaded statements from IBKR and read the ending balance, then create a reconcile capital gain/loss to close the balance equation. The capital gain/loss is booked as income into HB ledger.
- **investment account CPF:** fixed recurring contributions as transfers are already booked into HB ledger, so the reconciliation process is to verify the ending balance with the statement reflected online account.  There are no downloaded statements except annually where annual interest income is recorded.  Other transactions for CPF Medisave do show up and should be reconciled in a similar way as the digital wallet, where the balance is recorded and if there is a gap then user investigates and creates manual transactions to close the gap. Legacy interim solution used a helper worksheet to break down CPF contributions and link the contribution logic to earned salary; this is being replaced by app-native calculation logic in the CPF adapter module.
