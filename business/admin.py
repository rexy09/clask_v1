from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Customer)
admin.site.register(Expense)
admin.site.register(Payroll)
admin.site.register(Takehome)
admin.site.register(Interest)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderList)
admin.site.register(LocalPurchaseOrder)
admin.site.register(LocalPurchaseOrderList)

admin.site.register(SavingAccount)

@admin.register(Sale)
class SaleModelAdmin(admin.ModelAdmin):
    list_display = ('pk','branch','inventory','customer','user','quantity','total','amount_paid','price','profit','order_no','status','created_at')
    list_display_links = ['pk','branch']
    list_filter = ('created_at','branch')
    # readonly_fields = ('',)
    search_fields = ('order_no',)
    empty_value_display = '-empty-'
    ordering = ('-pk',)
    
admin.site.register(FixedAsset)
admin.site.register(FixedAssetCost)
admin.site.register(Total)

admin.site.register(PurchaseOrderCheck)
admin.site.register(PurchaseOrderApprove)
admin.site.register(PurchaseOrderAuthorize)

admin.site.register(LocalPurchaseOrderCheck)
admin.site.register(LocalPurchaseOrderApprove)
admin.site.register(LocalPurchaseOrderAuthorize)

admin.site.register(AccountsCurrentAsset)
admin.site.register(AccountsFixedAsset)

admin.site.register(Transaction)
admin.site.register(Loan)

@admin.register(CheckAccount)
class CheckAccountAdmin(admin.ModelAdmin):
    list_display = ('pk','business','employee','description','debit','credit','balance','created_at')
    list_display_links = ['pk','business']
    list_filter = ('created_at','business')
    readonly_fields = ('business','debit','credit','balance','employee')
    search_fields = ('pk','description')
    empty_value_display = '-empty-'
    ordering = ('-pk',)


admin.site.register(Tax)