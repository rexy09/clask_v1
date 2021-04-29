from django.urls import path
from . import views
from . import reports
from . import pdfs
from . import excels

app_name = "business"

urlpatterns = [
    path("<int:id>/profile/", views.business_profile, name="business_profile"),
    path("<int:id>/inventory/", views.inventory, name="inventory"),
    path("<int:id>/inventory/list/", views.inventory_list, name="inventory_list"),
    path("<int:id>/inventory/add/", views.add_inventory, name="add_inventory"),
    path("<int:id>/inventory/edit/", views.edit_inventory, name="edit_inventory"),
    path("<int:id>/expenses/", views.expenses, name="expenses"),
    path("<int:id>/products/", views.products, name="products"),
    path("<int:id>/product/add/", views.add_product, name="add_product"),
    path("<int:id>/product/edit/", views.edit_product, name="edit_product"),
    path("<int:id>/sales/", views.sales, name="sales"),
    path("<int:id>/sales/branch/", views.sales_branch, name="sales_branch"),
    path("<int:id>/sales/list/", views.sales_list, name="sales_list"),
    path("<int:id>/sales/add/", views.add_sale, name="add_sale"),
    path("<int:id>/sales/edit/", views.edit_sale, name="edit_sale"),
    path("<int:id>/sales/delete/", views.delete_sale, name="delete_sale"),
    path("<int:id>/inventory/stock/list/", views.stock_list, name="stock_list"),
    path("<int:id>/customer/list/", views.customer_list, name="customer_list"),
    path("<int:id>/customer/add/", views.add_customer, name="add_customer"),
    path("<int:id>/customer/edit/", views.edit_customer, name="edit_customer"),

    # AJAX URL
    path("get/inventory/", views.get_inventory, name="get_inventory"),

    
    path("<int:id>/fixed-assets-management/", views.fixed_asset_list, name="fixed-asset-home"),  
    path("<int:id>/expense/", views.expense_list, name="expense-list"),    
    path("<int:id>/expense/delete/<int:pk>/", views.expense_delete, name="expense-delete"),    
    path("<int:id>/payroll/delete/<int:pk>/", views.payroll_delete, name="payroll-delete"),    
    path("<int:id>/<int:pk>/edit/payroll/", views.payroll_update, name="payroll-update"),    
    path("<int:id>/<int:pk>/edit/expense/", views.expense_update, name="expense-update"),    
    path("<int:id>/<int:pk>/edit/fixed-asset/", views.fixed_asset_update, name="fixed-asset-update"),    
    path("<int:id>/takehome/", views.takehome, name="takehome"),

    # Reports  
    path("<int:id>/reports/", reports.reports, name="reports"),
    path("<int:id>/reports/sales/", reports.sales_time, name="sales_time"),
    path("<int:id>/<int:d>/reports/sales/report/", reports.sales_report, name="sales_report"),

    path("<int:id>/procurement/management/", views.procurement_management, name="procurement_management"),
    path("<int:id>/procurement/management/suppliers/", views.suppliers, name="suppliers"),
    path("<int:id>/procurement/management/suppliers/add/", views.add_supplier, name="add_supplier"),
    path("<int:id>/procurement/management/suppliers/edit/", views.edit_supplier, name="edit_supplier"),
    path("<int:id>/procurement/management/purchase/order/", views.purchase_order, name="purchase_order"),
    path("<int:id>/procurement/management/purchase/order/add/", views.add_purchase_order, name="add_purchase_order"),
    path("<int:id>/procurement/management/purchase/order/edit/", views.edit_purchase_order, name="edit_purchase_order"),
    path("<int:id>/procurement/management/purchase/order/view/", views.view_purchase_order, name="view_purchase_order"),
    path("<int:id>/procurement/management/purchase/local/order/", views.local_purchase_order, name="local_purchase_order"),
    path("<int:id>/procurement/management/purchase/local/order/add/", views.add_local_purchase_order, name="add_local_purchase_order"),
    path("<int:id>/procurement/management/purchase/local/order/edit/", views.edit_local_purchase_order, name="edit_local_purchase_order"),
    path("<int:id>/procurement/management/purchase/local/order/view/", views.view_local_purchase_order, name="view_local_purchase_order"),

    path("<int:id>/fixed-assets/", views.fixed_asset_list, name="fixed-asset-list"),       
    path("<int:id>/accounts/", views.accounts, name="accounts-home"),       
    path("<int:id>/bank-accounts/", views.bank_accounts, name="bank-accounts"),       
    path("<int:id>/assets/", views.assets, name="assets-home"),    
    path("<int:id>/fixed_assets/", views.fixed_assets, name="fixed_assets-list"),       
    path("<int:id>/<int:pk>/fixed_assets/edit/", views.fixed_assets_update, name="fixed_asset-update"),       
    path("<int:id>/current_assets/", views.current_assets, name="current_assets-list"),       
    path("<int:id>/<int:pk>/current_assets/edit/", views.current_assets_update, name="current_asset-update"),       
    path("<int:id>/liabilities/list/", views.liabilities_list, name="liabilities-list"),  
    path("<int:id>/<int:pk>/liabilities/edit/", views.liabilities_update, name="liabilities-update"),  

    path("<int:id>/procurement/management/purchase/order/check/", views.purchase_order_check_approve, name="purchase_order_check_approve"),
    path("<int:id>/procurement/management/purchase/order/check/decline/", views.purchase_order_check_decline, name="purchase_order_check_decline"),
    path("<int:id>/procurement/management/purchase/order/approve/", views.purchase_order_approve, name="purchase_order_approve"),
    path("<int:id>/procurement/management/purchase/order/approve/decline/", views.purchase_order_decline, name="purchase_order_decline"),
    path("<int:id>/procurement/management/purchase/order/authorize/", views.purchase_order_authorize_approve, name="purchase_order_authorize_approve"),
    path("<int:id>/procurement/management/purchase/order/authorize/decline/", views.purchase_order_authorize_decline, name="purchase_order_authorize_decline"),

    path("<int:id>/procurement/management/purchase/local/order/check/", views.local_purchase_order_check_approve, name="local_purchase_order_check_approve"),
    path("<int:id>/procurement/management/purchase/local/order/check/decline/", views.local_purchase_order_check_decline, name="local_purchase_order_check_decline"),
    path("<int:id>/procurement/management/purchase/local/order/approve/", views.local_purchase_order_approve, name="local_purchase_order_approve"),
    path("<int:id>/procurement/management/purchase/local/order/approve/decline/", views.local_purchase_order_decline, name="local_purchase_order_decline"),
    path("<int:id>/procurement/management/purchase/local/order/authorize/", views.local_purchase_order_authorize_approve, name="local_purchase_order_authorize_approve"),
    path("<int:id>/procurement/management/purchase/local/order/authorize/decline/", views.local_purchase_order_authorize_decline, name="local_purchase_order_authorize_decline"),

    path("<int:id>/procurement/management/purchase/order/pdf", pdfs.purchase_order_export_pdf, name="purchase_order_export_pdf"),
    path("<int:id>/procurement/management/purchase/local/order/pdf", pdfs.local_purchase_order_export_pdf, name="local_purchase_order_export_pdf"),

    path("<int:id>/reports/procurements/", reports.procurement_time, name="procurement_time"),
    path("<int:id>/<int:d>/reports/procurements/report/", reports.procurement_report, name="procurement_report"),

    path("<int:id>/reports/inventory/", reports.inventory_product, name="inventory_product"),
    path("<int:id>/reports/inventory/report/", reports.inventory_report, name="inventory_report"),

    path("<int:id>/customer/report/", reports.customer_report, name="customer-report"),    
    path("<int:id>/reports/payroll/", reports.payroll_time, name="payroll-time"),
    path("<int:id>/reports/opex/", reports.opex_time, name="opex-time"),
    path("<int:id>/<int:d>/payroll/report/", reports.payroll_report, name="payroll-report"),    
    path("<int:id>/<int:d>/opex/report/", reports.opex_report, name="opex-report"),    
    path("<int:id>/check/account/<str:trans>/", views.check_account, name="check-account"),    
    path("<int:id>/saving/account/<str:trans>/", views.saving_account, name="saving-account"),    
    path("<int:id>/interest/list/", views.interest_list, name="interest-list"),    
    path("<int:id>/interest/payment/<int:pk>/", views.interest_payment, name="interest-payment"),    

    path("<int:id>/financial/statements/", reports.financial_statements, name="financial_statements"),
    path("<int:id>/financial/statements/income/statement/time/", reports.income_statement_time, name="income_statement_time"),
    path("<int:id>/<int:d>/financial/statements/income/statement/", reports.income_statement, name="income_statement"),
    path("<int:id>/financial/statements/balance-sheet/", reports.balance_sheet, name="balance-sheet"),

    path("<int:id>/cashbook/time/", reports.cashflow_time, name="cashflow_time"),
    path("<int:id>/cashbook/", reports.cashflow, name="cashflow"),

    path("<int:id>/taxes/", views.taxes, name="taxes"),   
    path("<int:id>/pay/tax/", views.pay_tax, name="pay_tax"),   
    path("<int:id>/loans/", views.loan_list, name="loan-list"),   
    path("<int:id>/trialbalance/", views.trial_balance, name="trial-balance"),   
    path("<int:id>/trialbalance/time/", reports.trial_balance_time, name="trial-balance-time"),   
    path("<int:id>/trialbalance/excel/", excels.trial_balance_export_excel, name="trial-balance-excel"),   
    path("<int:id>/trialbalance/pdf/", pdfs.trial_balance_export_pdf, name="trial-balance-pdf"),   
    path("<int:id>/balancesheet/pdf/", reports.balance_sheet_export_pdf, name="balance-sheet-pdf"),   
]

